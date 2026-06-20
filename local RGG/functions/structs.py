def generate_rgg_with_grid(G, m, n):
    grid = {(r, c): [] for r in range(m) for c in range(n)}
    pos = {}

    for node in range(G.vcount()):
        coord = G.vs[node]["pos"]
        x, y = coord[0], coord[1]

        pos[node] = (x, y)

        col = min(int(x * n), n - 1)
        row = min(int(y * m), m - 1)
        grid[(row, col)].append(node)

    return grid