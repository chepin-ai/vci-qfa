#!/usr/bin/env python3
import datetime as dt
import hashlib
import json
import os
import platform
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
INPUT = Path('/mnt/agents/output/.scratch/beat172-qfa-replay-01/inputs')
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(INPUT))
from canonical_npa import CanonicalTwirlNPA
from test_twirl import build_RAC4_1AB, make_chars_Z4cube


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    iters = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    mode = sys.argv[2] if len(sys.argv) > 2 else 'quick'
    if mode not in ('quick', 'full'):
        raise ValueError('mode must be quick or full')
    if mode == 'quick' and iters > 2000:
        raise ValueError('quick mode is capped at 2000 iterations')
    out = HERE / f'rac4-canonical-{iters}.json'
    ckpt = HERE / f'rac4-canonical-{iters}.checkpoint.npz'
    if out.exists():
        raise RuntimeError(f'output generation exists: {out}')
    started = dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')
    t0 = time.time()
    letters, povm_of, words, gens, obj = build_RAC4_1AB()
    t = CanonicalTwirlNPA(letters, povm_of, words, gens, obj)
    # Known-answer normal-form controls on words longer than length two.
    def ix(letter):
        return letters.index(letter)
    a00 = ix(('A', 0, 0)); a01 = ix(('A', 0, 1)); a10 = ix(('A', 1, 0))
    b000 = ix(('B', 0, 0, 0)); b001 = ix(('B', 0, 0, 1))
    kats = {
        'cross_side_commutation': t.norm_class((a00, b000)) == t.norm_class((b000, a00)),
        'same_side_commutation_len3': t.norm_class((a00, a10, b000)) == t.norm_class((a10, a00, b000)),
        'idempotence_len3': t.norm_class((a00, a00, b000)) == t.norm_class((a00, b000)),
        'orthogonal_A_zero': t.norm_class((a00, a01, b000)) == 'Z',
        'orthogonal_B_zero': t.norm_class((a00, b000, b001)) == 'Z',
    }
    if not all(kats.values()):
        raise AssertionError(f'normal-form KAT failure: {kats}')
    chars, names = make_chars_Z4cube(t)
    t.set_chars(chars, names)
    t.build(verbose=True)
    result = t.solve_cg(mu=0.1, iters=iters, verbose=True, ckpt=str(ckpt), alpha=1.6)
    cert = float(result['cert'])
    cert_avg = result.get('cert_avg')
    candidates = {'terminal': cert}
    if cert_avg is not None:
        candidates['ergodic_average'] = float(cert_avg)
    best_name, best_cert = min(candidates.items(), key=lambda kv: kv[1])
    lb_ok = best_cert >= 0.75 - 1e-7
    old_ub = 0.7537703608
    doc = {
        'schema': 'BEAT173-QFA-CANONICAL-NPA-RUN-01',
        'started_utc': started,
        'ended_utc': dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z'),
        'wall_seconds': time.time() - t0,
        'mode': mode,
        'iterations_requested': iters,
        'known_answer_controls': kats,
        'structure': {
            'group_order': t.oG, 'basis_words': t.N, 'word_orbits': t.norb,
            'z_variables': t.nz, 'blocks': len(t.blocks),
            'block_sizes': sorted(b['size'] for b in t.blocks),
        },
        'result': {k: (float(v) if isinstance(v, (float, np.floating)) or (isinstance(v, (int, np.integer)) and k != 'z') else None)
                   for k, v in result.items() if k != 'z'},
        'certificate_candidates': candidates,
        'best_candidate': best_name,
        'best_cert': best_cert,
        'known_quantum_lower_bound': 0.75,
        'previous_valid_upper_bound': old_ub,
        'lower_bound_guard_pass': lb_ok,
        'not_worse_than_previous_bound': best_cert <= old_ub + 1e-10,
        'verdict': ('PASS_NUMERIC_DUAL_BOUND__EXACT_THEOREM_NOT_CLAIMED' if lb_ok and best_cert <= old_ub + 1e-10
                    else 'FAIL_CERT_BELOW_KNOWN_QUANTUM_CONSTRUCTION' if not lb_ok
                    else 'VALID_BUT_NOT_IMPROVED_OR_NOT_CONVERGED'),
        'boundary': 'Floating-point dual certificate only; no exact 3/4 theorem. Quick is not full. A certificate below the known construction is an implementation/model failure, not a refutation.',
        'input_sha256': {name: sha(INPUT / name) for name in ('npa_twirl.py', 'test_twirl.py')},
        'canonical_source_sha256': sha(HERE / 'canonical_npa.py'),
        'runner_source_sha256': sha(Path(__file__).resolve()),
        'checkpoint_path': ckpt.name,
        'checkpoint_sha256': sha(ckpt) if ckpt.exists() else None,
        'environment': {'python': sys.version.split()[0], 'numpy': np.__version__, 'platform': platform.platform()},
    }
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    print('RESULT_JSON', out)
    print('RESULT_SHA256', sha(out))
    print('VERDICT', doc['verdict'])
    print('BEST_CERT', repr(best_cert))
    return 0 if lb_ok else 2


if __name__ == '__main__':
    raise SystemExit(main())
