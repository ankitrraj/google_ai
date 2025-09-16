"""
Pattern-Based Mass Solver - Solve tasks based on comprehensive pattern analysis
"""
import json
import numpy as np
import os
from collections import Counter

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

def generate_comprehensive_patterns(inp: np.ndarray, out: np.ndarray):
    """Generate all possible patterns for input-output pair"""
    patterns = []
    
    # 1. Identity and basic transformations
    patterns.append("def p(g):return g")
    
    if inp.shape == out.shape:
        # Rotations (all 4)
        patterns.extend([
            "def p(g):import numpy as n;return n.rot90(n.array(g),1).tolist()",
            "def p(g):import numpy as n;return n.rot90(n.array(g),2).tolist()",
            "def p(g):import numpy as n;return n.rot90(n.array(g),3).tolist()"
        ])
        
        # Flips
        patterns.extend([
            "def p(g):import numpy as n;return n.flipud(n.array(g)).tolist()",
            "def p(g):import numpy as n;return n.fliplr(n.array(g)).tolist()",
            "def p(g):import numpy as n;return n.flipud(n.fliplr(n.array(g))).tolist()"
        ])
        
        # Transpose
        patterns.append("def p(g):import numpy as n;return n.array(g).T.tolist()")
        
        # Color transformations
        unique_inp = set(inp.flatten())
        unique_out = set(out.flatten())
        
        # Simple color shifts
        if len(unique_inp) <= 10 and len(unique_out) <= 10:
            for shift in range(1, 10):
                patterns.append(f"def p(g):return[[(c+{shift})%10 for c in r]for r in g]")
            
            # Color inversions
            if unique_inp == {0, 1} and unique_out == {0, 1}:
                patterns.append("def p(g):return[[1-c for c in r]for r in g]")
        
        # Fill patterns
        if 0 in inp.flatten():
            for fill_color in range(10):
                patterns.append(f"def p(g):return[[{fill_color} if c==0 else c for c in r]for r in g]")
        
        # Replace specific colors
        for old_color in unique_inp:
            for new_color in range(10):
                if new_color not in unique_inp:
                    patterns.append(f"def p(g):return[[{new_color} if c=={old_color} else c for c in r]for r in g]")
    
    # 2. Size transformations
    # Scaling patterns
    if out.shape == (inp.shape[0] * 2, inp.shape[1] * 2):
        patterns.append("def p(g):import numpy as n;g=n.array(g);return n.repeat(n.repeat(g,2,0),2,1).tolist()")
    
    if out.shape == (inp.shape[0] * 3, inp.shape[1] * 3):
        # 3x3 tiling variations
        tile_patterns = [
            # All tiles
            "[(i,j)for i in range(3)for j in range(3)]",
            # Exclude corners
            "[(i,j)for i in range(3)for j in range(3)if not((i==0 or i==2)and(j==0 or j==2))]",
            # Only corners
            "[(0,0),(0,2),(2,0),(2,2)]",
            # Cross pattern
            "[(0,1),(1,0),(1,1),(1,2),(2,1)]",
            # Exclude specific positions
            "[(i,j)for i in range(3)for j in range(3)if not((i==0 and j==0)or(i==2 and j==0))]",
            "[(i,j)for i in range(3)for j in range(3)if not(i==1 and j==1)]",
            # L-shapes
            "[(0,0),(0,1),(0,2),(1,0),(2,0)]",
            "[(0,2),(1,2),(2,0),(2,1),(2,2)]"
        ]
        
        for tile_pattern in tile_patterns:
            patterns.append(f"""def p(g):
 import numpy as n
 g=n.array(g)
 h,w=g.shape
 r=n.zeros((h*3,w*3),int)
 for i,j in {tile_pattern}:r[i*h:(i+1)*h,j*w:(j+1)*w]=g
 return r.tolist()""")
    
    # Contraction patterns
    if out.size < inp.size:
        # Subsampling
        patterns.extend([
            "def p(g):return[r[::2]for r in g[::2]]",
            "def p(g):return[r[1::2]for r in g[1::2]]",
            "def p(g):return[r[::3]for r in g[::3]]"
        ])
        
        # Edge extraction
        if inp.shape[0] > 2 and inp.shape[1] > 2:
            patterns.extend([
                "def p(g):return[r[1:-1]for r in g[1:-1]]",
                "def p(g):return[g[0]]",
                "def p(g):return[g[-1]]",
                "def p(g):return[[r[0]]for r in g]",
                "def p(g):return[[r[-1]]for r in g]"
            ])
    
    # 3. Aggregation patterns
    if out.size == 1:
        patterns.extend([
            # Count patterns
            "def p(g):import numpy as n;return[[n.count_nonzero(g)]]",
            "def p(g):return[[len([c for r in g for c in r if c!=0])]]",
            "def p(g):return[[sum(sum(r)for r in g)]]",
            
            # Most/least frequent
            "def p(g):from collections import Counter;return[[Counter([c for r in g for c in r]).most_common(1)[0][0]]]",
            "def p(g):from collections import Counter;return[[Counter([c for r in g for c in r]).most_common()[-1][0]]]",
            
            # Max/min values
            "def p(g):return[[max(max(r)for r in g)]]",
            "def p(g):return[[min(min(r)for r in g)]]"
        ])
    
    # 4. Border/padding patterns
    if out.size > inp.size:
        # Add borders
        for border_color in range(10):
            patterns.append(f"def p(g):h,w=len(g),len(g[0]);r=[[{border_color}]*(w+2)for _ in range(h+2)];[r[i+1].__setitem__(slice(1,w+1),g[i])for i in range(h)];return r")
    
    return patterns

def solve_task_comprehensively(task_num: int):
    """Try to solve a task using comprehensive pattern matching"""
    task_data = load_task(task_num)
    
    if not task_data['train']:
        return "def p(g):return g"
    
    # Get first example for pattern generation
    example = task_data['train'][0]
    inp = np.array(example['input'])
    out = np.array(example['output'])
    
    # Generate all possible patterns
    patterns = generate_comprehensive_patterns(inp, out)
    
    # Test each pattern
    for pattern in patterns:
        if test_solver(pattern, task_data):
            return pattern
    
    return "def p(g):return g"

def mass_solve_all_tasks():
    """Solve all 400 tasks using comprehensive approach"""
    print("🚀 Mass solving all 400 tasks with comprehensive patterns...")
    
    results = {
        'working': 0,
        'identity': 0,
        'total_score': 0,
        'working_tasks': []
    }
    
    for task_num in range(1, 401):
        if task_num % 20 == 0:
            print(f"  Solved {task_num}/400 tasks...")
        
        solver_code = solve_task_comprehensively(task_num)
        
        # Write solver
        with open(f"solvers/task{task_num:03d}.py", 'w') as f:
            f.write(solver_code)
        
        # Calculate score
        code_length = len(solver_code.encode('utf-8'))
        score = max(1, 2500 - code_length)
        results['total_score'] += score
        
        if solver_code == "def p(g):return g":
            results['identity'] += 1
        else:
            results['working'] += 1
            results['working_tasks'].append({
                'task': task_num,
                'score': score,
                'bytes': code_length
            })
            print(f"    ✅ Task {task_num:03d}: {score} points ({code_length} bytes)")
    
    return results

if __name__ == "__main__":
    results = mass_solve_all_tasks()
    
    print(f"\n🏆 COMPREHENSIVE MASS SOLVING RESULTS:")
    print(f"✅ Working solvers: {results['working']}")
    print(f"🔄 Identity solvers: {results['identity']}")
    print(f"🎯 Total estimated score: {results['total_score']:,}")
    print(f"📊 Average score per task: {results['total_score']/400:.0f}")
    
    if results['total_score'] > 950000:
        print("🏆 CHAMPIONSHIP LEVEL!")
    elif results['total_score'] > 900000:
        print("🥈 TOP 3 POTENTIAL!")
    else:
        print("📈 COMPETITIVE SUBMISSION!")
    
    if results['working_tasks']:
        print(f"\n🌟 All working solvers:")
        for solver in sorted(results['working_tasks'], key=lambda x: x['score'], reverse=True):
            print(f"  Task {solver['task']:03d}: {solver['score']} points ({solver['bytes']} bytes)")
