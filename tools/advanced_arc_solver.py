"""
Advanced ARC-AGI Solver using object detection and spatial reasoning
"""
import json
import numpy as np
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Set, Any

def load_task(task_num: int) -> dict:
    with open(f"data/task{task_num:03d}.json", 'r') as f:
        return json.load(f)

def test_solver_complete(solver_code: str, task_data: dict) -> bool:
    """Test solver against ALL examples (train + test) like Kaggle does"""
    try:
        exec(solver_code, globals())
        solver_func = globals()['p']
        
        # Test ALL train examples
        for example in task_data['train']:
            inp = [row[:] for row in example['input']]
            expected = example['output']
            result = solver_func(inp)
            
            if not np.array_equal(np.array(result), np.array(expected)):
                return False
        
        # Test ALL test examples (if available)
        if 'test' in task_data:
            for example in task_data['test']:
                inp = [row[:] for row in example['input']]
                expected = example['output']
                result = solver_func(inp)
                
                if not np.array_equal(np.array(result), np.array(expected)):
                    return False
        
        return True
    except:
        return False

def find_objects(grid: List[List[int]]) -> List[Dict]:
    """Find connected components (objects) in grid"""
    grid = np.array(grid)
    h, w = grid.shape
    visited = np.zeros((h, w), dtype=bool)
    objects = []
    
    def flood_fill(start_r, start_c, color):
        stack = [(start_r, start_c)]
        cells = []
        
        while stack:
            r, c = stack.pop()
            if r < 0 or r >= h or c < 0 or c >= w or visited[r, c] or grid[r, c] != color:
                continue
            
            visited[r, c] = True
            cells.append((r, c))
            
            # 4-connected neighbors
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                stack.append((r + dr, c + dc))
        
        return cells
    
    for r in range(h):
        for c in range(w):
            if not visited[r, c] and grid[r, c] != 0:  # Non-background
                cells = flood_fill(r, c, grid[r, c])
                if cells:
                    objects.append({
                        'color': grid[r, c],
                        'cells': cells,
                        'size': len(cells),
                        'bbox': (min(r for r, c in cells), min(c for r, c in cells),
                                max(r for r, c in cells), max(c for r, c in cells))
                    })
    
    return objects

def analyze_object_transformations(task_data: dict) -> List[str]:
    """Analyze how objects transform between input and output"""
    patterns = []
    
    for example in task_data['train']:
        inp_objects = find_objects(example['input'])
        out_objects = find_objects(example['output'])
        
        # Object count changes
        if len(out_objects) == len(inp_objects) * 2:
            patterns.append("duplicate_objects")
        elif len(out_objects) == len(inp_objects) // 2:
            patterns.append("merge_objects")
        
        # Size changes
        if inp_objects and out_objects:
            inp_sizes = [obj['size'] for obj in inp_objects]
            out_sizes = [obj['size'] for obj in out_objects]
            
            if all(o == i * 4 for i, o in zip(inp_sizes, out_sizes)):
                patterns.append("scale_2x")
            elif all(o == i // 4 for i, o in zip(inp_sizes, out_sizes)):
                patterns.append("scale_half")
    
    return list(set(patterns))

def generate_object_based_solver(pattern: str) -> str:
    """Generate solver code based on object analysis"""
    if pattern == "duplicate_objects":
        return """def p(g):
import numpy as n
a=n.array(g)
h,w=a.shape
r=n.zeros((h,w*2),dtype=int)
r[:,:w]=a
r[:,w:]=a
return r.tolist()"""
    
    elif pattern == "scale_2x":
        return """def p(g):
import numpy as n
a=n.array(g)
return n.repeat(n.repeat(a,2,0),2,1).tolist()"""
    
    elif pattern == "scale_half":
        return """def p(g):
import numpy as n
a=n.array(g)
return a[::2,::2].tolist()"""
    
    return None

def analyze_spatial_patterns(task_data: dict) -> List[str]:
    """Analyze spatial relationships and patterns"""
    patterns = []
    
    for example in task_data['train']:
        inp = np.array(example['input'])
        out = np.array(example['output'])
        
        # Check if output is input with borders
        if out.shape[0] == inp.shape[0] + 2 and out.shape[1] == inp.shape[1] + 2:
            if np.array_equal(out[1:-1, 1:-1], inp):
                patterns.append("add_border")
        
        # Check if output is cropped input
        if inp.shape[0] > out.shape[0] and inp.shape[1] > out.shape[1]:
            for r in range(inp.shape[0] - out.shape[0] + 1):
                for c in range(inp.shape[1] - out.shape[1] + 1):
                    if np.array_equal(inp[r:r+out.shape[0], c:c+out.shape[1]], out):
                        patterns.append("crop_region")
                        break
        
        # Check for tiling patterns
        if out.shape[0] % inp.shape[0] == 0 and out.shape[1] % inp.shape[1] == 0:
            tile_h = out.shape[0] // inp.shape[0]
            tile_w = out.shape[1] // inp.shape[1]
            if tile_h > 1 or tile_w > 1:
                patterns.append(f"tile_{tile_h}x{tile_w}")
    
    return list(set(patterns))

def generate_spatial_solver(pattern: str) -> str:
    """Generate solver code based on spatial analysis"""
    if pattern == "add_border":
        return """def p(g):
import numpy as n
a=n.array(g)
h,w=a.shape
r=n.zeros((h+2,w+2),dtype=int)
r[1:-1,1:-1]=a
return r.tolist()"""
    
    elif pattern == "crop_region":
        return """def p(g):
import numpy as n
a=n.array(g)
return a[1:-1,1:-1].tolist()"""
    
    elif pattern.startswith("tile_"):
        dims = pattern.split("_")[1].split("x")
        tile_h, tile_w = int(dims[0]), int(dims[1])
        return f"""def p(g):
import numpy as n
a=n.array(g)
return n.tile(a,({tile_h},{tile_w})).tolist()"""
    
    return None

def analyze_rule_patterns(task_data: dict) -> List[str]:
    """Analyze logical rules and conditions"""
    patterns = []
    
    for example in task_data['train']:
        inp = np.array(example['input'])
        out = np.array(example['output'])
        
        # Check for conditional color changes
        unique_inp = set(inp.flatten())
        unique_out = set(out.flatten())
        
        if len(unique_inp) == len(unique_out):
            # Same number of colors - might be color mapping
            color_map = {}
            for i, o in zip(inp.flatten(), out.flatten()):
                if i in color_map and color_map[i] != o:
                    break
                color_map[i] = o
            else:
                if len(color_map) <= 3:  # Simple mapping
                    patterns.append("color_mapping")
        
        # Check for majority/minority rules
        color_counts = Counter(inp.flatten())
        most_common = color_counts.most_common(1)[0][0]
        if np.all(out == most_common):
            patterns.append("fill_majority_color")
    
    return list(set(patterns))

def generate_rule_solver(pattern: str, task_data: dict) -> str:
    """Generate solver code based on rule analysis"""
    if pattern == "fill_majority_color":
        return """def p(g):
from collections import Counter
c=Counter(x for r in g for x in r).most_common(1)[0][0]
return[[c]*len(g[0])for _ in g]"""
    
    elif pattern == "color_mapping":
        # Analyze first example to get mapping
        example = task_data['train'][0]
        inp = np.array(example['input'])
        out = np.array(example['output'])
        
        color_map = {}
        for i, o in zip(inp.flatten(), out.flatten()):
            color_map[i] = o
        
        # Generate mapping code
        mapping_str = str(color_map).replace(" ", "")
        return f"""def p(g):
m={mapping_str}
return[[m.get(c,c)for c in r]for r in g]"""
    
    return None

def solve_task_advanced(task_num: int) -> bool:
    """Solve task using advanced techniques"""
    print(f"\n🧠 Advanced Analysis Task {task_num:03d}...")
    
    task_data = load_task(task_num)
    
    # Try object-based analysis
    obj_patterns = analyze_object_transformations(task_data)
    for pattern in obj_patterns:
        solver = generate_object_based_solver(pattern)
        if solver and test_solver_complete(solver, task_data):
            with open(f"solvers/task{task_num:03d}.py", 'w') as f:
                f.write(solver)
            score = 2500 - len(solver)
            print(f"✅ Task {task_num:03d} SOLVED (Object: {pattern})! Score: {score}")
            return True
    
    # Try spatial analysis
    spatial_patterns = analyze_spatial_patterns(task_data)
    for pattern in spatial_patterns:
        solver = generate_spatial_solver(pattern)
        if solver and test_solver_complete(solver, task_data):
            with open(f"solvers/task{task_num:03d}.py", 'w') as f:
                f.write(solver)
            score = 2500 - len(solver)
            print(f"✅ Task {task_num:03d} SOLVED (Spatial: {pattern})! Score: {score}")
            return True
    
    # Try rule-based analysis
    rule_patterns = analyze_rule_patterns(task_data)
    for pattern in rule_patterns:
        solver = generate_rule_solver(pattern, task_data)
        if solver and test_solver_complete(solver, task_data):
            with open(f"solvers/task{task_num:03d}.py", 'w') as f:
                f.write(solver)
            score = 2500 - len(solver)
            print(f"✅ Task {task_num:03d} SOLVED (Rule: {pattern})! Score: {score}")
            return True
    
    print(f"❌ Task {task_num:03d} - No advanced pattern found")
    return False

def run_advanced_solver():
    """Run advanced solver on all unsolved tasks"""
    print("🚀 ADVANCED ARC-AGI SOLVER")
    print("=" * 50)
    
    # Get list of already solved tasks
    import os
    solved_tasks = set()
    if os.path.exists("solvers"):
        for filename in os.listdir("solvers"):
            if filename.startswith("task") and filename.endswith(".py"):
                task_num = int(filename[4:7])
                # Check if it's a real solver (not identity)
                with open(f"solvers/{filename}", 'r') as f:
                    content = f.read()
                if "def p(g): return g" not in content and len(content) > 20:
                    solved_tasks.add(task_num)
    
    print(f"Already solved: {len(solved_tasks)} tasks")
    
    new_solvers = 0
    total_score = 0
    
    for task_num in range(1, 401):
        if task_num in solved_tasks:
            continue
            
        if solve_task_advanced(task_num):
            new_solvers += 1
            with open(f"solvers/task{task_num:03d}.py", 'r') as f:
                solver_code = f.read()
            task_score = 2500 - len(solver_code)
            total_score += task_score
        
        # Progress update every 50 tasks
        if task_num % 50 == 0:
            print(f"\n📊 Progress: {task_num}/400 tasks analyzed")
            print(f"   New solvers found: {new_solvers}")
            print(f"   Additional score: {total_score:,}")
    
    print(f"\n🏆 ADVANCED SOLVER RESULTS:")
    print(f"   New solvers found: {new_solvers}")
    print(f"   Additional score: {total_score:,}")
    print(f"   Total working solvers: {len(solved_tasks) + new_solvers}")
    
    return new_solvers

if __name__ == "__main__":
    run_advanced_solver()
