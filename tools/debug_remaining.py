"""
Debug remaining failing tasks
"""
import json
import numpy as np

def load_task(task_num: int) -> dict:
    with open(f"data/task{task_num:03d}.json", 'r') as f:
        return json.load(f)

def debug_task(task_num: int):
    task_data = load_task(task_num)
    print(f"\n=== TASK {task_num} DEBUG ===")
    
    for i, example in enumerate(task_data['train'][:2]):
        inp = np.array(example['input'])
        out = np.array(example['output'])
        
        print(f"\nExample {i+1}:")
        print(f"Input shape: {inp.shape}, Output shape: {out.shape}")
        print(f"Input colors: {sorted(set(inp.flatten()))}")
        print(f"Output colors: {sorted(set(out.flatten()))}")
        
        if inp.shape == out.shape:
            # Check for color mapping
            mapping = {}
            consistent = True
            for r in range(inp.shape[0]):
                for c in range(inp.shape[1]):
                    ic, oc = inp[r,c], out[r,c]
                    if ic in mapping:
                        if mapping[ic] != oc:
                            consistent = False
                            break
                    else:
                        mapping[ic] = oc
                if not consistent:
                    break
            
            if consistent:
                print(f"Color mapping: {mapping}")
            else:
                print("No consistent color mapping")

if __name__ == "__main__":
    for task in [1, 309, 337]:
        debug_task(task)
