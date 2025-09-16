"""
Smart Solver Generator - Analyzes each task individually and creates custom solutions
Uses pattern recognition to generate highly optimized, task-specific solvers
"""
import json
import os
import numpy as np
from typing import Dict, List, Tuple

class SmartSolverGenerator:
    def __init__(self, data_dir: str, solvers_dir: str):
        self.data_dir = data_dir
        self.solvers_dir = solvers_dir
        os.makedirs(solvers_dir, exist_ok=True)
    
    def load_task(self, task_num: int) -> Dict:
        """Load task data"""
        with open(f"{self.data_dir}/task{task_num:03d}.json", 'r') as f:
            return json.load(f)
    
    def analyze_task_pattern(self, task_num: int) -> Tuple[str, str]:
        """Analyze task and return pattern type and optimized solver code"""
        task_data = self.load_task(task_num)
        
        if not task_data['train']:
            return "no_examples", "def p(g):return g"
        
        # Analyze first training example
        example = task_data['train'][0]
        inp = np.array(example['input'])
        out = np.array(example['output'])
        
        # Try to detect the exact pattern
        pattern, solver = self.detect_and_solve(inp, out, task_data)
        
        # Validate solver on all training examples
        if self.validate_solver(solver, task_data):
            return pattern, solver
        else:
            return "validation_failed", f"def p(g):return g  # TODO: Manual analysis for task {task_num}"
    
    def detect_and_solve(self, inp: np.ndarray, out: np.ndarray, task_data: Dict) -> Tuple[str, str]:
        """Detect pattern and generate solver"""
        
        # Identity transformation
        if np.array_equal(inp, out):
            return "identity", "def p(g):return g"
        
        # Same size transformations
        if inp.shape == out.shape:
            return self.analyze_same_size_transform(inp, out)
        
        # 3x3 tiling (input appears 9 times in 3x3 grid)
        if out.shape == (inp.shape[0] * 3, inp.shape[1] * 3):
            return self.analyze_3x3_pattern(inp, out)
        
        # 2x scaling
        if out.shape == (inp.shape[0] * 2, inp.shape[1] * 2):
            return self.analyze_2x_scaling(inp, out)
        
        # Contraction patterns
        if out.size < inp.size:
            return self.analyze_contraction(inp, out)
        
        # Other expansion patterns
        if out.size > inp.size:
            return self.analyze_expansion(inp, out)
        
        return "complex", f"def p(g):return g  # Complex pattern detected"
    
    def analyze_same_size_transform(self, inp: np.ndarray, out: np.ndarray) -> Tuple[str, str]:
        """Analyze same-size transformations"""
        
        # Rotations
        if np.array_equal(out, np.rot90(inp, 1)):
            return "rot90", "def p(g):import numpy as n;return n.rot90(n.array(g)).tolist()"
        if np.array_equal(out, np.rot90(inp, 2)):
            return "rot180", "def p(g):import numpy as n;return n.rot90(n.array(g),2).tolist()"
        if np.array_equal(out, np.rot90(inp, 3)):
            return "rot270", "def p(g):import numpy as n;return n.rot90(n.array(g),3).tolist()"
        
        # Flips
        if np.array_equal(out, np.flipud(inp)):
            return "flipud", "def p(g):import numpy as n;return n.flipud(n.array(g)).tolist()"
        if np.array_equal(out, np.fliplr(inp)):
            return "fliplr", "def p(g):import numpy as n;return n.fliplr(n.array(g)).tolist()"
        
        # Transpose
        if np.array_equal(out, inp.T):
            return "transpose", "def p(g):import numpy as n;return n.array(g).T.tolist()"
        
        # Color transformations
        if self.is_color_inversion(inp, out):
            return "color_invert", "def p(g):return[[1-c for c in r]for r in g]"
        
        # Color mapping (0->1, 1->0, etc.)
        color_map = self.detect_color_mapping(inp, out)
        if color_map:
            return "color_map", self.generate_color_map_solver(color_map)
        
        return "same_size_complex", "def p(g):return g  # Same size complex"
    
    def analyze_3x3_pattern(self, inp: np.ndarray, out: np.ndarray) -> Tuple[str, str]:
        """Analyze 3x3 tiling patterns"""
        h, w = inp.shape
        
        # Check if it's simple 3x3 tiling
        is_simple_tile = True
        for i in range(3):
            for j in range(3):
                tile = out[i*h:(i+1)*h, j*w:(j+1)*w]
                if not np.array_equal(tile, inp):
                    is_simple_tile = False
                    break
            if not is_simple_tile:
                break
        
        if is_simple_tile:
            return "3x3_tile", """def p(g):
 import numpy as n
 g=n.array(g)
 h,w=g.shape
 r=n.zeros((h*3,w*3),int)
 for i in range(3):
  for j in range(3):r[i*h:(i+1)*h,j*w:(j+1)*w]=g
 return r.tolist()"""
        
        # Check for 3x3 with modifications (like adding borders)
        return self.analyze_3x3_with_modifications(inp, out)
    
    def analyze_3x3_with_modifications(self, inp: np.ndarray, out: np.ndarray) -> Tuple[str, str]:
        """Analyze 3x3 patterns with modifications like borders"""
        h, w = inp.shape
        
        # Check if there are 0-filled regions that could be borders/shadows
        zero_positions = []
        for i in range(3):
            for j in range(3):
                tile_region = out[i*h:(i+1)*h, j*w:(j+1)*w]
                if np.all(tile_region == 0):
                    zero_positions.append((i, j))
                elif not np.array_equal(tile_region, inp):
                    # Check if it's input with some modifications
                    pass
        
        # Pattern: 3x3 with some tiles replaced by zeros
        if len(zero_positions) > 0:
            return "3x3_selective", self.generate_3x3_selective_solver(zero_positions)
        
        return "3x3_complex", "def p(g):return g  # 3x3 complex pattern"
    
    def generate_3x3_selective_solver(self, zero_positions: List[Tuple[int, int]]) -> str:
        """Generate solver for 3x3 pattern with selective zero regions"""
        zero_coords = str(zero_positions)
        return f"""def p(g):
 import numpy as n
 g=n.array(g)
 h,w=g.shape
 r=n.zeros((h*3,w*3),int)
 zeros={zero_coords}
 for i in range(3):
  for j in range(3):
   if (i,j) not in zeros:r[i*h:(i+1)*h,j*w:(j+1)*w]=g
 return r.tolist()"""
    
    def analyze_2x_scaling(self, inp: np.ndarray, out: np.ndarray) -> Tuple[str, str]:
        """Analyze 2x scaling patterns"""
        # Simple 2x nearest neighbor scaling
        scaled = np.repeat(np.repeat(inp, 2, axis=0), 2, axis=1)
        if np.array_equal(out, scaled):
            return "2x_scale", "def p(g):import numpy as n;g=n.array(g);return n.repeat(n.repeat(g,2,0),2,1).tolist()"
        
        return "2x_complex", "def p(g):return g  # 2x complex scaling"
    
    def analyze_contraction(self, inp: np.ndarray, out: np.ndarray) -> Tuple[str, str]:
        """Analyze contraction patterns"""
        
        # Every other element
        if np.array_equal(out, inp[::2, ::2]):
            return "subsample_2x", "def p(g):return[r[::2]for r in g[::2]]"
        
        # Center region
        if inp.shape[0] > 2 and inp.shape[1] > 2:
            center = inp[1:-1, 1:-1]
            if np.array_equal(out, center):
                return "center_crop", "def p(g):return[r[1:-1]for r in g[1:-1]]"
        
        return "contraction_complex", "def p(g):return g  # Complex contraction"
    
    def analyze_expansion(self, inp: np.ndarray, out: np.ndarray) -> Tuple[str, str]:
        """Analyze expansion patterns"""
        
        # Add border of zeros
        if out.shape == (inp.shape[0] + 2, inp.shape[1] + 2):
            inner = out[1:-1, 1:-1]
            if np.array_equal(inner, inp):
                return "add_border", "def p(g):h,w=len(g),len(g[0]);r=[[0]*(w+2)for _ in range(h+2)];[r[i+1].__setitem__(slice(1,w+1),g[i])for i in range(h)];return r"
        
        return "expansion_complex", "def p(g):return g  # Complex expansion"
    
    def is_color_inversion(self, inp: np.ndarray, out: np.ndarray) -> bool:
        """Check if output is color inversion of input (0->1, 1->0)"""
        unique_inp = set(inp.flatten())
        unique_out = set(out.flatten())
        
        if unique_inp == {0, 1} and unique_out == {0, 1}:
            return np.array_equal(out, 1 - inp)
        
        return False
    
    def detect_color_mapping(self, inp: np.ndarray, out: np.ndarray) -> Dict:
        """Detect color mapping pattern"""
        if inp.shape != out.shape:
            return None
        
        mapping = {}
        for i in range(inp.shape[0]):
            for j in range(inp.shape[1]):
                inp_color = inp[i, j]
                out_color = out[i, j]
                
                if inp_color in mapping:
                    if mapping[inp_color] != out_color:
                        return None  # Inconsistent mapping
                else:
                    mapping[inp_color] = out_color
        
        return mapping if len(mapping) <= 10 else None  # Max 10 colors
    
    def generate_color_map_solver(self, color_map: Dict) -> str:
        """Generate solver for color mapping"""
        map_str = str(color_map)
        return f"def p(g):m={map_str};return[[m.get(c,c)for c in r]for r in g]"
    
    def validate_solver(self, solver_code: str, task_data: Dict) -> bool:
        """Validate solver against all training examples"""
        try:
            # Create function
            exec(solver_code, globals())
            solver_func = globals()['p']
            
            # Test on all training examples
            for example in task_data['train']:
                inp = [row[:] for row in example['input']]  # Deep copy
                expected = example['output']
                
                result = solver_func(inp)
                if not np.array_equal(np.array(result), np.array(expected)):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def generate_all_smart_solvers(self, start_task: int = 1, end_task: int = 400) -> Dict:
        """Generate smart solvers for all tasks"""
        results = {
            'successful': 0,
            'failed': 0,
            'patterns': {},
            'total_estimated_score': 0
        }
        
        for task_num in range(start_task, end_task + 1):
            print(f"Analyzing task{task_num:03d}...", end=" ")
            
            pattern, solver_code = self.analyze_task_pattern(task_num)
            
            # Write solver
            with open(f"{self.solvers_dir}/task{task_num:03d}.py", 'w') as f:
                f.write(solver_code)
            
            # Track results
            if "TODO" in solver_code or "Complex" in solver_code:
                results['failed'] += 1
                estimated_score = 1000  # Conservative estimate for manual solutions
            else:
                results['successful'] += 1
                # Estimate score based on code length
                code_length = len(solver_code.encode('utf-8'))
                estimated_score = max(1, 2500 - code_length)
            
            results['total_estimated_score'] += estimated_score
            
            # Track patterns
            if pattern not in results['patterns']:
                results['patterns'][pattern] = 0
            results['patterns'][pattern] += 1
            
            print(f"{pattern} (est. score: {estimated_score})")
        
        return results

if __name__ == "__main__":
    generator = SmartSolverGenerator("data", "solvers")
    
    print("🧠 Generating smart solvers for all 400 tasks...")
    results = generator.generate_all_smart_solvers()
    
    print(f"\n📊 Smart Generation Results:")
    print(f"✅ Successful: {results['successful']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"🏆 Total Estimated Score: {results['total_estimated_score']:,}")
    
    print(f"\n📈 Pattern Distribution:")
    for pattern, count in sorted(results['patterns'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {pattern}: {count}")
    
    # Competitive analysis
    if results['total_estimated_score'] > 950000:
        print("🎯 CHAMPIONSHIP POTENTIAL!")
    elif results['total_estimated_score'] > 900000:
        print("🎯 TOP 3 POTENTIAL!")
    else:
        print("🎯 COMPETITIVE POSITION")
