"""
Individual Task Analyzer - Deep dive into specific tasks
Analyzes the exact transformation pattern for manual solver creation
"""
import json
import numpy as np
from typing import Dict, List, Tuple

class TaskAnalyzer:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
    
    def load_task(self, task_num: int) -> Dict:
        """Load task data"""
        with open(f"{self.data_dir}/task{task_num:03d}.json", 'r') as f:
            return json.load(f)
    
    def analyze_transformation(self, task_num: int) -> Dict:
        """Analyze the exact transformation pattern"""
        task_data = self.load_task(task_num)
        
        if not task_data['train']:
            return {"error": "No training examples"}
        
        analysis = {
            "task": task_num,
            "examples": [],
            "pattern_hypothesis": None,
            "solver_code": None
        }
        
        # Analyze each training example
        for i, example in enumerate(task_data['train'][:3]):  # First 3 examples
            inp = np.array(example['input'])
            out = np.array(example['output'])
            
            example_analysis = {
                "example": i,
                "input_shape": inp.shape,
                "output_shape": out.shape,
                "input_colors": sorted(set(inp.flatten())),
                "output_colors": sorted(set(out.flatten())),
                "transformation_type": self.detect_transformation_type(inp, out),
                "detailed_analysis": self.detailed_analysis(inp, out)
            }
            
            analysis["examples"].append(example_analysis)
        
        # Generate hypothesis based on first example
        if analysis["examples"]:
            analysis["pattern_hypothesis"] = self.generate_hypothesis(analysis["examples"][0])
            analysis["solver_code"] = self.generate_solver_code(task_num, analysis["pattern_hypothesis"])
        
        return analysis
    
    def detect_transformation_type(self, inp: np.ndarray, out: np.ndarray) -> str:
        """Detect specific transformation type"""
        if inp.shape == out.shape:
            if np.array_equal(inp, out):
                return "identity"
            elif np.array_equal(inp, np.rot90(out)):
                return "rotation_90"
            elif np.array_equal(inp, np.rot90(out, 2)):
                return "rotation_180"
            elif np.array_equal(inp, np.rot90(out, 3)):
                return "rotation_270"
            elif np.array_equal(inp, np.flipud(out)):
                return "flip_vertical"
            elif np.array_equal(inp, np.fliplr(out)):
                return "flip_horizontal"
            elif np.array_equal(inp, out.T):
                return "transpose"
            else:
                return "same_size_complex"
        
        # Check for tiling patterns
        if out.shape == (inp.shape[0] * 3, inp.shape[1] * 3):
            return "3x3_tile"
        elif out.shape == (inp.shape[0] * 2, inp.shape[1] * 2):
            return "2x2_tile"
        
        # Check for scaling
        if out.shape[0] == inp.shape[0] * 2 and out.shape[1] == inp.shape[1] * 2:
            return "2x_scale"
        elif out.shape[0] == inp.shape[0] * 3 and out.shape[1] == inp.shape[1] * 3:
            return "3x_scale"
        
        return "complex_transformation"
    
    def detailed_analysis(self, inp: np.ndarray, out: np.ndarray) -> Dict:
        """Detailed analysis of the transformation"""
        return {
            "size_change": f"{inp.shape} -> {out.shape}",
            "color_mapping": self.analyze_color_mapping(inp, out),
            "spatial_pattern": self.analyze_spatial_pattern(inp, out)
        }
    
    def analyze_color_mapping(self, inp: np.ndarray, out: np.ndarray) -> Dict:
        """Analyze how colors are mapped"""
        inp_colors = set(inp.flatten())
        out_colors = set(out.flatten())
        
        return {
            "input_colors": sorted(inp_colors),
            "output_colors": sorted(out_colors),
            "new_colors": sorted(out_colors - inp_colors),
            "removed_colors": sorted(inp_colors - out_colors)
        }
    
    def analyze_spatial_pattern(self, inp: np.ndarray, out: np.ndarray) -> str:
        """Analyze spatial transformation pattern"""
        if inp.shape == out.shape:
            return "same_size"
        elif out.size > inp.size:
            return f"expansion_{out.size // inp.size}x"
        else:
            return f"contraction_{inp.size // out.size}x"
    
    def generate_hypothesis(self, example_analysis: Dict) -> str:
        """Generate transformation hypothesis"""
        trans_type = example_analysis["transformation_type"]
        
        if trans_type == "identity":
            return "Return input unchanged"
        elif trans_type == "rotation_90":
            return "Rotate 90 degrees counterclockwise"
        elif trans_type == "rotation_180":
            return "Rotate 180 degrees"
        elif trans_type == "rotation_270":
            return "Rotate 270 degrees counterclockwise"
        elif trans_type == "flip_vertical":
            return "Flip vertically"
        elif trans_type == "flip_horizontal":
            return "Flip horizontally"
        elif trans_type == "transpose":
            return "Transpose matrix"
        elif trans_type == "3x3_tile":
            return "Tile input in 3x3 pattern"
        elif trans_type == "2x_scale":
            return "Scale up 2x with nearest neighbor"
        else:
            return f"Complex transformation: {trans_type}"
    
    def generate_solver_code(self, task_num: int, hypothesis: str) -> str:
        """Generate optimized solver code based on hypothesis"""
        if "Return input unchanged" in hypothesis:
            return "def p(g):return g"
        elif "Rotate 90 degrees counterclockwise" in hypothesis:
            return "def p(g):import numpy as n;return n.rot90(n.array(g)).tolist()"
        elif "Rotate 180 degrees" in hypothesis:
            return "def p(g):import numpy as n;return n.rot90(n.array(g),2).tolist()"
        elif "Rotate 270 degrees counterclockwise" in hypothesis:
            return "def p(g):import numpy as n;return n.rot90(n.array(g),3).tolist()"
        elif "Flip vertically" in hypothesis:
            return "def p(g):import numpy as n;return n.flipud(n.array(g)).tolist()"
        elif "Flip horizontally" in hypothesis:
            return "def p(g):import numpy as n;return n.fliplr(n.array(g)).tolist()"
        elif "Transpose matrix" in hypothesis:
            return "def p(g):import numpy as n;return n.array(g).T.tolist()"
        elif "Tile input in 3x3 pattern" in hypothesis:
            return """def p(g):
 import numpy as n
 g=n.array(g)
 h,w=g.shape
 r=n.zeros((h*3,w*3),int)
 for i in range(3):
  for j in range(3):r[i*h:(i+1)*h,j*w:(j+1)*w]=g
 return r.tolist()"""
        else:
            return f"def p(g):return g  # TODO: {hypothesis}"

if __name__ == "__main__":
    import sys
    analyzer = TaskAnalyzer("data")
    
    # Get task number from command line argument or default to first few
    if len(sys.argv) > 1:
        task_nums = [int(sys.argv[1])]
    else:
        task_nums = [1, 2, 3, 4, 5]
    
    for task_num in task_nums:
        print(f"\n=== TASK {task_num:03d} ANALYSIS ===")
        analysis = analyzer.analyze_transformation(task_num)
        
        print(f"Pattern Hypothesis: {analysis['pattern_hypothesis']}")
        print(f"Solver Code: {analysis['solver_code']}")
        
        if analysis["examples"]:
            ex = analysis["examples"][0]
            print(f"Transformation: {ex['transformation_type']}")
            print(f"Shape: {ex['input_shape']} -> {ex['output_shape']}")
            print(f"Colors: {ex['input_colors']} -> {ex['output_colors']}")
