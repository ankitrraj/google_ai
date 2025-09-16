"""
Simple Validator - Test individual solvers without external dependencies
"""
import json
import numpy as np
import importlib.util
import sys
import os

def load_task(task_num: int) -> dict:
    """Load task data"""
    with open(f"data/task{task_num:03d}.json", 'r') as f:
        return json.load(f)

def load_solver(task_num: int):
    """Load solver function from file"""
    solver_path = f"solvers/task{task_num:03d}.py"
    
    if not os.path.exists(solver_path):
        return None
    
    spec = importlib.util.spec_from_file_location(f"task{task_num:03d}", solver_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return getattr(module, 'p', None)

def test_solver(task_num: int) -> dict:
    """Test a solver against all examples"""
    task_data = load_task(task_num)
    solver = load_solver(task_num)
    
    if not solver:
        return {"error": "No solver found"}
    
    results = {
        "task": task_num,
        "train_passed": 0,
        "train_total": len(task_data.get('train', [])),
        "test_passed": 0,
        "test_total": len(task_data.get('test', [])),
        "errors": []
    }
    
    # Test on training examples
    for i, example in enumerate(task_data.get('train', [])):
        try:
            inp = [row[:] for row in example['input']]  # Deep copy
            expected = example['output']
            result = solver(inp)
            
            if np.array_equal(np.array(result), np.array(expected)):
                results["train_passed"] += 1
            else:
                results["errors"].append(f"Train example {i}: output mismatch")
                
        except Exception as e:
            results["errors"].append(f"Train example {i}: {str(e)}")
    
    # Test on test examples
    for i, example in enumerate(task_data.get('test', [])):
        try:
            inp = [row[:] for row in example['input']]  # Deep copy
            expected = example['output']
            result = solver(inp)
            
            if np.array_equal(np.array(result), np.array(expected)):
                results["test_passed"] += 1
            else:
                results["errors"].append(f"Test example {i}: output mismatch")
                
        except Exception as e:
            results["errors"].append(f"Test example {i}: {str(e)}")
    
    return results

def test_multiple_tasks(task_nums: list):
    """Test multiple tasks"""
    print("🧪 Testing solvers...")
    
    working_tasks = []
    failing_tasks = []
    
    for task_num in task_nums:
        print(f"Testing task{task_num:03d}...", end=" ")
        
        results = test_solver(task_num)
        
        if "error" in results:
            print(f"❌ {results['error']}")
            failing_tasks.append(task_num)
            continue
        
        train_success = results["train_passed"] == results["train_total"]
        test_success = results["test_passed"] == results["test_total"]
        
        if train_success and test_success:
            print(f"✅ All passed ({results['train_passed']}/{results['train_total']} train, {results['test_passed']}/{results['test_total']} test)")
            working_tasks.append(task_num)
        else:
            print(f"❌ Failed ({results['train_passed']}/{results['train_total']} train, {results['test_passed']}/{results['test_total']} test)")
            if results["errors"]:
                print(f"   Errors: {results['errors'][:2]}")  # Show first 2 errors
            failing_tasks.append(task_num)
    
    print(f"\n📊 Results:")
    print(f"✅ Working: {len(working_tasks)} tasks")
    print(f"❌ Failing: {len(failing_tasks)} tasks")
    
    if working_tasks:
        print(f"Working tasks: {working_tasks}")
    
    return working_tasks, failing_tasks

if __name__ == "__main__":
    # Test the tasks we think should be working
    priority_tasks = [1, 87, 276, 307, 309, 337, 380]
    working, failing = test_multiple_tasks(priority_tasks)
