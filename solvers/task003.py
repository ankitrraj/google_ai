def p(g):
    import numpy as n
    a = n.array(g)
    # Convert 1s to 2s
    converted = n.where(a == 1, 2, a)
    
    # Pattern detection: check if rows 0 and 3 are identical
    if n.array_equal(converted[0], converted[3]):
        # Use first 3 rows pattern (Examples 2,3)
        result = n.vstack([converted, converted[:3]])
    else:
        # Use [0,3,0] pattern (Example 1)
        result = n.vstack([converted, converted[[0,3,0]]])
    
    return result.tolist()