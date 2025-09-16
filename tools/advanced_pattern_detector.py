"""
Advanced Pattern Detector - Detects complex ARC-AGI transformation patterns
Analyzes multiple examples to find logical rules and generate working solvers
"""
import json
import numpy as np
from typing import Dict, List, Tuple, Any
from collections import Counter
import itertools

class AdvancedPatternDetector:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
    
    def load_task(self, task_num: int) -> Dict:
        """Load task data"""
        with open(f"{self.data_dir}/task{task_num:03d}.json", 'r') as f:
            return json.load(f)
    
    def analyze_task_deeply(self, task_num: int) -> Dict:
        """Deep analysis of a task to find the actual transformation rule"""
        task_data = self.load_task(task_num)
        
        if not task_data['train']:
            return {"pattern": "no_examples", "solver": "def p(g):return g"}
        
        # Analyze all training examples
        examples = []
        for ex in task_data['train']:
            inp = np.array(ex['input'])
            out = np.array(ex['output'])
            examples.append((inp, out))
        
        # Try different pattern detection strategies
        patterns = [
            self.detect_object_manipulation,
            self.detect_color_rules,
            self.detect_spatial_rules,
            self.detect_counting_rules,
            self.detect_symmetry_rules,
            self.detect_fill_rules,
            self.detect_shape_rules,
            self.detect_grid_rules
        ]
        
        for pattern_detector in patterns:
            result = pattern_detector(examples)
            if result and self.validate_pattern(result, examples):
                return {
                    "task": task_num,
                    "pattern": result["name"],
                    "solver": result["solver"],
                    "confidence": result.get("confidence", 0.5)
                }
        
        return {
            "task": task_num,
            "pattern": "unsolved",
            "solver": f"def p(g):return g  # TODO: Manual analysis needed for task {task_num}",
            "confidence": 0.0
        }
    
    def detect_object_manipulation(self, examples: List[Tuple[np.ndarray, np.ndarray]]) -> Dict:
        """Detect object-based transformations (move, copy, remove objects)"""
        if not examples:
            return None
        
        inp, out = examples[0]
        
        # Check if objects are being moved/copied
        if self.has_object_movement(inp, out):
            return {
                "name": "object_movement",
                "solver": self.generate_object_movement_solver(examples),
                "confidence": 0.7
            }
        
        return None
    
    def detect_color_rules(self, examples: List[Tuple[np.ndarray, np.ndarray]]) -> Dict:
        """Detect color-based transformation rules"""
        if not examples:
            return None
        
        # Check for consistent color mappings across all examples
        color_mappings = []
        for inp, out in examples:
            if inp.shape != out.shape:
                continue
            
            mapping = {}
            for i in range(inp.shape[0]):
                for j in range(inp.shape[1]):
                    inp_color = inp[i, j]
                    out_color = out[i, j]
                    
                    if inp_color in mapping:
                        if mapping[inp_color] != out_color:
                            mapping = None
                            break
                    else:
                        mapping[inp_color] = out_color
                if mapping is None:
                    break
            
            if mapping:
                color_mappings.append(mapping)
        
        # Check if all examples have the same color mapping
        if len(color_mappings) == len(examples) and len(set(str(m) for m in color_mappings)) == 1:
            mapping = color_mappings[0]
            return {
                "name": "color_mapping",
                "solver": f"def p(g):m={mapping};return[[m.get(c,c)for c in r]for r in g]",
                "confidence": 0.9
            }
        
        return None
    
    def detect_spatial_rules(self, examples: List[Tuple[np.ndarray, np.ndarray]]) -> Dict:
        """Detect spatial transformation rules"""
        if not examples:
            return None
        
        inp, out = examples[0]
        
        # Check for rotations
        for k in [1, 2, 3]:
            if np.array_equal(out, np.rot90(inp, k)):
                # Verify on other examples
                if all(np.array_equal(o, np.rot90(i, k)) for i, o in examples[1:]):
                    return {
                        "name": f"rotation_{k*90}",
                        "solver": f"def p(g):import numpy as n;return n.rot90(n.array(g),{k}).tolist()",
                        "confidence": 0.95
                    }
        
        # Check for flips
        if np.array_equal(out, np.flipud(inp)):
            if all(np.array_equal(o, np.flipud(i)) for i, o in examples[1:]):
                return {
                    "name": "flip_vertical",
                    "solver": "def p(g):import numpy as n;return n.flipud(n.array(g)).tolist()",
                    "confidence": 0.95
                }
        
        if np.array_equal(out, np.fliplr(inp)):
            if all(np.array_equal(o, np.fliplr(i)) for i, o in examples[1:]):
                return {
                    "name": "flip_horizontal",
                    "solver": "def p(g):import numpy as n;return n.fliplr(n.array(g)).tolist()",
                    "confidence": 0.95
                }
        
        return None
    
    def detect_counting_rules(self, examples: List[Tuple[np.ndarray, np.ndarray]]) -> Dict:
        """Detect rules based on counting colors or patterns"""
        if not examples:
            return None
        
        # Check if output is based on counting colors in input
        for inp, out in examples:
            inp_counts = Counter(inp.flatten())
            out_unique = set(out.flatten())
            
            # Simple case: output color corresponds to most frequent input color
            if len(out_unique) == 1:
                most_common_color = inp_counts.most_common(1)[0][0]
                if list(out_unique)[0] == most_common_color:
                    # Verify pattern
                    if all(list(set(o.flatten()))[0] == Counter(i.flatten()).most_common(1)[0][0] 
                           for i, o in examples):
                        return {
                            "name": "most_frequent_color",
                            "solver": "def p(g):from collections import Counter;c=Counter([c for r in g for c in r]).most_common(1)[0][0];return[[c]*len(g[0])]*len(g)",
                            "confidence": 0.8
                        }
        
        return None
    
    def detect_symmetry_rules(self, examples: List[Tuple[np.ndarray, np.ndarray]]) -> Dict:
        """Detect symmetry-based transformations"""
        if not examples:
            return None
        
        inp, out = examples[0]
        
        # Check if output is symmetric version of input
        if np.array_equal(out, out[::-1]):  # Vertically symmetric
            return {
                "name": "make_symmetric_vertical",
                "solver": "def p(g):import numpy as n;g=n.array(g);return((g+g[::-1])//2).tolist()",
                "confidence": 0.6
            }
        
        return None
    
    def detect_fill_rules(self, examples: List[Tuple[np.ndarray, np.ndarray]]) -> Dict:
        """Detect fill-based transformations (flood fill, etc.)"""
        if not examples:
            return None
        
        # Check for simple fill patterns
        inp, out = examples[0]
        
        # Check if all zeros become a specific color
        if inp.shape == out.shape:
            zero_positions = (inp == 0)
            if np.any(zero_positions):
                fill_colors = out[zero_positions]
                if len(set(fill_colors)) == 1:
                    fill_color = fill_colors[0]
                    # Check if non-zero positions remain unchanged
                    if np.array_equal(inp[~zero_positions], out[~zero_positions]):
                        return {
                            "name": "fill_zeros",
                            "solver": f"def p(g):return[[{fill_color} if c==0 else c for c in r]for r in g]",
                            "confidence": 0.7
                        }
        
        return None
    
    def detect_shape_rules(self, examples: List[Tuple[np.ndarray, np.ndarray]]) -> Dict:
        """Detect shape-based transformations"""
        if not examples:
            return None
        
        # Check for scaling patterns
        inp, out = examples[0]
        
        if out.shape == (inp.shape[0] * 2, inp.shape[1] * 2):
            # Check if it's nearest neighbor scaling
            scaled = np.repeat(np.repeat(inp, 2, axis=0), 2, axis=1)
            if np.array_equal(out, scaled):
                return {
                    "name": "scale_2x",
                    "solver": "def p(g):import numpy as n;g=n.array(g);return n.repeat(n.repeat(g,2,0),2,1).tolist()",
                    "confidence": 0.9
                }
        
        # Check for 3x3 tiling
        if out.shape == (inp.shape[0] * 3, inp.shape[1] * 3):
            h, w = inp.shape
            is_tiled = True
            for i in range(3):
                for j in range(3):
                    tile = out[i*h:(i+1)*h, j*w:(j+1)*w]
                    if not np.array_equal(tile, inp):
                        is_tiled = False
                        break
                if not is_tiled:
                    break
            
            if is_tiled:
                return {
                    "name": "tile_3x3",
                    "solver": """def p(g):
 import numpy as n
 g=n.array(g)
 h,w=g.shape
 r=n.zeros((h*3,w*3),int)
 for i in range(3):
  for j in range(3):r[i*h:(i+1)*h,j*w:(j+1)*w]=g
 return r.tolist()""",
                    "confidence": 0.95
                }
        
        return None
    
    def detect_grid_rules(self, examples: List[Tuple[np.ndarray, np.ndarray]]) -> Dict:
        """Detect grid-based transformation rules"""
        if not examples:
            return None
        
        # Check for border addition
        inp, out = examples[0]
        
        if out.shape == (inp.shape[0] + 2, inp.shape[1] + 2):
            # Check if input is in the center with border
            inner = out[1:-1, 1:-1]
            if np.array_equal(inner, inp):
                border_color = out[0, 0]  # Assume uniform border
                return {
                    "name": "add_border",
                    "solver": f"def p(g):h,w=len(g),len(g[0]);r=[[{border_color}]*(w+2)for _ in range(h+2)];[r[i+1].__setitem__(slice(1,w+1),g[i])for i in range(h)];return r",
                    "confidence": 0.8
                }
        
        return None
    
    def has_object_movement(self, inp: np.ndarray, out: np.ndarray) -> bool:
        """Check if objects have moved between input and output"""
        if inp.shape != out.shape:
            return False
        
        # Simple heuristic: same colors but different positions
        inp_colors = Counter(inp.flatten())
        out_colors = Counter(out.flatten())
        
        return inp_colors == out_colors and not np.array_equal(inp, out)
    
    def generate_object_movement_solver(self, examples: List[Tuple[np.ndarray, np.ndarray]]) -> str:
        """Generate solver for object movement (placeholder)"""
        return "def p(g):return g  # TODO: Object movement pattern detected"
    
    def validate_pattern(self, pattern_result: Dict, examples: List[Tuple[np.ndarray, np.ndarray]]) -> bool:
        """Validate that the detected pattern works on all examples"""
        if not pattern_result or "solver" not in pattern_result:
            return False
        
        try:
            # Execute the solver code
            exec(pattern_result["solver"], globals())
            solver_func = globals()['p']
            
            # Test on all examples
            for inp, expected_out in examples:
                inp_list = inp.tolist()
                result = solver_func(inp_list)
                
                if not np.array_equal(np.array(result), expected_out):
                    return False
            
            return True
            
        except Exception:
            return False

def analyze_failing_tasks(start_task: int = 1, end_task: int = 50):
    """Analyze tasks that are currently failing"""
    detector = AdvancedPatternDetector("data")
    
    successful = 0
    total = 0
    
    for task_num in range(start_task, end_task + 1):
        total += 1
        print(f"Analyzing task {task_num:03d}...", end=" ")
        
        result = detector.analyze_task_deeply(task_num)
        
        if result["pattern"] != "unsolved":
            successful += 1
            print(f"✅ {result['pattern']} (confidence: {result['confidence']:.2f})")
        else:
            print("❌ Unsolved")
    
    print(f"\nResults: {successful}/{total} tasks solved ({successful/total*100:.1f}%)")

if __name__ == "__main__":
    analyze_failing_tasks(1, 100)
