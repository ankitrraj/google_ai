"""
Manual Solver - Analyze and solve tasks manually for maximum score improvement
"""
import json
import numpy as np
import random

def load_task(task_num: int) -> dict:
    with open(f"data/task{task_num:03d}.json", 'r') as f:
        return json.load(f)

def analyze_and_solve_task(task_num: int):
    """Analyze a task and attempt to create a working solver"""
    task_data = load_task(task_num)
    
    if not task_data['train']:
        return None
    
    print(f"\n=== ANALYZING TASK {task_num:03d} ===")
    
    examples = []
    for i, example in enumerate(task_data['train'][:3]):
        inp = np.array(example['input'])
        out = np.array(example['output'])
        examples.append((inp, out))
        
        print(f"Example {i+1}: {inp.shape} -> {out.shape}")
        print(f"  Input colors: {sorted(set(inp.flatten()))}")
        print(f"  Output colors: {sorted(set(out.flatten()))}")
    
    # Try different solving strategies
    solver = None
    
    # Strategy 1: Simple transformations
    solver = try_simple_transforms(examples)
    if solver:
        return solver
    
    # Strategy 2: Color-based rules
    solver = try_color_rules(examples)
    if solver:
        return solver
    
    # Strategy 3: Pattern-based rules
    solver = try_pattern_rules(examples)
    if solver:
        return solver
    
    return None

def try_simple_transforms(examples):
    """Try simple geometric transformations"""
    inp, out = examples[0]
    
    if inp.shape != out.shape:
        return None
    
    # Identity
    if np.array_equal(inp, out):
        if all(np.array_equal(i, o) for i, o in examples):
            return "def p(g):return g"
    
    # Rotations
    for k in [1, 2, 3]:
        if np.array_equal(out, np.rot90(inp, k)):
            if all(np.array_equal(o, np.rot90(i, k)) for i, o in examples):
                return f"def p(g):import numpy as n;return n.rot90(n.array(g),{k}).tolist()"
    
    # Flips
    if np.array_equal(out, np.flipud(inp)):
        if all(np.array_equal(o, np.flipud(i)) for i, o in examples):
            return "def p(g):import numpy as n;return n.flipud(n.array(g)).tolist()"
    
    if np.array_equal(out, np.fliplr(inp)):
        if all(np.array_equal(o, np.fliplr(i)) for i, o in examples):
            return "def p(g):import numpy as n;return n.fliplr(n.array(g)).tolist()"
    
    return None

def try_color_rules(examples):
    """Try color-based transformation rules"""
    inp, out = examples[0]
    
    if inp.shape != out.shape:
        return None
    
    # Check for consistent color mapping
    mapping = {}
    for i in range(inp.shape[0]):
        for j in range(inp.shape[1]):
            ic, oc = inp[i, j], out[i, j]
            if ic in mapping:
                if mapping[ic] != oc:
                    return None
            else:
                mapping[ic] = oc
    
    # Verify mapping on all examples
    for inp_ex, out_ex in examples:
        for i in range(inp_ex.shape[0]):
            for j in range(inp_ex.shape[1]):
                if mapping.get(inp_ex[i, j]) != out_ex[i, j]:
                    return None
    
    # Generate solver
    if len(mapping) <= 10:  # Reasonable mapping size
        return f"def p(g):m={dict(mapping)};return[[m.get(c,c)for c in r]for r in g]"
    
    return None

def try_pattern_rules(examples):
    """Try pattern-based rules"""
    inp, out = examples[0]
    
    # Check for fill patterns
    if inp.shape == out.shape:
        # Fill zeros with specific color
        zero_positions = (inp == 0)
        if np.any(zero_positions):
            fill_colors = out[zero_positions]
            if len(set(fill_colors)) == 1:
                fill_color = fill_colors[0]
                # Check if non-zero positions remain unchanged
                if np.array_equal(inp[~zero_positions], out[~zero_positions]):
                    # Verify on all examples
                    works = True
                    for inp_ex, out_ex in examples:
                        zero_pos = (inp_ex == 0)
                        if not np.all(out_ex[zero_pos] == fill_color):
                            works = False
                            break
                        if not np.array_equal(inp_ex[~zero_pos], out_ex[~zero_pos]):
                            works = False
                            break
                    
                    if works:
                        return f"def p(g):return[[{fill_color} if c==0 else c for c in r]for r in g]"
    
    return None

def solve_high_priority_tasks():
    """Solve tasks that are likely to have simple patterns"""
    # Focus on tasks that might have simple patterns
    priority_tasks = random.sample(range(2, 101), 20)  # Random sample from first 100 tasks
    
    solved_count = 0
    total_estimated_score = 0
    
    for task_num in priority_tasks:
        solver = analyze_and_solve_task(task_num)
        
        if solver:
            # Write the solver
            with open(f"solvers/task{task_num:03d}.py", 'w') as f:
                f.write(solver)
            
            print(f"✅ SOLVED task {task_num:03d}")
            solved_count += 1
            
            # Estimate score (shorter code = higher score)
            code_length = len(solver.encode('utf-8'))
            estimated_score = max(1, 2500 - code_length)
            total_estimated_score += estimated_score
            
        else:
            print(f"❌ Could not solve task {task_num:03d}")
    
    print(f"\n📊 Manual Solving Results:")
    print(f"✅ Solved: {solved_count}/20 tasks")
    print(f"🏆 Additional Score: {total_estimated_score:,}")
    
    return solved_count, total_estimated_score

if __name__ == "__main__":
    solve_high_priority_tasks()
