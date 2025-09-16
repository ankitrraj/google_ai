"""
Task Debugger - Analyze specific failing tasks to understand the exact pattern
"""
import json
import numpy as np

def load_task(task_num: int) -> dict:
    """Load task data"""
    with open(f"data/task{task_num:03d}.json", 'r') as f:
        return json.load(f)

def debug_task001():
    """Debug task001 to understand the actual pattern"""
    task_data = load_task(1)
    
    print("=== TASK 001 DEBUG ===")
    
    for i, example in enumerate(task_data['train'][:2]):  # First 2 examples
        inp = np.array(example['input'])
        out = np.array(example['output'])
        
        print(f"\nExample {i+1}:")
        print(f"Input shape: {inp.shape}")
        print(f"Output shape: {out.shape}")
        print(f"Input:\n{inp}")
        print(f"Output:\n{out}")
        
        # Analyze the 3x3 pattern
        h, w = inp.shape
        print(f"\nAnalyzing 3x3 tiling pattern:")
        for tile_i in range(3):
            for tile_j in range(3):
                tile = out[tile_i*h:(tile_i+1)*h, tile_j*w:(tile_j+1)*w]
                is_input = np.array_equal(tile, inp)
                is_zeros = np.all(tile == 0)
                print(f"Tile ({tile_i},{tile_j}): {'INPUT' if is_input else 'ZEROS' if is_zeros else 'OTHER'}")

def debug_task276():
    """Debug task276 color mapping"""
    task_data = load_task(276)
    
    print("\n=== TASK 276 DEBUG ===")
    
    example = task_data['train'][0]
    inp = np.array(example['input'])
    out = np.array(example['output'])
    
    print(f"Input shape: {inp.shape}")
    print(f"Output shape: {out.shape}")
    print(f"Input colors: {sorted(set(inp.flatten()))}")
    print(f"Output colors: {sorted(set(out.flatten()))}")
    
    # Analyze color mapping
    if inp.shape == out.shape:
        mapping = {}
        for i in range(inp.shape[0]):
            for j in range(inp.shape[1]):
                inp_color = inp[i, j]
                out_color = out[i, j]
                if inp_color in mapping:
                    if mapping[inp_color] != out_color:
                        print(f"Inconsistent mapping at ({i},{j}): {inp_color} -> {out_color} vs {mapping[inp_color]}")
                else:
                    mapping[inp_color] = out_color
        
        print(f"Color mapping: {mapping}")

if __name__ == "__main__":
    debug_task001()
    debug_task276()
