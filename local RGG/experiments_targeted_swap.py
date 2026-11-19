"""Paired benchmark of a single reverse order with and without swap cleanup.

An optional raw shared-pruning checkpoint supplies previously measured forward
results. The two reverse variants always use the same freshly computed set and
distance matrix. Timing repeats reuse the same seed, not different orders.
"""

import argparse
import csv
import json
from pathlib import Path
import random
from statistics import median
from time import perf_counter

from experiments_final_entropy_collision import _prepare_graph
from functions.optimized_pruning import prune_resolving_set_optimized
from functions.targeted_swap_cleanup import targeted_swap_cleanup


def load_reference(path):
    if path is None:
        return {}
    graphs = {}
    with path.open(newline='', encoding='utf-8') as stream:
        for row in csv.DictReader(stream):
            if row['method'] in {'grid', 'circle', 'zoomed', 'reverse'}:
                key = (int(row['n']), float(row['radius']), int(row['repeat']))
                group = graphs.setdefault(key, {})
                if row['method'] in group:
                    raise ValueError(f'duplicate reference run for {key}')
                group[row['method']] = row
    return graphs


def benchmark(radii, *, repeats, n, seed, max_pairs, timing_repeats, reference=None):
    ref = load_reference(reference)
    rows = []
    for radius in radii:
        for i in range(repeats):
            point_seed = random.Random(seed + n * 1009 + i * 7919).randrange(2**32)
            order_seed = point_seed ^ int(round(radius * 1e9))
            prepared = _prepare_graph(n, radius, point_seed)
            graph, dist = prepared['converted'], prepared['dist_matrix']
            prep = prepared['shared_preprocessing_time_seconds']
            base_times, swap_times, combined_times = [], [], []
            expected = None
            for _ in range(timing_repeats):
                start = perf_counter()
                base = prune_resolving_set_optimized(graph, range(n), dist, seed=order_seed)
                middle = perf_counter()
                clean = targeted_swap_cleanup(graph, base, dist, max_pairs=max_pairs, seed=order_seed)
                end = perf_counter()
                base_times.append(prep + middle - start)
                swap_times.append(end - middle)
                combined_times.append(prep + end - start)
                outcome = (base, clean)
                if expected is not None and outcome != expected:
                    raise RuntimeError('seeded results changed between timing repeats')
                expected = outcome
            row = dict(radius=radius, cloud=i+1, density=prepared['summary']['edge_density'],
                       point_seed=point_seed, order_seed=order_seed, fingerprint=prepared['fingerprint'],
                       reverse_size=len(base), cleanup_size=len(clean.resolving_set),
                       reverse_seconds=median(base_times), cleanup_seconds=median(swap_times),
                       combined_seconds=median(combined_times), pairs_checked=clean.pairs_checked,
                       probes_saved=clean.swaps)
            if reference is not None:
                prior = ref.get((n, radius, i+1), {})
                if set(prior) != {'grid', 'circle', 'zoomed', 'reverse'} or any(
                    r['graph_fingerprint'] != row['fingerprint'] or
                    int(r['algorithm_seed']) != order_seed or r['valid'] != 'True' or
                    r['pruning_backend'] != 'shared-optimized' or r['timing'] != 'full'
                    for r in prior.values()
                ) or int(prior['reverse']['size']) != len(base):
                    raise ValueError(f'no matching reference for radius {radius}, cloud {i+1}')
                forward = [r for name, r in prior.items() if name != 'reverse']
                row['forward_methods'] = {r['method']: dict(probes=int(r['size']), seconds=float(r['seconds']))
                                          for r in forward}
                row['best_forward_size'] = min(int(r['size']) for r in forward)
                row['fastest_forward_seconds'] = min(float(r['seconds']) for r in forward)
            rows.append(row)
    return rows


def summarize(rows):
    summary = []
    for radius in sorted({row['radius'] for row in rows}):
        group = [row for row in rows if row['radius'] == radius]
        item = dict(radius=radius, cases=len(group), improved=sum(r['probes_saved'] > 0 for r in group),
                    median_saved=median(r['probes_saved'] for r in group),
                    median_added_ms=round(1000 * median(r['cleanup_seconds'] for r in group), 2))
        if 'best_forward_size' in group[0]:
            for label in ('reverse', 'cleanup'):
                item[f'median_{label}_gap'] = median(r[f'{label}_size'] - r['best_forward_size'] for r in group)
            item['matches_forward_size'] = sum(r['cleanup_size'] <= r['best_forward_size'] for r in group)
            item['faster_than_cached_forward'] = sum(r['combined_seconds'] < r['fastest_forward_seconds'] for r in group)
        summary.append(item)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--radii', type=float, nargs='+', default=[0.5, 0.6, 0.65, 0.9])
    parser.add_argument('--n', type=int, default=500)
    parser.add_argument('--repeats', type=int, default=5)
    parser.add_argument('--timing-repeats', type=int, default=3)
    parser.add_argument('--seed', type=int, default=20261026)
    parser.add_argument('--max-pairs', type=int, default=512)
    parser.add_argument('--reference', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if min(args.n, args.repeats, args.timing_repeats) < 1 or args.max_pairs < 0:
        parser.error('n and repeat counts must be positive and max-pairs nonnegative')
    rows = benchmark(args.radii, n=args.n, repeats=args.repeats, seed=args.seed,
                     max_pairs=args.max_pairs, timing_repeats=args.timing_repeats, reference=args.reference)
    summary = summarize(rows)
    print(json.dumps(summary, indent=2))
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(dict(settings=vars(args), summary=summary, runs=rows),
                                         indent=2, default=str) + '\n', encoding='utf-8')
