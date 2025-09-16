"""
Automated Testing Framework for ARC-AGI Solutions
Tests solutions against train/test/arc-gen examples and calculates scores
"""
import json
import os
import importlib.util
import sys
import traceback
import numpy as np
from typing import Dict, List, Tuple

class TestRunner:
    def __init__(self, data_dir: str, solvers_dir: str):
        self.data_dir = data_dir
        self.solvers_dir = solvers_dir
        
    def load_task(self, task_num: int) -> Dict:
        """Load task data from JSON file"""
        with open(f"{self.data_dir}/task{task_num:03d}.json", 'r') as f:
            return json.load(f)
    
    def load_solver(self, task_num: int):
        """Load solver function from Python file"""
        solver_path = f"{self.solvers_dir}/task{task_num:03d}.py"
        if not os.path.exists(solver_path):
            return None
            
        spec = importlib.util.spec_from_file_location(f"task{task_num:03d}", solver_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, 'p'):
            return module.p
        return None
    
    def test_solver(self, task_num: int) -> Dict:
        """Test a single solver against all examples"""
        try:
            task_data = self.load_task(task_num)
            solver = self.load_solver(task_num)
            
            if not solver:
                return {"error": "Solver not found", "score": 0.001}
            
            results = {
                "train": self.test_examples(solver, task_data.get("train", [])),
                "test": self.test_examples(solver, task_data.get("test", [])),
                "arc-gen": self.test_examples(solver, task_data.get("arc-gen", []))
            }
            
            total_correct = sum(r["correct"] for r in results.values())
            total_examples = sum(r["total"] for r in results.values())
            
            # Calculate score
            solver_path = f"{self.solvers_dir}/task{task_num:03d}.py"
            file_size = os.path.getsize(solver_path) if os.path.exists(solver_path) else 9999
            
            if total_correct == total_examples:
                score = max(1, 2500 - file_size)
            else:
                score = 0.001
            
            return {
                "task": task_num,
                "score": score,
                "file_size": file_size,
                "correct": total_correct,
                "total": total_examples,
                "results": results
            }
            
        except Exception as e:
            return {
                "task": task_num,
                "error": str(e),
                "score": 0.001
            }
    
    def test_examples(self, solver, examples: List[Dict]) -> Dict:
        """Test solver against a list of examples"""
        correct = 0
        total = len(examples)
        errors = []
        
        for i, example in enumerate(examples):
            try:
                input_grid = example["input"]
                expected_output = example["output"]
                
                # Run solver
                actual_output = solver([row[:] for row in input_grid])  # Deep copy
                
                # Compare outputs
                if np.array_equal(np.array(actual_output), np.array(expected_output)):
                    correct += 1
                else:
                    errors.append(f"Example {i}: Output mismatch")
                    
            except Exception as e:
                errors.append(f"Example {i}: {str(e)}")
        
        return {
            "correct": correct,
            "total": total,
            "errors": errors
        }
    
    def test_all_tasks(self, start_task: int = 1, end_task: int = 400) -> Dict:
        """Test all tasks in range"""
        results = []
        total_score = 0
        
        for task_num in range(start_task, end_task + 1):
            print(f"Testing task {task_num:03d}...", end=" ")
            result = self.test_solver(task_num)
            results.append(result)
            total_score += result["score"]
            
            if "error" in result:
                print(f"ERROR: {result['error']}")
            else:
                print(f"Score: {result['score']:.3f} ({result['correct']}/{result['total']})")
        
        summary = {
            "total_score": total_score,
            "tasks_tested": len(results),
            "tasks_correct": sum(1 for r in results if r["score"] > 1),
            "average_score": total_score / len(results) if results else 0,
            "results": results
        }
        
        return summary
    
    def generate_report(self, results: Dict, output_file: str = "test_report.json"):
        """Generate detailed test report"""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n=== TEST SUMMARY ===")
        print(f"Total Score: {results['total_score']:.3f}")
        print(f"Tasks Correct: {results['tasks_correct']}/{results['tasks_tested']}")
        print(f"Average Score: {results['average_score']:.3f}")
        print(f"Report saved to: {output_file}")

if __name__ == "__main__":
    runner = TestRunner("data", "solvers")
    
    # Test first 10 tasks as example
    results = runner.test_all_tasks(1, 10)
    runner.generate_report(results, "sample_test_report.json")
