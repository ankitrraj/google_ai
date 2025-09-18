def p(g):
    import numpy as n
    a = n.array(g)
    result = a.copy()
    h, w = a.shape
    
    # Process each color separately
    for color in range(1, 10):
        positions = n.where(a == color)
        if len(positions[0]) == 0:
            continue
            
        # Get bounding box
        min_r, max_r = min(positions[0]), max(positions[0])
        min_c, max_c = min(positions[1]), max(positions[1])
        pattern_h = max_r - min_r + 1
        pattern_w = max_c - min_c + 1
        
        # Extract the original pattern
        pattern = a[min_r:max_r+1, min_c:max_c+1]
        
        # Expansion rules based on pattern size
        if pattern_h == 1 and pattern_w == 3:  # 1x3 horizontal pattern
            # Expand to 3x3 at original position and every 4 rows
            expanded_pattern = n.zeros((3, 3), dtype=int)
            expanded_pattern[0, :] = pattern[0, :]  # Top row: original pattern
            expanded_pattern[1, 0] = pattern[0, 0]  # Middle row: only edges
            expanded_pattern[1, 2] = pattern[0, 2]  
            expanded_pattern[2, :] = pattern[0, :]  # Bottom row: original pattern
            
            # Place at original position
            result[min_r:min_r+3, min_c:min_c+3] = expanded_pattern
            
            # Tile every 4 rows
            for offset in range(4, h-min_r, 4):
                new_r = min_r + offset
                if new_r + 2 < h:
                    result[new_r:new_r+3, min_c:min_c+3] = expanded_pattern
                    
        elif pattern_h == 3 and pattern_w == 1:  # 3x1 vertical pattern  
            # Expand to 3x3 at original position and every 4 columns
            expanded_pattern = n.zeros((3, 3), dtype=int)
            expanded_pattern[:, 0] = pattern[:, 0]  # Left column: original pattern
            expanded_pattern[0, 1] = pattern[0, 0]  # Middle column: only edges
            expanded_pattern[2, 1] = pattern[2, 0]  
            expanded_pattern[:, 2] = pattern[:, 0]  # Right column: original pattern
            
            # Place at original position
            result[min_r:min_r+3, min_c:min_c+3] = expanded_pattern
            
            # Tile every 4 columns
            for offset in range(4, w-min_c, 4):
                new_c = min_c + offset
                if new_c + 2 < w:
                    result[min_r:min_r+3, new_c:new_c+3] = expanded_pattern
                    
        elif pattern_h == 1 and pattern_w == 1:  # 1x1 single cell
            # Expand in cross pattern every 2 units
            for r_offset in range(0, h, 2):
                for c_offset in range(0, w, 2):
                    new_r = min_r + r_offset
                    new_c = min_c + c_offset
                    if 0 <= new_r < h and 0 <= new_c < w:
                        result[new_r, new_c] = color
                        
        elif pattern_h == 2 and pattern_w == 2:  # 2x2 pattern
            # Expand to larger pattern every 3 units
            for r_offset in range(0, h, 3):
                for c_offset in range(0, w, 3):
                    new_r = min_r + r_offset
                    new_c = min_c + c_offset
                    if new_r + 1 < h and new_c + 1 < w:
                        result[new_r:new_r+2, new_c:new_c+2] = pattern
        # 3x3 patterns stay unchanged
    
    return result.tolist()