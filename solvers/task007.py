def p(g):
    import numpy as n
    a = n.array(g)
    h, w = a.shape
    # Collect unique non-zero colors in row-major order
    seq = []
    seen = set()
    for r in range(h):
        for c in range(w):
            v = a[r, c]
            if v != 0 and v not in seen:
                seen.add(v)
                seq.append(int(v))
    if not seq:
        return a.tolist()
    # Reduce to first 3 colors if more
    if len(seq) > 3:
        seq = seq[:3]
    k = len(seq)
    # Output is full square same size as input, filled by (r+c) mod k
    out = n.zeros((h, w), dtype=int)
    for r in range(h):
        for c in range(w):
            out[r, c] = seq[(r + c) % k]
    return out.tolist()