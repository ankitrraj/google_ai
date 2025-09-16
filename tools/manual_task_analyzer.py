"""
Manual Task Analysis - Deep dive into specific difficult ARC tasks
"""
import json
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple

def load_task(task_num: int) -> dict:
    with open(f"data/task{task_num:03d}.json", 'r') as f:
        return json.load(f)

def visualize_example(inp: List[List[int]], out: List[List[int]], title: str = ""):
    """Visualize input and output side by side"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    ax1.imshow(inp, cmap='tab10', vmin=0, vmax=9)
    ax1.set_title(f"Input {title}")
    ax1.grid(True, alpha=0.3)
    
    ax2.imshow(out, cmap='tab10', vmin=0, vmax=9)
    ax2.set_title(f"Output {title}")
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def analyze_task_001():
    """Deep analysis of Task 001 - Complex tiling pattern"""
    print("🔍 DEEP ANALYSIS OF TASK 001")
    print("=" * 50)
    
    task_data = load_task(1)
    
    print("Pattern Analysis:")
    print("- Input: 3x3 grid")
    print("- Output: 9x9 grid (3x3 tiling)")
    print("- Each 3x3 tile in output has different placement of input")
    
    for i, example in enumerate(task_data['train']):
        print(f"\nExample {i+1}:")
        inp = np.array(example['input'])
        out = np.array(example['output'])
        
        print(f"Input shape: {inp.shape}")
        print(f"Output shape: {out.shape}")
        
        # Analyze tile positions
        for tile_r in range(3):
            for tile_c in range(3):
                start_r, start_c = tile_r * 3, tile_c * 3
                tile = out[start_r:start_r+3, start_c:start_c+3]
                
                # Check if tile matches input exactly
                if np.array_equal(tile, inp):
                    print(f"  Tile ({tile_r},{tile_c}): EXACT MATCH")
                else:
                    # Check for transformations
                    if np.array_equal(tile, np.rot90(inp, 1)):
                        print(f"  Tile ({tile_r},{tile_c}): 90° rotation")
                    elif np.array_equal(tile, np.rot90(inp, 2)):
                        print(f"  Tile ({tile_r},{tile_c}): 180° rotation")
                    elif np.array_equal(tile, np.rot90(inp, 3)):
                        print(f"  Tile ({tile_r},{tile_c}): 270° rotation")
                    elif np.array_equal(tile, np.fliplr(inp)):
                        print(f"  Tile ({tile_r},{tile_c}): Horizontal flip")
                    elif np.array_equal(tile, np.flipud(inp)):
                        print(f"  Tile ({tile_r},{tile_c}): Vertical flip")
                    elif np.array_equal(tile, np.zeros_like(inp)):
                        print(f"  Tile ({tile_r},{tile_c}): ZEROS")
                    else:
                        print(f"  Tile ({tile_r},{tile_c}): CUSTOM PATTERN")
        
        # visualize_example(inp, out, f"Example {i+1}")

def analyze_task_pattern(task_num: int):
    """Analyze any task pattern in detail"""
    print(f"\n🔍 ANALYZING TASK {task_num:03d}")
    print("=" * 40)
    
    task_data = load_task(task_num)
    
    for i, example in enumerate(task_data['train']):
        inp = np.array(example['input'])
        out = np.array(example['output'])
        
        print(f"\nExample {i+1}:")
        print(f"  Input shape: {inp.shape}")
        print(f"  Output shape: {out.shape}")
        print(f"  Input colors: {sorted(set(inp.flatten()))}")
        print(f"  Output colors: {sorted(set(out.flatten()))}")
        
        # Size relationship
        if out.shape == inp.shape:
            print("  Size: SAME")
        elif out.shape[0] == inp.shape[0] * 2 and out.shape[1] == inp.shape[1] * 2:
            print("  Size: 2x SCALING")
        elif out.shape[0] == inp.shape[0] * 3 and out.shape[1] == inp.shape[1] * 3:
            print("  Size: 3x SCALING")
        else:
            print(f"  Size: CUSTOM ({out.shape[0]/inp.shape[0]:.1f}x, {out.shape[1]/inp.shape[1]:.1f}x)")
        
        # Color analysis
        inp_unique = set(inp.flatten())
        out_unique = set(out.flatten())
        
        if inp_unique == out_unique:
            print("  Colors: PRESERVED")
        elif len(out_unique) < len(inp_unique):
            print("  Colors: REDUCED")
        elif len(out_unique) > len(inp_unique):
            print("  Colors: EXPANDED")
        else:
            print("  Colors: CHANGED")

def generate_custom_solver_for_task(task_num: int) -> str:
    """Try to generate a custom solver for specific task"""
    task_data = load_task(task_num)
    
    # Analyze first example in detail
    example = task_data['train'][0]
    inp = np.array(example['input'])
    out = np.array(example['output'])
    
    # Task 001 specific pattern (complex tiling)
    if task_num == 1:
        return "def p(g):import numpy as n;a=n.array(g);r=n.zeros((9,9),dtype=int);r[0:3,3:6]=a;r[0:3,6:9]=a;r[3:6,0:3]=a;r[3:6,6:9]=a;r[6:9,3:6]=a;r[6:9,6:9]=a;return r.tolist()"
    
    # Try to detect simple patterns
    if out.shape == (inp.shape[0] * 3, inp.shape[1] * 3):
        # 3x3 tiling - try different arrangements
        patterns = [
            # Simple 3x3 tile
            """def p(g):
import numpy as n
return n.tile(n.array(g),(3,3)).tolist()""",
            
            # Checkerboard pattern
            """def p(g):
import numpy as n
a=n.array(g)
r=n.zeros((len(g)*3,len(g[0])*3),dtype=int)
for i in range(3):
    for j in range(3):
        if (i+j)%2==0:
            r[i*len(g):(i+1)*len(g),j*len(g[0]):(j+1)*len(g[0])]=a
return r.tolist()""",
        ]
        
        return patterns[0]  # Try simple tiling first
    
    return None

def test_custom_solvers():
    """Test custom solvers on difficult tasks"""
    print("🧪 TESTING CUSTOM SOLVERS")
    print("=" * 30)
    
    difficult_tasks = [1, 5, 10, 15, 20, 25, 30]  # Sample of difficult tasks
    
    for task_num in difficult_tasks:
        print(f"\nTesting Task {task_num:03d}...")
        
        task_data = load_task(task_num)
        solver_code = generate_custom_solver_for_task(task_num)
        
        if solver_code:
            try:
                exec(solver_code, globals())
                solver_func = globals()['p']
                
                # Test on first training example
                example = task_data['train'][0]
                inp = [row[:] for row in example['input']]
                expected = example['output']
                result = solver_func(inp)
                
                if np.array_equal(np.array(result), np.array(expected)):
                    print(f"✅ Custom solver works for Task {task_num:03d}!")
                    
                    # Test on all examples
                    all_pass = True
                    for ex in task_data['train']:
                        inp = [row[:] for row in ex['input']]
                        expected = ex['output']
                        result = solver_func(inp)
                        if not np.array_equal(np.array(result), np.array(expected)):
                            all_pass = False
                            break
                    
                    if all_pass:
                        print(f"🎯 ALL EXAMPLES PASS! Saving solver...")
                        with open(f"solvers/task{task_num:03d}.py", 'w') as f:
                            f.write(solver_code)
                    else:
                        print(f"⚠️ Only first example passes")
                else:
                    print(f"❌ Custom solver failed")
            except Exception as e:
                print(f"❌ Solver error: {e}")
        else:
            print(f"❌ No custom solver generated")

def manual_analysis_session():
    """Interactive manual analysis session"""
    print("🔍 MANUAL ARC TASK ANALYSIS")
    print("=" * 40)
    
    # Analyze specific challenging tasks
    challenging_tasks = [1, 2, 3, 4, 5]
    
    for task_num in challenging_tasks:
        analyze_task_pattern(task_num)
        print("\n" + "-" * 40)
    
    # Deep dive into Task 001
    analyze_task_001()
    
    # Test custom solvers
    test_custom_solvers()

if __name__ == "__main__":
    manual_analysis_session()
