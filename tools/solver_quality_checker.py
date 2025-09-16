"""
Solver Quality Checker - Check all solvers for issues and fix them
"""
import os
import json
import numpy as np
import importlib.util

def load_task(task_num: int) -> dict:
    with open(f"data/task{task_num:03d}.json", 'r') as f:
        return json.load(f)

def load_solver(task_num: int):
    solver_path = f"solvers/task{task_num:03d}.py"
    if not os.path.exists(solver_path):
        return None
    
    spec = importlib.util.spec_from_file_location(f"task{task_num:03d}", solver_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, 'p', None)

def check_solver_quality(task_num: int):
    """Check if solver works and estimate its score"""
    try:
        task_data = load_task(task_num)
        solver = load_solver(task_num)
        
        if not solver:
            return {"status": "missing", "score": 0}
        
        # Test on training examples
        train_passed = 0
        train_total = len(task_data.get('train', []))
        
        for example in task_data.get('train', []):
            try:
                inp = [row[:] for row in example['input']]
                expected = example['output']
                result = solver(inp)
                
                if np.array_equal(np.array(result), np.array(expected)):
                    train_passed += 1
            except:
                pass
        
        # Read solver file to check code quality
        with open(f"solvers/task{task_num:03d}.py", 'r') as f:
            code = f.read()
        
        code_length = len(code.encode('utf-8'))
        
        if train_passed == train_total and train_total > 0:
            estimated_score = max(1, 2500 - code_length)
            return {"status": "working", "score": estimated_score, "train_passed": train_passed, "train_total": train_total, "code_length": code_length}
        elif "TODO" in code or "Manual analysis needed" in code:
            return {"status": "placeholder", "score": 1000, "train_passed": train_passed, "train_total": train_total, "code_length": code_length}
        else:
            return {"status": "broken", "score": 1, "train_passed": train_passed, "train_total": train_total, "code_length": code_length}
            
    except Exception as e:
        return {"status": "error", "score": 1, "error": str(e)}

def check_all_solvers():
    """Check quality of all 400 solvers"""
    results = {
        "working": [],
        "placeholder": [],
        "broken": [],
        "missing": [],
        "error": [],
        "total_score": 0
    }
    
    print("Checking solver quality...")
    
    for task_num in range(1, 401):
        if task_num % 50 == 0:
            print(f"  Checked {task_num}/400 tasks...")
        
        quality = check_solver_quality(task_num)
        status = quality["status"]
        
        results[status].append({
            "task": task_num,
            "score": quality["score"],
            "details": quality
        })
        
        results["total_score"] += quality["score"]
    
    return results

def print_quality_report(results):
    """Print detailed quality report"""
    print(f"\n=== SOLVER QUALITY REPORT ===")
    print(f"Working solvers: {len(results['working'])}")
    print(f"Placeholder solvers: {len(results['placeholder'])}")
    print(f"Broken solvers: {len(results['broken'])}")
    print(f"Missing solvers: {len(results['missing'])}")
    print(f"Error solvers: {len(results['error'])}")
    print(f"Total estimated score: {results['total_score']:,}")
    
    if results['working']:
        print(f"\n✅ Working solvers ({len(results['working'])}):")
        for solver in results['working'][:10]:  # Show first 10
            details = solver['details']
            print(f"  Task {solver['task']:03d}: {solver['score']} points ({details['code_length']} bytes, {details['train_passed']}/{details['train_total']} passed)")
    
    if results['broken']:
        print(f"\n❌ Broken solvers ({len(results['broken'])}):")
        for solver in results['broken'][:5]:  # Show first 5
            details = solver['details']
            print(f"  Task {solver['task']:03d}: {details['train_passed']}/{details['train_total']} passed")

if __name__ == "__main__":
    results = check_all_solvers()
    print_quality_report(results)
