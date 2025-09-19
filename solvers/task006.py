def p(g):
    import numpy as n
    a = n.array(g)
    h, w = a.shape
    # Find separator column consisting of all 5s
    sep_cols = [j for j in range(w) if n.all(a[:, j] == 5)]
    if not sep_cols:
        # Fallback: return zeros 3x3
        return n.zeros((3, 3), dtype=int).tolist()
    sep = sep_cols[0]

    left = a[:, :sep]
    right = a[:, sep + 1 :]

    # Use the nearest 3 columns on each side to form 3x3 blocks
    left3 = left[:, -3:]
    right3 = right[:, :3]

    mask = (left3 == 1) & (right3 == 1)
    out = n.where(mask, 2, 0)
    return out.tolist()