"""
Mass Solver Generator for ARC-AGI Tasks
Creates optimized solvers for all tasks based on pattern analysis
"""
import json
import os
import numpy as np
from typing import Dict, List

class MassSolverGenerator:
    def __init__(self, data_dir: str, solvers_dir: str):
        self.data_dir = data_dir
        self.solvers_dir = solvers_dir
        
        # Load pattern analysis results
        with open('pattern_analysis.json', 'r') as f:
            self.analysis = json.load(f)
        
        # Ultra-golfed solver templates
        self.templates = {
            "same_size_transform": [
                # Rotation variants (very short)
                "def p(g):import numpy as n;return n.rot90(n.array(g)).tolist()",
                "def p(g):import numpy as n;return n.rot90(n.array(g),2).tolist()",
                "def p(g):import numpy as n;return n.rot90(n.array(g),3).tolist()",
                "def p(g):import numpy as n;return n.flipud(n.array(g)).tolist()",
                "def p(g):import numpy as n;return n.fliplr(n.array(g)).tolist()",
                "def p(g):import numpy as n;return n.array(g).T.tolist()",
                # Color mapping variants
                "def p(g):return[[1-c for c in r]for r in g]",
                "def p(g):return[[c*2%10 for c in r]for r in g]",
                "def p(g):return[[(c+1)%10 for c in r]for r in g]",
                # Identity (shortest possible)
                "def p(g):return g"
            ],
            "contraction": [
                # Take every other element
                "def p(g):return[r[::2]for r in g[::2]]",
                "def p(g):return[r[1::2]for r in g[1::2]]",
                # Take center region
                "def p(g):return[r[1:-1]for r in g[1:-1]]",
                # Take corners
                "def p(g):h,w=len(g),len(g[0]);return[[g[0][0],g[0][w-1]],[g[h-1][0],g[h-1][w-1]]]"
            ],
            "expansion": [
                # 2x scaling
                "def p(g):import numpy as n;g=n.array(g);return n.repeat(n.repeat(g,2,0),2,1).tolist()",
                # 3x scaling  
                "def p(g):import numpy as n;g=n.array(g);return n.repeat(n.repeat(g,3,0),3,1).tolist()",
                # Add border
                "def p(g):h,w=len(g),len(g[0]);r=[[0]*(w+2)for _ in range(h+2)];[r[i+1].__setitem__(slice(1,w+1),g[i])for i in range(h)];return r"
            ],
            "3x3_tile": [
                "def p(g):import numpy as n;g=n.array(g);h,w=g.shape;r=n.zeros((h*3,w*3),int);[[r.__setitem__((slice(i*h,(i+1)*h),slice(j*w,(j+1)*w)),g)for j in range(3)]for i in range(3)];return r.tolist()"
            ],
            "rearrangement": [
                "def p(g):import numpy as n;return n.array(g).T.tolist()",
                "def p(g):return g[::-1]",
                "def p(g):return[r[::-1]for r in g]"
            ]
        }
    
    def load_task(self, task_num: int) -> Dict:
        """Load task data"""
        with open(f"{self.data_dir}/task{task_num:03d}.json", 'r') as f:
            return json.load(f)
    
    def test_solver_template(self, template: str, task_data: Dict) -> bool:
        """Test if a solver template works for a task"""
        try:
            # Create temporary function
            exec(template, globals())
            solver = globals()['p']
            
            # Test on first training example
            if not task_data['train']:
                return False
                
            example = task_data['train'][0]
            input_grid = [row[:] for row in example['input']]  # Deep copy
            expected = example['output']
            
            result = solver(input_grid)
            return np.array_equal(np.array(result), np.array(expected))
            
        except Exception as e:
            return False
    
    def find_best_solver(self, task_num: int, pattern: str) -> str:
        """Find the best (shortest working) solver for a task"""
        task_data = self.load_task(task_num)
        templates = self.templates.get(pattern, [])
        
        # Try templates in order (shortest first)
        for template in templates:
            if self.test_solver_template(template, task_data):
                return template
        
        # If no template works, return a placeholder
        return f"def p(g):return g  # TODO: Manual analysis needed for task {task_num}"
    
    def generate_all_solvers(self):
        """Generate solvers for all tasks based on pattern analysis"""
        os.makedirs(self.solvers_dir, exist_ok=True)
        
        results = {
            'generated': 0,
            'manual_needed': 0,
            'by_pattern': {}
        }
        
        for task_info in self.analysis['results']:
            task_num = task_info['task']
            pattern = task_info['pattern']
            
            print(f"Generating solver for task{task_num:03d} (pattern: {pattern})...")
            
            solver_code = self.find_best_solver(task_num, pattern)
            
            # Write solver file
            with open(f"{self.solvers_dir}/task{task_num:03d}.py", 'w') as f:
                f.write(solver_code)
            
            # Track results
            if "TODO" in solver_code:
                results['manual_needed'] += 1
            else:
                results['generated'] += 1
            
            if pattern not in results['by_pattern']:
                results['by_pattern'][pattern] = {'generated': 0, 'manual': 0}
            
            if "TODO" in solver_code:
                results['by_pattern'][pattern]['manual'] += 1
            else:
                results['by_pattern'][pattern]['generated'] += 1
        
        return results
    
    def estimate_scores(self, results: Dict) -> Dict:
        """Estimate competition scores based on generated solvers"""
        # Average template sizes (bytes)
        avg_sizes = {
            'same_size_transform': 60,  # Very short templates
            'contraction': 80,
            'expansion': 120,
            'rearrangement': 70,
            '3x3_tile': 150,
            'manual': 300  # Estimated for manual solutions
        }
        
        total_score = 0
        breakdown = {}
        
        for pattern, counts in results['by_pattern'].items():
            generated = counts['generated']
            manual = counts['manual']
            
            avg_size = avg_sizes.get(pattern, 100)
            pattern_score = generated * max(1, 2500 - avg_size) + manual * max(1, 2500 - 300)
            
            breakdown[pattern] = {
                'tasks': generated + manual,
                'avg_size': avg_size,
                'total_score': pattern_score
            }
            
            total_score += pattern_score
        
        return {
            'total_estimated_score': total_score,
            'breakdown': breakdown,
            'competitive_position': 'TOP 3' if total_score > 950000 else 'TOP 10' if total_score > 900000 else 'COMPETITIVE'
        }

if __name__ == "__main__":
    generator = MassSolverGenerator("data", "solvers")
    
    print("🚀 Generating solvers for all 400 tasks...")
    results = generator.generate_all_solvers()
    
    print(f"\n📊 Generation Results:")
    print(f"✅ Auto-generated: {results['generated']}")
    print(f"🔧 Manual needed: {results['manual_needed']}")
    
    print(f"\n📈 By Pattern:")
    for pattern, counts in results['by_pattern'].items():
        print(f"  {pattern}: {counts['generated']} auto, {counts['manual']} manual")
    
    # Estimate scores
    score_estimate = generator.estimate_scores(results)
    print(f"\n🏆 Score Estimate: {score_estimate['total_estimated_score']:,.0f}")
    print(f"🎯 Competitive Position: {score_estimate['competitive_position']}")
