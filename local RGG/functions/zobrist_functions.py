import random
import numpy as np

def build_zobrist_tables(landmarks, dist_matrix, INF_CODE, bits=64):
    max_dist = INF_CODE
    rand = [
        [random.getrandbits(bits) for _ in range(max_dist+1)]
        for _ in range(len(landmarks))
    ]
    return rand

def compute_initial_hashes(n, landmarks, dist_matrix, rand, INF_CODE):
    hashes = [0] * n
    for v in range(n):
        h = 0
        for j, l in enumerate(landmarks):
            d = dist_matrix[v][l]
            code = int(d) if d < float('inf') else INF_CODE
            h ^= rand[j][code]
        hashes[v] = h
    return hashes

def try_remove_landmark(j, l, n, hashes, rand, dist_matrix, INF_CODE):
    adjusted = [0] * n
    for v in range(n):
        d = dist_matrix[v][l]
        code = int(d) if d < float('inf') else INF_CODE
        adjusted[v] = hashes[v] ^ rand[j][code]
    if len(set(adjusted)) == n:
        return adjusted
    return None

def prune_resolving_set_zobrist_fast(g, resolving_set, dist_matrix, bits=64):
    n = g.vcount()
    landmarks = list(resolving_set)
    if not landmarks:
        return set()
    max_d = 0
    for v in range(n):
        for l in landmarks:
            d = dist_matrix[v][l]
            if d < float('inf'):
                max_d = max(max_d, int(d))
    INF_CODE = max_d + 1

    rand = build_zobrist_tables(landmarks, dist_matrix, INF_CODE, bits=bits)
    hashes = compute_initial_hashes(n, landmarks, dist_matrix, rand, INF_CODE)

    pruned = set(landmarks)
    changed = True

    while changed:
        changed = False
        for j, l in enumerate(landmarks):
            if l not in pruned:
                continue

            adjusted = try_remove_landmark(j, l, n, hashes, rand, dist_matrix, INF_CODE)
            if adjusted is not None:
                pruned.remove(l)
                hashes = adjusted
                changed = True
                break

    return pruned