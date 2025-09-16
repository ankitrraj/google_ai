"""
Manual Task Debugger - Deep dive into specific tasks to understand patterns
"""
import json
import numpy as np
import matplotlib.pyplot as plt

def load_task(task_num: int) -> dict:
    with open(f"data/task{task_num:03d}.json", 'r') as f:
        return json.load(f)

def visualize_task(task_num: int):
    """Visualize a task to understand the pattern"""
    task_data = load_task(task_num)
    
    print(f"=== TASK {task_num:03d} ANALYSIS ===")
    
    for i, example in enumerate(task_data['train']):
        inp = np.array(example['input'])
        out = np.array(example['output'])
        
        print(f"\nExample {i+1}:")
        print(f"Input shape: {inp.shape}")
        print(f"Output shape: {out.shape}")
        print(f"Input colors: {sorted(set(inp.flatten()))}")
        print(f"Output colors: {sorted(set(out.flatten()))}")
        
        if inp.size <= 50:  # Small enough to print
            print("Input:")
            print(inp)
        
        if out.size <= 50:  # Small enough to print
            print("Output:")
            print(out)
        
        # Analyze relationship
        if inp.shape == out.shape:
            if np.array_equal(inp, out):
                print("→ Identity transformation")
            elif np.array_equal(inp, np.rot90(out, 1)):
                print("→ 90° counter-clockwise rotation")
            elif np.array_equal(inp, np.rot90(out, 2)):
                print("→ 180° rotation")
            elif np.array_equal(inp, np.rot90(out, 3)):
                print("→ 90° clockwise rotation")
            elif np.array_equal(inp, np.flipud(out)):
                print("→ Vertical flip")
            elif np.array_equal(inp, np.fliplr(out)):
                print("→ Horizontal flip")
            else:
                print("→ Complex same-size transformation")
        
        elif out.shape == (inp.shape[0] * 3, inp.shape[1] * 3):
            print("→ 3x3 tiling pattern")
            # Check which positions have the input
            h, w = inp.shape
            positions = []
            for ti in range(3):
                for tj in range(3):
                    tile = out[ti*h:(ti+1)*h, tj*w:(tj+1)*w]
                    if np.array_equal(tile, inp):
                        positions.append((ti, tj))
            print(f"  Input appears at positions: {positions}")
        
        elif out.shape == (inp.shape[0] * 2, inp.shape[1] * 2):
            print("→ 2x2 scaling")
        
        else:
            print("→ Complex size transformation")

def test_manual_solution(task_num: int, solver_code: str):
    """Test a manually created solution"""
    task_data = load_task(task_num)
    
    try:
        exec(solver_code, globals())
        solver_func = globals()['p']
        
        all_correct = True
        for i, example in enumerate(task_data['train']):
            inp = [row[:] for row in example['input']]
            expected = example['output']
            result = solver_func(inp)
            
            if not np.array_equal(np.array(result), np.array(expected)):
                print(f"❌ Example {i+1} failed")
                print(f"Expected: {np.array(expected).shape}")
                print(f"Got: {np.array(result).shape}")
                all_correct = False
            else:
                print(f"✅ Example {i+1} passed")
        
        if all_correct:
            score = max(1, 2500 - len(solver_code.encode('utf-8')))
            print(f"🏆 All examples passed! Score: {score} ({len(solver_code.encode('utf-8'))} bytes)")
            return True
        else:
            print("❌ Solution failed")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def analyze_task_001():
    """Deep analysis of task 001"""
    print("🔍 DEEP ANALYSIS OF TASK 001")
    visualize_task(1)
    
    # Let's manually create the solution based on analysis
    task_data = load_task(1)
    example = task_data['train'][0]
    inp = np.array(example['input'])
    out = np.array(example['output'])
    
    print(f"\nDetailed analysis of first example:")
    print(f"Input:\n{inp}")
    print(f"Output shape: {out.shape}")
    
    # Check each 3x3 tile in output
    h, w = inp.shape
    print(f"\nChecking each 3x3 tile:")
    for i in range(3):
        for j in range(3):
            tile = out[i*h:(i+1)*h, j*w:(j+1)*w]
            is_input = np.array_equal(tile, inp)
            is_zeros = np.all(tile == 0)
            print(f"Tile ({i},{j}): {'INPUT' if is_input else 'ZEROS' if is_zeros else 'OTHER'}")
    
    # Try different tiling patterns
    patterns_to_test = [
        # Pattern 1: All except (0,0) and (2,0)
        "[(0,1), (0,2), (1,0), (1,1), (1,2), (2,1), (2,2)]",
        # Pattern 2: All except (1,1) 
        "[(0,0), (0,1), (0,2), (1,0), (1,2), (2,0), (2,1), (2,2)]",
        # Pattern 3: Specific pattern from analysis
        "[(0,1), (0,2), (1,0), (1,1), (1,2), (2,1), (2,2)]"
    ]
    
    for i, pattern in enumerate(patterns_to_test):
        solver = f"""def p(g):
 import numpy as n
 g=n.array(g)
 h,w=g.shape
 r=n.zeros((h*3,w*3),int)
 for i,j in {pattern}:r[i*h:(i+1)*h,j*w:(j+1)*w]=g
 return r.tolist()"""
        
        print(f"\nTesting pattern {i+1}: {pattern}")
        if test_manual_solution(1, solver):
            return solver
    
    return None

if __name__ == "__main__":
    # Analyze task 001 in detail
    solution = analyze_task_001()
    
    if solution:
        print(f"\n🎉 FOUND SOLUTION FOR TASK 001!")
        with open("solvers/task001.py", 'w') as f:
            f.write(solution)
        print("✅ Saved to solvers/task001.py")
    else:
        print("\n❌ Could not solve task 001")
    
    # Also check a few more tasks manually
    for task_num in [2, 3, 10, 87]:
        print(f"\n" + "="*50)
        visualize_task(task_num)
