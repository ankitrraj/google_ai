def p(g):
    import numpy as n
    a = n.array(g)
    result = a.copy()
    h, w = a.shape
    
    # Find objects and create 3x3 tiling patterns
    for color in range(1, 10):
        positions = n.where(a == color)
        if len(positions[0]) == 0:
            continue
            
        # Get bounding box
        min_r, max_r = min(positions[0]), max(positions[0])
        min_c, max_c = min(positions[1]), max(positions[1])
        
        # Create 3x3 pattern from the object
        pattern_3x3 = n.zeros((3, 3), dtype=int)
        
        # Fill the 3x3 pattern based on object shape
        if max_r - min_r == 0:  # 1-row object (horizontal)
            pattern_3x3[0, :] = color
            pattern_3x3[2, :] = color
            # Tile vertically every 4 rows
            for offset in range(4, h-min_r, 4):
                new_r = min_r + offset
                if new_r + 3 <= h:
                    result[new_r:new_r+3, min_c:min_c+3] = pattern_3x3
        elif max_c - min_c == 0:  # 1-column object (vertical)
            pattern_3x3[:, 0] = color
            pattern_3x3[:, 2] = color
            pattern_3x3[1, 1] = 0  # Keep center empty
            # Tile horizontally every 4 columns
            for offset in range(4, w-min_c, 4):
                new_c = min_c + offset
                if new_c + 3 <= w:
                    result[min_r:min_r+3, new_c:new_c+3] = pattern_3x3
    
    return result.tolist()