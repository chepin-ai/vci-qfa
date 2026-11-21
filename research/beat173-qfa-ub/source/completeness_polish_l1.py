#!/usr/bin/env python3
"""Optimize the exact-completeness dual residual in the certificate's actual L1 norm."""
import datetime as dt
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from scipy.optimize import linprog

HERE = Path(__file__).resolve().parent
INPUT = Path('/mnt/agents/output/.scratch/beat172-qfa-replay-01/inputs')
sys.path.insert(0, str(INPUT))
from npa_twirl import TwirlNPA
from test_twirl import build_RAC4_1AB, make_chars_Z4cube
from facial_polish import load_system, stackvec, make_Utr


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    out = HERE / 'rac4-completeness-polish-l1-02.json'
    witness = HERE / 'rac4-completeness-polish-l1-02.npz'
    if out.exists() or witness.exists():
        raise RuntimeError('output generation exists')
    started = dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z'); t0 = time.time()
    letters, povm_of, words, gens, obj = build_RAC4_1AB()
    t = TwirlNPA(letters, povm_of, words, gens, obj)
    chars, names = make_chars_Z4cube(t); t.set_chars(chars, names); t.build(verbose=False)
    cv, Ss, F0s, sizes, St = load_system(t); StT = St.T.tocsr()
    old = np.load(INPUT / 'y_best.npz', allow_pickle=True)
    Ys = [np.array(y) for y in old['Ys']]
    Utr = make_Utr(t, F0s, sizes)
    dual0 = 0.0; pen = 0.0; min_eigs = []
    for Y, F0, ub in zip(Ys, F0s, Utr):
        lm = float(np.linalg.eigvalsh((Y + Y.conj().T) / 2).min()); min_eigs.append(lm)
        dual0 += float(np.real(np.trace(F0.conj().T @ Y))); pen += max(0.0, -lm) * ub
    r0 = cv + StT @ stackvec(Ys)
    em = np.load(HERE / 'rac4-completeness-equalities-01.npz', allow_pickle=True)
    E = sp.csr_matrix((em['data'], em['indices'], em['indptr']), shape=tuple(em['shape']))
    e0 = em['e0']; m, nv = E.shape
    ET = E.T.tocsr()
    # Variables are free multipliers nu and nonnegative absolute-residual bounds t.
    # -t <= r0 + E^T nu <= t. Objective is exactly e0.nu + ||r||_1 + constant.
    I = sp.eye(nv, format='csr')
    A = sp.vstack([sp.hstack([ET, -I]), sp.hstack([-ET, -I])], format='csr')
    b = np.concatenate([-r0, r0])
    c = np.concatenate([e0, np.ones(nv)])
    bounds = [(None, None)] * m + [(0, None)] * nv
    print('LP dimensions', A.shape, 'nnz', A.nnz, flush=True)
    sol = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs',
                  options={'presolve': True, 'dual_feasibility_tolerance': 1e-9,
                           'primal_feasibility_tolerance': 1e-9})
    if not sol.success:
        raise RuntimeError(f'L1 dual optimization failed: status={sol.status} message={sol.message}')
    nu = sol.x[:m]
    r1 = r0 + ET @ nu
    equality_dual = float(e0 @ nu); dual1 = dual0 + equality_dual
    rn = float(np.abs(r1).sum()); cert = dual1 + pen + rn
    np.savez(witness, nu=nu, r0=r0, r1=r1, Ys=np.array(Ys, dtype=object))
    doc = {
        'schema': 'BEAT173-QFA-POVM-COMPLETENESS-DUAL-L1-02',
        'started_utc': started, 'ended_utc': dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z'),
        'wall_seconds': time.time() - t0,
        'optimization': {'solver': 'scipy.optimize.linprog/HiGHS', 'status': int(sol.status),
                         'message': sol.message, 'variables': len(c), 'constraints': A.shape[0],
                         'objective_without_constant': float(sol.fun), 'nit': int(sol.nit)},
        'old_certificate': {'cert': dual0 + pen + float(np.abs(r0).sum()), 'dualobj': dual0,
                            'psd_penalty': pen, 'residual_l1': float(np.abs(r0).sum())},
        'new_certificate': {'cert': cert, 'dualobj': dual1, 'base_dualobj': dual0,
                            'equality_dualobj': equality_dual, 'psd_penalty': pen, 'residual_l1': rn,
                            'residual_l2': float(np.linalg.norm(r1)), 'residual_linf': float(np.abs(r1).max()),
                            'min_psd_eigenvalue': min(min_eigs)},
        'guards': {'known_quantum_lb': 0.75, 'previous_valid_ub': 0.7537703608,
                   'not_below_known_lb_1e-7': bool(cert >= 0.75 - 1e-7),
                   'improves_previous_ub': bool(cert < 0.7537703608),
                   'improves_lsqr_generation_01': bool(cert < 0.7533021836843592)},
        'verdict': ('PASS_L1_OPTIMIZED_NUMERIC_DUAL_UB__INDEPENDENT_REPLAY_REQUIRED' if cert >= 0.75 - 1e-7 and cert < 0.7533021836843592
                    else 'FAIL_CERT_BELOW_KNOWN_CONSTRUCTION__DEBUG_MODEL_OR_NUMERICS' if cert < 0.75 - 1e-7
                    else 'NO_ADDITIONAL_IMPROVEMENT'),
        'boundary': 'Fixed-Y convex L1 optimization with exact completeness multipliers. Floating-point bound only; not an exact 3/4 theorem.',
        'inputs': {'equality_matrix_sha256': sha(HERE/'rac4-completeness-equalities-01.npz'),
                   'old_witness_sha256': sha(INPUT/'y_best.npz')},
        'source_sha256': sha(Path(__file__).resolve()), 'artifact': witness.name,
    }
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    print('RESULT_JSON', out); print('RESULT_SHA256', sha(out))
    print('NEW_CERT', repr(cert), 'DUAL', repr(dual1), 'PEN', repr(pen), 'RNORM', repr(rn))
    print('VERDICT', doc['verdict'])
    return 0 if doc['verdict'].startswith('PASS_') else 2


if __name__ == '__main__':
    raise SystemExit(main())
