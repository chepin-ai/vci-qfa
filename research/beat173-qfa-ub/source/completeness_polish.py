#!/usr/bin/env python3
"""Add exact POVM completeness equalities to the frozen RAC4 1+AB dual certificate."""
import datetime as dt
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import lsqr

HERE = Path(__file__).resolve().parent
INPUT = Path('/mnt/agents/output/.scratch/beat172-qfa-replay-01/inputs')
sys.path.insert(0, str(INPUT))
from npa_twirl import TwirlNPA
from test_twirl import build_RAC4_1AB, make_chars_Z4cube
from facial_polish import load_system, stackvec, make_Utr


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalize_row(row):
    if not row:
        return None
    # Sign-normalize; equality rows and their negations are duplicates.
    first = min(row)
    if row[first] < 0:
        row = {k: -v for k, v in row.items()}
    scale = max(abs(v) for v in row.values())
    return tuple(sorted((k, float(v / scale)) for k, v in row.items() if abs(v) > 1e-14))


def classical_feasible_z(t):
    """Twirl the deterministic 5/8 strategy; independent of the equality matrix."""
    def letter_val(li):
        lt = t.letters[li]
        if lt[0] == 'A':
            _, x, m = lt
            return 1.0 if m == x // 4 else 0.0
        _, y, m, v = lt
        g = m if y == 0 else 0
        return 1.0 if v == g else 0.0
    wv = np.array([letter_val(li) for li in range(len(t.letters))])
    def word_val(wd):
        ans = 1.0
        for li in wd:
            ans *= wv[li]
        return ans
    zsym = np.zeros(t.nz)
    wvals = {wd: word_val(wd) for wd in t.W}
    reps = [int(x) for x in t.reps]
    for o in range(t.norb):
        for o2 in range(t.norb):
            for k in range(t.oG):
                wi = reps[o]; wj = int(t.gt[k, reps[o2]])
                zid = t.zid_of_class(t.class_key(wi, wj))
                if zid < 0:
                    continue
                value = sum(wvals[t.W[int(t.gt[gi, wi])]] * wvals[t.W[int(t.gt[gi, wj])]]
                            for gi in range(t.oG)) / t.oG
                zsym[zid] = value
    zsym[t.zI] = 1.0
    return zsym


def main():
    started = dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')
    t0 = time.time()
    out = HERE / 'rac4-completeness-polish-01.json'
    witness = HERE / 'rac4-completeness-polish-01.npz'
    matrix_path = HERE / 'rac4-completeness-equalities-01.npz'
    if out.exists() or witness.exists() or matrix_path.exists():
        raise RuntimeError('output generation exists')
    letters, povm_of, words, gens, obj = build_RAC4_1AB()
    t = TwirlNPA(letters, povm_of, words, gens, obj)
    chars, names = make_chars_Z4cube(t)
    t.set_chars(chars, names); t.build(verbose=True)
    cv, Ss, F0s, sizes, St = load_system(t)
    StT = St.T.tocsr(); nv = len(cv); old_nz = t.nz
    I = t.wpos[()]
    single = {w[0]: i for i, w in enumerate(t.W) if len(w) == 1}
    povms = {}
    for li, povm in povm_of.items():
        povms.setdefault(povm, []).append(li)
    raw_rows = []; unique = {}; duplicate_count = 0
    for povm, ls in sorted(povms.items()):
        ls = sorted(ls)
        for si in range(t.N):
            row = {}
            for li in ls:
                zid = t.zid_of_class(t.class_key(single[li], si))
                if zid >= 0:
                    row[zid] = row.get(zid, 0.0) - 1.0
            zid = t.zid_of_class(t.class_key(I, si))
            if zid >= 0:
                row[zid] = row.get(zid, 0.0) + 1.0
            norm = normalize_row(row)
            raw_rows.append((povm, si))
            if norm is None:
                duplicate_count += 1
            elif norm in unique:
                duplicate_count += 1
            else:
                unique[norm] = (povm, si)
    assert t.nz == old_nz, (t.nz, old_nz)
    keys = sorted(unique)
    rr = []; cc = []; vv = []; e0 = []
    for ri, key in enumerate(keys):
        const = 0.0
        for zid, value in key:
            if zid == t.zI:
                const += value
            else:
                vid = zid - int(zid > t.zI)
                rr.append(ri); cc.append(vid); vv.append(value)
        e0.append(const)
    E = sp.csr_matrix((vv, (rr, cc)), shape=(len(keys), nv))
    e0 = np.array(e0)
    zc = classical_feasible_z(t)
    zcn = np.delete(zc, t.zI)
    classical_res = E @ zcn + e0
    classical_obj = float(sum(t.c[z] * zc[z] for z in range(t.nz)))
    classical_kat = bool(np.max(np.abs(classical_res), initial=0.0) < 1e-10 and abs(classical_obj - 0.625) < 1e-12)
    nc = zcn.copy()
    target_row = int(np.argmax(np.asarray(np.abs(E).sum(axis=1)).ravel()))
    target_col = int(E[target_row].indices[0])
    nc[target_col] += 0.03125
    nc_res = E @ nc + e0
    negative_control_detected = bool(np.max(np.abs(nc_res)) > 1e-3)
    if not classical_kat or not negative_control_detected:
        raise AssertionError({'classical_kat': classical_kat, 'negative_control': negative_control_detected,
                              'classical_max_res': float(np.max(np.abs(classical_res))),
                              'classical_obj': classical_obj})
    old = np.load(INPUT / 'y_best.npz', allow_pickle=True)
    Ys = [np.array(y) for y in old['Ys']]
    Utr = make_Utr(t, F0s, sizes)
    dual0 = 0.0; pen = 0.0; min_eigs = []
    for Y, F0, ub in zip(Ys, F0s, Utr):
        H = (Y + Y.conj().T) / 2
        lm = float(np.linalg.eigvalsh(H).min()); min_eigs.append(lm)
        dual0 += float(np.real(np.trace(F0.conj().T @ Y)))
        pen += max(0.0, -lm) * ub
    r0 = cv + StT @ stackvec(Ys)
    cert0 = dual0 + pen + float(np.abs(r0).sum())
    print('equality system:', E.shape, 'nnz=', E.nnz, 'raw=', len(raw_rows), flush=True)
    print('old certificate:', cert0, 'dual=', dual0, 'pen=', pen, 'rnorm=', float(np.abs(r0).sum()), flush=True)
    fit = lsqr(E.T, -r0, atol=1e-12, btol=1e-12, iter_lim=4000)
    nu = fit[0]
    r1 = r0 + E.T @ nu
    equality_dual = float(e0 @ nu)
    dual1 = dual0 + equality_dual
    rnorm1 = float(np.abs(r1).sum())
    cert1 = dual1 + pen + rnorm1
    np.savez(matrix_path, data=E.data, indices=E.indices, indptr=E.indptr, shape=np.array(E.shape),
             e0=e0, row_keys=np.array(keys, dtype=object), zI=np.array(t.zI))
    np.savez(witness, nu=nu, r0=r0, r1=r1, Ys=np.array(Ys, dtype=object))
    doc = {
        'schema': 'BEAT173-QFA-POVM-COMPLETENESS-DUAL-01',
        'started_utc': started, 'ended_utc': dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z'),
        'wall_seconds': time.time() - t0,
        'model': 'RAC4 full d=4 EARAC, symmetry-twirled commuting NPA 1+AB plus exact POVM completeness',
        'structure': {'group_order': t.oG, 'basis_words': t.N, 'z_variables': t.nz,
                      'povms': len(povms), 'raw_completeness_equations': len(raw_rows),
                      'unique_nontrivial_equations': E.shape[0], 'duplicate_or_zero_equations': duplicate_count,
                      'nonidentity_variables': nv, 'equality_nnz': E.nnz},
        'known_answers': {'classical_5over8_feasible': classical_kat,
                          'classical_max_equality_residual': float(np.max(np.abs(classical_res), initial=0.0)),
                          'classical_objective': classical_obj,
                          'completeness_negative_control_detected': negative_control_detected,
                          'negative_control_max_residual': float(np.max(np.abs(nc_res)))},
        'old_certificate': {'cert': cert0, 'dualobj': dual0, 'psd_penalty': pen, 'residual_l1': float(np.abs(r0).sum())},
        'new_certificate': {'cert': cert1, 'dualobj': dual1, 'base_dualobj': dual0,
                            'equality_dualobj': equality_dual, 'psd_penalty': pen, 'residual_l1': rnorm1,
                            'residual_l2': float(np.linalg.norm(r1)), 'min_psd_eigenvalue': min(min_eigs)},
        'lsqr': {'iterations': int(fit[2]), 'istop': int(fit[1]), 'reported_residual': float(fit[3]),
                 'reported_normal_residual': float(fit[4]), 'condition_estimate': float(fit[6])},
        'guards': {'known_quantum_lb': 0.75, 'previous_valid_ub': 0.7537703608,
                   'not_below_known_lb_1e-7': bool(cert1 >= 0.75 - 1e-7),
                   'improves_previous_ub': bool(cert1 < 0.7537703608)},
        'verdict': ('PASS_IMPROVED_NUMERIC_DUAL_UB__INDEPENDENT_REPLAY_REQUIRED' if cert1 >= 0.75 - 1e-7 and cert1 < 0.7537703608
                    else 'FAIL_CERT_BELOW_KNOWN_CONSTRUCTION__DEBUG_MODEL_OR_NUMERICS' if cert1 < 0.75 - 1e-7
                    else 'NO_IMPROVEMENT'),
        'boundary': 'Exact completeness equalities, not penalty constraints. Floating-point certificate is not an exact 3/4 theorem. Independent second-entry replay is mandatory.',
        'artifacts': {'equality_matrix': matrix_path.name, 'witness': witness.name},
        'input_sha256': {name: sha(INPUT / name) for name in ('npa_twirl.py', 'test_twirl.py', 'facial_polish.py', 'y_best.npz')},
        'source_sha256': sha(Path(__file__).resolve()),
    }
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    print('RESULT_JSON', out)
    print('RESULT_SHA256', sha(out))
    print('NEW_CERT', repr(cert1), 'DUAL', repr(dual1), 'PEN', repr(pen), 'RNORM', repr(rnorm1))
    print('VERDICT', doc['verdict'])
    return 0 if doc['verdict'].startswith('PASS_') else 2


if __name__ == '__main__':
    raise SystemExit(main())
