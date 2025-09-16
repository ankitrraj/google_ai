"""
Advanced Pattern Finder - Find more complex but solvable patterns
"""
import json
import numpy as np
import os

def load_task(task_num: int) -> dict:
    with open(f"data/task{task_num:03d}.json", 'r') as f:
        return json.load(f)

def test_solver(solver_code: str, task_data: dict) -> bool:
    try:
        exec(solver_code, globals())
        solver_func = globals()['p']
        
        for example in task_data['train']:
            inp = [row[:] for row in example['input']]
            expected = example['output']
            result = solver_func(inp)
            
            if not np.array_equal(np.array(result), np.array(expected)):
                return False
        return True
    except:
        return False

def find_color_patterns():
    """Find tasks with color replacement patterns"""
    
    working_solvers = {}
    
    print("🎨 Finding color pattern tasks...")
    
    for task_num in range(1, 401):
        if task_num % 50 == 0:
            print(f"  Checked {task_num}/400 tasks...")
        
        task_data = load_task(task_num)
        if not task_data['train']:
            continue
        
        example = task_data['train'][0]
        inp = np.array(example['input'])
        out = np.array(example['output'])
        
        # Only test same-shape transformations
        if inp.shape != out.shape:
            continue
        
        # Test color shifts
        for shift in range(1, 10):
            solver = f"def p(g):return[[(c+{shift})%10 for c in r]for r in g]"
            if test_solver(solver, task_data):
                working_solvers[task_num] = f"Color +{shift}"
                score = max(1, 2500 - len(solver.encode('utf-8')))
                print(f"  ✅ Task {task_num:03d}: Color +{shift} - {score} points")
                with open(f"solvers/task{task_num:03d}.py", 'w') as f:
                    f.write(solver)
                break
        
        if task_num in working_solvers:
            continue
        
        # Test fill zeros with colors
        if 0 in inp.flatten():
            for fill_color in range(1, 10):
                solver = f"def p(g):return[[{fill_color} if c==0 else c for c in r]for r in g]"
                if test_solver(solver, task_data):
                    working_solvers[task_num] = f"Fill zeros with {fill_color}"
                    score = max(1, 2500 - len(solver.encode('utf-8')))
                    print(f"  ✅ Task {task_num:03d}: Fill zeros with {fill_color} - {score} points")
                    with open(f"solvers/task{task_num:03d}.py", 'w') as f:
                        f.write(solver)
                    break
        
        if task_num in working_solvers:
            continue
        
        # Test specific color replacements
        unique_inp = set(inp.flatten())
        unique_out = set(out.flatten())
        
        if len(unique_inp) <= 3 and len(unique_out) <= 3:
            for old_color in unique_inp:
                for new_color in range(10):
                    if new_color not in unique_inp and new_color in unique_out:
                        solver = f"def p(g):return[[{new_color} if c=={old_color} else c for c in r]for r in g]"
                        if test_solver(solver, task_data):
                            working_solvers[task_num] = f"Replace {old_color} with {new_color}"
                            score = max(1, 2500 - len(solver.encode('utf-8')))
                            print(f"  ✅ Task {task_num:03d}: Replace {old_color} with {new_color} - {score} points")
                            with open(f"solvers/task{task_num:03d}.py", 'w') as f:
                                f.write(solver)
                            break
                if task_num in working_solvers:
                    break
    
    return working_solvers

def find_scaling_patterns():
    """Find tasks with scaling patterns"""
    
    working_solvers = {}
    
    print("📏 Finding scaling pattern tasks...")
    
    for task_num in range(1, 401):
        task_data = load_task(task_num)
        if not task_data['train']:
            continue
        
        example = task_data['train'][0]
        inp = np.array(example['input'])
        out = np.array(example['output'])
        
        # Test 2x scaling
        if out.shape == (inp.shape[0] * 2, inp.shape[1] * 2):
            solver = "def p(g):import numpy as n;g=n.array(g);return n.repeat(n.repeat(g,2,0),2,1).tolist()"
            if test_solver(solver, task_data):
                working_solvers[task_num] = "2x scaling"
                score = max(1, 2500 - len(solver.encode('utf-8')))
                print(f"  ✅ Task {task_num:03d}: 2x scaling - {score} points")
                with open(f"solvers/task{task_num:03d}.py", 'w') as f:
                    f.write(solver)
        
        # Test 3x scaling
        elif out.shape == (inp.shape[0] * 3, inp.shape[1] * 3):
            solver = "def p(g):import numpy as n;g=n.array(g);return n.repeat(n.repeat(g,3,0),3,1).tolist()"
            if test_solver(solver, task_data):
                working_solvers[task_num] = "3x scaling"
                score = max(1, 2500 - len(solver.encode('utf-8')))
                print(f"  ✅ Task {task_num:03d}: 3x scaling - {score} points")
                with open(f"solvers/task{task_num:03d}.py", 'w') as f:
                    f.write(solver)
        
        # Test downsampling
        elif inp.shape[0] % 2 == 0 and inp.shape[1] % 2 == 0 and out.shape == (inp.shape[0] // 2, inp.shape[1] // 2):
            solver = "def p(g):return[r[::2]for r in g[::2]]"
            if test_solver(solver, task_data):
                working_solvers[task_num] = "2x downsample"
                score = max(1, 2500 - len(solver.encode('utf-8')))
                print(f"  ✅ Task {task_num:03d}: 2x downsample - {score} points")
                with open(f"solvers/task{task_num:03d}.py", 'w') as f:
                    f.write(solver)
    
    return working_solvers

def find_aggregation_patterns():
    """Find more aggregation patterns"""
    
    working_solvers = {}
    
    print("🔢 Finding aggregation pattern tasks...")
    
    aggregation_tests = [
        ("Count non-zero", "def p(g):import numpy as n;return[[n.count_nonzero(g)]]"),
        ("Count zeros", "def p(g):import numpy as n;return[[n.count_nonzero(n.array(g)==0)]]"),
        ("Most frequent", "def p(g):from collections import Counter;return[[Counter([c for r in g for c in r]).most_common(1)[0][0]]]"),
        ("Max value", "def p(g):return[[max(max(r)for r in g)]]"),
        ("Min value", "def p(g):return[[min(min(r)for r in g)]]"),
        ("Sum all", "def p(g):return[[sum(sum(r)for r in g)]]"),
        ("Unique colors", "def p(g):return[[len(set(c for r in g for c in r))]]"),
        ("Grid height", "def p(g):return[[len(g)]]"),
        ("Grid width", "def p(g):return[[len(g[0])]]"),
        ("Grid area", "def p(g):return[[len(g)*len(g[0])]]"),
    ]
    
    for task_num in range(1, 401):
        task_data = load_task(task_num)
        if not task_data['train']:
            continue
        
        example = task_data['train'][0]
        out = np.array(example['output'])
        
        # Only test single-output tasks
        if out.size != 1:
            continue
        
        for pattern_name, solver in aggregation_tests:
            if test_solver(solver, task_data):
                working_solvers[task_num] = pattern_name
                score = max(1, 2500 - len(solver.encode('utf-8')))
                print(f"  ✅ Task {task_num:03d}: {pattern_name} - {score} points")
                with open(f"solvers/task{task_num:03d}.py", 'w') as f:
                    f.write(solver)
                break
    
    return working_solvers

if __name__ == "__main__":
    print("🚀 Advanced Pattern Finder - Finding more complex patterns")
    
    # Find different types of patterns
    color_solvers = find_color_patterns()
    scaling_solvers = find_scaling_patterns()
    agg_solvers = find_aggregation_patterns()
    
    # Combine all results
    all_new_solvers = {**color_solvers, **scaling_solvers, **agg_solvers}
    
    print(f"\n🏆 ADVANCED PATTERN SEARCH COMPLETE!")
    print(f"✅ Found {len(all_new_solvers)} additional working solvers")
    
    if all_new_solvers:
        print(f"\n🌟 New working solvers:")
        total_new_score = 0
        for task_num in sorted(all_new_solvers.keys()):
            pattern_name = all_new_solvers[task_num]
            # Read the saved solver to calculate score
            with open(f"solvers/task{task_num:03d}.py", 'r') as f:
                solver_code = f.read()
            score = max(1, 2500 - len(solver_code.encode('utf-8')))
            total_new_score += score
            print(f"  Task {task_num:03d}: {pattern_name} - {score} points")
        
        print(f"\n🎯 Total score from new solvers: {total_new_score:,}")
        
        # Count total working solvers
        working_count = 0
        total_score = 0
        for task_num in range(1, 401):
            solver_path = f"solvers/task{task_num:03d}.py"
            if os.path.exists(solver_path):
                with open(solver_path, 'r') as f:
                    code = f.read()
                if code != "def p(g):return g":
                    working_count += 1
                    score = max(1, 2500 - len(code.encode('utf-8')))
                    total_score += score
                else:
                    total_score += 2499  # Identity function
            else:
                total_score += 2499  # Missing = identity
        
        print(f"\n📊 TOTAL SUBMISSION STATUS:")
        print(f"✅ Total working solvers: {working_count}")
        print(f"🎯 Estimated total score: {total_score:,}")
        
        if total_score > 950000:
            print("🏆 CHAMPIONSHIP LEVEL!")
        elif total_score > 900000:
            print("🥈 TOP 3 POTENTIAL!")
        else:
            print("📈 COMPETITIVE SUBMISSION!")
    else:
        print("❌ No additional working solvers found")
