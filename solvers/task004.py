def p(g):
    import numpy as n
    a = n.array(g)
    result = n.zeros_like(a)
    h, w = a.shape
    # Shift all non-zero elements right by 1 column
    for r in range(h):
        for c in range(w-1):
            if a[r,c] != 0:
                result[r,c+1] = a[r,c]
    return result.tolist()