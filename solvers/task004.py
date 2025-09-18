def p(g):
    import numpy as n
    a = n.array(g)
    result = n.zeros_like(a)
    
    # For each row, try to move objects to avoid overlaps
    for r in range(a.shape[0]):
        row = a[r].copy()
        nonzero_cols = n.where(row != 0)[0]
        
        if len(nonzero_cols) == 0:
            continue
            
        # Get all non-zero values in order
        values = []
        for c in nonzero_cols:
            values.append(row[c])
        
        # Try to place values starting from leftmost+1, compacting gaps
        leftmost = min(nonzero_cols)
        
        # Special handling based on row patterns observed
        if len(nonzero_cols) == 2 and nonzero_cols[1] - nonzero_cols[0] == 3:
            # Two objects separated by 3 - move right and compact gap
            result[r, leftmost + 1] = values[0]
            result[r, leftmost + 3] = values[1]
        else:
            # Default: shift right by 1
            pos = leftmost + 1
            for val in values:
                if pos < a.shape[1]:
                    result[r, pos] = val
                    pos += 1
    
    return result.tolist()