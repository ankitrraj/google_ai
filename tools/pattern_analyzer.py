"""
Pattern Analysis Tool for ARC-AGI Tasks
Analyzes transformation patterns across all 400 tasks
"""
import json
import os
from collections import defaultdict
import numpy as np

class PatternAnalyzer:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.patterns = defaultdict(list)
        
    def analyze_task(self, task_num):
        """Analyze a single task and categorize its pattern"""
        with open(f"{self.data_dir}/task{task_num:03d}.json", 'r') as f:
            task = json.load(f)
        
        # Analyze first training example
        if not task['train']:
            return None
            
        inp = np.array(task['train'][0]['input'])
        out = np.array(task['train'][0]['output'])
        
        pattern_type = self.detect_pattern(inp, out)
        return {
            'task': task_num,
            'pattern': pattern_type,
            'input_shape': inp.shape,
            'output_shape': out.shape,
            'size_ratio': out.size / inp.size
        }
    
    def detect_pattern(self, inp, out):
        """Detect the transformation pattern"""
        # Size-based patterns
        if out.shape == (inp.shape[0] * 3, inp.shape[1] * 3):
            return "3x3_tile"
        elif out.shape == inp.shape:
            return "same_size_transform"
        elif out.size > inp.size * 2:
            return "expansion"
        elif out.size < inp.size:
            return "contraction"
        
        # Content-based patterns
        unique_inp = set(inp.flatten())
        unique_out = set(out.flatten())
        
        if unique_inp == unique_out:
            return "rearrangement"
        elif len(unique_out) > len(unique_inp):
            return "color_addition"
        elif len(unique_out) < len(unique_inp):
            return "color_reduction"
        
        return "complex"
    
    def analyze_all_tasks(self):
        """Analyze all 400 tasks"""
        results = []
        for i in range(1, 401):
            try:
                result = self.analyze_task(i)
                if result:
                    results.append(result)
                    self.patterns[result['pattern']].append(i)
            except Exception as e:
                print(f"Error analyzing task {i}: {e}")
        
        return results
    
    def get_pattern_summary(self):
        """Get summary of all patterns found"""
        return {pattern: len(tasks) for pattern, tasks in self.patterns.items()}

if __name__ == "__main__":
    analyzer = PatternAnalyzer("data")
    results = analyzer.analyze_all_tasks()
    summary = analyzer.get_pattern_summary()
    
    print("Pattern Distribution:")
    for pattern, count in sorted(summary.items(), key=lambda x: x[1], reverse=True):
        print(f"{pattern}: {count} tasks")
        
    # Save results
    with open("pattern_analysis.json", 'w') as f:
        json.dump({
            'results': results,
            'summary': summary,
            'patterns': dict(analyzer.patterns)
        }, f, indent=2)
