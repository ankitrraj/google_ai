def p(g):
    import numpy as n
    a = n.array(g)
    r = a.copy()
    h, w = a.shape
    
    # Find all 0 regions and check if they're enclosed by 3s
    visited = n.zeros((h, w), dtype=bool)
    
    def flood_fill(start_r, start_c):
        if visited[start_r, start_c] or a[start_r, start_c] != 0:
            return [], False
        
        region = []
        queue = [(start_r, start_c)]
        touches_border = False
        
        while queue:
            r, c = queue.pop(0)
            if r < 0 or r >= h or c < 0 or c >= w or visited[r, c]:
                continue
            if a[r, c] != 0:
                continue
                
            visited[r, c] = True
            region.append((r, c))
            
            # Check if this cell touches the border
            if r == 0 or r == h-1 or c == 0 or c == w-1:
                touches_border = True
            
            # Add neighbors
            for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
                queue.append((r+dr, c+dc))
        
        return region, not touches_border
    
    # Process all 0 regions
    for i in range(h):
        for j in range(w):
            if a[i,j] == 0 and not visited[i,j]:
                region, is_enclosed = flood_fill(i, j)
                if is_enclosed and region:
                    for row, col in region:
                        r[row,col] = 4
    
    return r.tolist()