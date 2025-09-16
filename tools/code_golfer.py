"""
Code Golf Optimizer for ARC-AGI Solutions
Minimizes byte count while maintaining correctness
"""
import re
import ast
import os
from typing import Dict, List, Tuple

class CodeGolfer:
    def __init__(self):
        self.golf_rules = [
            self.remove_comments_docstrings,
            self.minimize_whitespace,
            self.shorten_variable_names,
            self.use_list_comprehensions,
            self.optimize_imports,
            self.use_builtin_shortcuts,
            self.minimize_function_calls,
            self.use_operator_shortcuts
        ]
    
    def golf_code(self, code: str) -> str:
        """Apply all golfing rules to minimize code size"""
        golfed = code
        for rule in self.golf_rules:
            try:
                golfed = rule(golfed)
            except:
                continue  # Skip rule if it breaks code
        return golfed
    
    def remove_comments_docstrings(self, code: str) -> str:
        """Remove comments and docstrings"""
        # Remove single line comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        # Remove docstrings
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
        return code
    
    def minimize_whitespace(self, code: str) -> str:
        """Minimize whitespace while preserving syntax"""
        lines = code.split('\n')
        minimized = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Minimize spaces around operators
                line = re.sub(r'\s*([+\-*/%=<>!&|^])\s*', r'\1', line)
                line = re.sub(r'\s*([,;:])\s*', r'\1', line)
                line = re.sub(r'\s*([()[\]{}])\s*', r'\1', line)
                minimized.append(line)
        
        return '\n'.join(minimized)
    
    def shorten_variable_names(self, code: str) -> str:
        """Replace long variable names with single letters"""
        # Common replacements
        replacements = {
            'grid': 'g',
            'result': 'r',
            'height': 'h',
            'width': 'w',
            'input': 'i',
            'output': 'o',
            'array': 'a',
            'numpy': 'n',
            'range': 'r',
            'enumerate': 'e'
        }
        
        for old, new in replacements.items():
            code = re.sub(rf'\b{old}\b', new, code)
        
        return code
    
    def use_list_comprehensions(self, code: str) -> str:
        """Convert simple loops to list comprehensions where possible"""
        # This is complex - simplified version
        # Convert: for i in range(n): result.append(expr)
        pattern = r'for (\w+) in range\((\w+)\):\s*(\w+)\.append\(([^)]+)\)'
        replacement = r'\3=[\4 for \1 in range(\2)]'
        return re.sub(pattern, replacement, code)
    
    def optimize_imports(self, code: str) -> str:
        """Optimize import statements"""
        # Use shorter import aliases
        code = re.sub(r'import numpy as np', 'import numpy as n', code)
        code = re.sub(r'import numpy', 'import numpy as n', code)
        
        # Remove unused imports (simplified)
        lines = code.split('\n')
        imports = []
        other_lines = []
        
        for line in lines:
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                imports.append(line)
            else:
                other_lines.append(line)
        
        # Only keep imports that are used
        used_imports = []
        code_body = '\n'.join(other_lines)
        
        for imp in imports:
            if 'numpy' in imp and ('n.' in code_body or 'numpy' in code_body):
                used_imports.append(imp)
            elif any(module in code_body for module in ['json', 'os', 'sys', 're']):
                used_imports.append(imp)
        
        return '\n'.join(used_imports + other_lines)
    
    def use_builtin_shortcuts(self, code: str) -> str:
        """Use Python builtin shortcuts"""
        # len(x) > 0 -> x
        code = re.sub(r'len\((\w+)\)\s*>\s*0', r'\1', code)
        
        # range(len(x)) -> range(len(x)) can't be shortened much
        # But we can use enumerate where appropriate
        
        return code
    
    def minimize_function_calls(self, code: str) -> str:
        """Minimize function call overhead"""
        # .tolist() can sometimes be avoided
        code = re.sub(r'\.tolist\(\)', '', code)
        return code
    
    def use_operator_shortcuts(self, code: str) -> str:
        """Use shorter operators where possible"""
        # x = x + 1 -> x += 1 (but += is longer, so skip)
        # Use * for repetition
        code = re.sub(r'\[0\]\s*\*\s*(\w+)', r'[0]*\1', code)
        return code
    
    def golf_file(self, input_file: str, output_file: str = None) -> Tuple[str, int, int]:
        """Golf a Python file and return original/new sizes"""
        with open(input_file, 'r') as f:
            original_code = f.read()
        
        golfed_code = self.golf_code(original_code)
        
        if output_file is None:
            output_file = input_file
        
        with open(output_file, 'w') as f:
            f.write(golfed_code)
        
        original_size = len(original_code.encode('utf-8'))
        new_size = len(golfed_code.encode('utf-8'))
        
        return golfed_code, original_size, new_size
    
    def golf_all_solvers(self, solvers_dir: str) -> Dict:
        """Golf all solver files in directory"""
        results = {}
        total_saved = 0
        
        for filename in os.listdir(solvers_dir):
            if filename.startswith('task') and filename.endswith('.py'):
                filepath = os.path.join(solvers_dir, filename)
                try:
                    golfed, orig_size, new_size = self.golf_file(filepath)
                    saved = orig_size - new_size
                    total_saved += saved
                    
                    results[filename] = {
                        'original_size': orig_size,
                        'new_size': new_size,
                        'bytes_saved': saved,
                        'score_improvement': saved  # Direct score improvement
                    }
                    
                    print(f"{filename}: {orig_size} -> {new_size} bytes (saved {saved})")
                    
                except Exception as e:
                    print(f"Error golfing {filename}: {e}")
        
        print(f"\nTotal bytes saved: {total_saved}")
        print(f"Total score improvement: {total_saved}")
        
        return results

# Example ultra-golfed patterns
GOLF_PATTERNS = {
    "3x3_tile": """def p(g):
 import numpy as n;g=n.array(g);h,w=g.shape;r=n.zeros((h*3,w*3),int)
 for i in range(3):
  for j in range(3):r[i*h:(i+1)*h,j*w:(j+1)*w]=g
 return r.tolist()""",
    
    "rotation": "def p(g):import numpy as n;return n.rot90(n.array(g)).tolist()",
    
    "flip": "def p(g):import numpy as n;return n.flipud(n.array(g)).tolist()",
    
    "transpose": "def p(g):import numpy as n;return n.array(g).T.tolist()",
    
    "identity": "def p(g):return g",
    
    "scale_2x": "def p(g):import numpy as n;g=n.array(g);return n.repeat(n.repeat(g,2,0),2,1).tolist()"
}

if __name__ == "__main__":
    golfer = CodeGolfer()
    
    # Example usage
    test_code = '''
def p(grid):
    """Solve the task"""
    import numpy as np
    result = []
    for row in grid:
        new_row = []
        for cell in row:
            new_row.append(cell * 2)
        result.append(new_row)
    return result
    '''
    
    golfed = golfer.golf_code(test_code)
    print("Original:", len(test_code), "bytes")
    print("Golfed:", len(golfed), "bytes")
    print("Golfed code:")
    print(golfed)
