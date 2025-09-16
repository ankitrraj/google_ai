"""
Quick Solver Fixer - Fix obvious patterns and improve score quickly
"""
import json
import numpy as np
import os

def load_task(task_num: int) -> dict:
    with open(f"data/task{task_num:03d}.json", 'r') as f:
        return json.load(f)

def analyze_and_fix_task(task_num: int):
    """Quick analysis and fix for simple patterns"""
    task_data = load_task(task_num)
    
    if not task_data['train']:
        return None
    
    example = task_data['train'][0]
    inp = np.array(example['input'])
    out = np.array(example['output'])
    
    # Identity transformation
    if np.array_equal(inp, out):
        if all(np.array_equal(np.array(ex['input']), np.array(ex['output'])) for ex in task_data['train']):
            return "def p(g):return g"
    
    # Same size transformations
    if inp.shape == out.shape:
        # Rotations
        for k, deg in [(1, 90), (2, 180), (3, 270)]:
            if np.array_equal(out, np.rot90(inp, k)):
                if all(np.array_equal(np.array(ex['output']), np.rot90(np.array(ex['input']), k)) for ex in task_data['train']):
                    return f"def p(g):import numpy as n;return n.rot90(n.array(g),{k}).tolist()"
        
        # Flips
        if np.array_equal(out, np.flipud(inp)):
            if all(np.array_equal(np.array(ex['output']), np.flipud(np.array(ex['input']))) for ex in task_data['train']):
                return "def p(g):import numpy as n;return n.flipud(n.array(g)).tolist()"
        
        if np.array_equal(out, np.fliplr(inp)):
            if all(np.array_equal(np.array(ex['output']), np.fliplr(np.array(ex['input']))) for ex in task_data['train']):
                return "def p(g):import numpy as n;return n.fliplr(n.array(g)).tolist()"
        
        # Transpose
        if np.array_equal(out, inp.T):
            if all(np.array_equal(np.array(ex['output']), np.array(ex['input']).T) for ex in task_data['train']):
                return "def p(g):import numpy as n;return n.array(g).T.tolist()"
        
        # Simple color mapping
        mapping = {}
        valid_mapping = True
        for i in range(inp.shape[0]):
            for j in range(inp.shape[1]):
                ic, oc = inp[i,j], out[i,j]
                if ic in mapping:
                    if mapping[ic] != oc:
                        valid_mapping = False
                        break
                else:
                    mapping[ic] = oc
            if not valid_mapping:
                break
        
        if valid_mapping and len(mapping) <= 10:
            # Verify on all examples
            works = True
            for ex in task_data['train']:
                ex_inp = np.array(ex['input'])
                ex_out = np.array(ex['output'])
                for i in range(ex_inp.shape[0]):
                    for j in range(ex_inp.shape[1]):
                        if mapping.get(ex_inp[i,j]) != ex_out[i,j]:
                            works = False
                            break
                    if not works:
                        break
                if not works:
                    break
            
            if works:
                return f"def p(g):m={dict(mapping)};return[[m.get(c,c)for c in r]for r in g]"
    
    # 2x scaling
    if out.shape == (inp.shape[0] * 2, inp.shape[1] * 2):
        scaled = np.repeat(np.repeat(inp, 2, axis=0), 2, axis=1)
        if np.array_equal(out, scaled):
            if all(np.array_equal(np.array(ex['output']), 
                                np.repeat(np.repeat(np.array(ex['input']), 2, axis=0), 2, axis=1)) 
                   for ex in task_data['train']):
                return "def p(g):import numpy as n;g=n.array(g);return n.repeat(n.repeat(g,2,0),2,1).tolist()"
    
    return None

def fix_multiple_tasks():
    """Fix multiple tasks quickly"""
    print("🔧 Quick fixing solvers...")
    
    fixed_count = 0
    total_score_improvement = 0
    
    # Check first 100 tasks for simple patterns
    for task_num in range(1, 101):
        if task_num % 20 == 0:
            print(f"  Checked {task_num}/100 tasks...")
        
        solver_code = analyze_and_fix_task(task_num)
        
        if solver_code:
            # Write the fixed solver
            with open(f"solvers/task{task_num:03d}.py", 'w') as f:
                f.write(solver_code)
            
            fixed_count += 1
            # Estimate score improvement
            code_length = len(solver_code.encode('utf-8'))
            score = max(1, 2500 - code_length)
            total_score_improvement += (score - 1000)  # Improvement over placeholder
            
            print(f"✅ Fixed task {task_num:03d} - {score} points ({code_length} bytes)")
    
    print(f"\n📊 Quick Fix Results:")
    print(f"✅ Fixed: {fixed_count} tasks")
    print(f"🏆 Score improvement: +{total_score_improvement:,} points")
    
    return fixed_count, total_score_improvement

if __name__ == "__main__":
    fix_multiple_tasks()
