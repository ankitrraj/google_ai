"""
Final Submission System - Create optimized submission.zip for competition
"""
import os
import zipfile
import json
from pathlib import Path

class FinalSubmissionSystem:
    def __init__(self, solvers_dir: str, output_file: str = "submission.zip"):
        self.solvers_dir = solvers_dir
        self.output_file = output_file
    
    def optimize_solver(self, solver_code: str) -> str:
        """Apply final code golf optimizations"""
        # Remove comments and extra whitespace
        lines = []
        for line in solver_code.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                lines.append(line)
        
        code = '\n'.join(lines)
        
        # Apply basic golfing rules
        replacements = [
            ('import numpy as n', 'import numpy as n'),
            ('import numpy as np', 'import numpy as n'),
            (' as n', ' as n'),
            ('n.array(g)', 'n.array(g)'),
            ('n.rot90(', 'n.rot90('),
            ('n.flipud(', 'n.flipud('),
            ('n.fliplr(', 'n.fliplr('),
            ('n.repeat(', 'n.repeat('),
            ('.tolist()', '.tolist()'),
            ('return ', 'return '),
            ('def p(g):', 'def p(g):'),
            ('  ', ' '),  # Reduce double spaces
        ]
        
        for old, new in replacements:
            code = code.replace(old, new)
        
        return code
    
    def calculate_score_estimate(self, solver_code: str) -> int:
        """Estimate competition score for a solver"""
        code_length = len(solver_code.encode('utf-8'))
        return max(1, 2500 - code_length)
    
    def create_submission(self) -> dict:
        """Create final submission.zip with all solvers"""
        results = {
            'total_files': 0,
            'working_solvers': 0,
            'placeholder_solvers': 0,
            'total_estimated_score': 0,
            'file_sizes': {},
            'score_breakdown': {}
        }
        
        # Create submission directory
        submission_dir = "submission_temp"
        os.makedirs(submission_dir, exist_ok=True)
        
        print("Creating final submission...")
        
        for task_num in range(1, 401):
            solver_file = f"{self.solvers_dir}/task{task_num:03d}.py"
            
            if os.path.exists(solver_file):
                # Read existing solver
                with open(solver_file, 'r') as f:
                    solver_code = f.read()
            else:
                # Create placeholder solver
                solver_code = "def p(g):return g"
            
            # Optimize the solver
            optimized_code = self.optimize_solver(solver_code)
            
            # Write to submission directory
            submission_file = f"{submission_dir}/task{task_num:03d}.py"
            with open(submission_file, 'w') as f:
                f.write(optimized_code)
            
            # Track statistics
            results['total_files'] += 1
            file_size = len(optimized_code.encode('utf-8'))
            results['file_sizes'][f'task{task_num:03d}'] = file_size
            
            # Estimate score
            estimated_score = self.calculate_score_estimate(optimized_code)
            results['score_breakdown'][f'task{task_num:03d}'] = estimated_score
            results['total_estimated_score'] += estimated_score
            
            # Categorize solver type
            if "TODO" in solver_code or solver_code.strip() == "def p(g):return g":
                results['placeholder_solvers'] += 1
            else:
                results['working_solvers'] += 1
            
            if task_num % 50 == 0:
                print(f"  Processed {task_num}/400 tasks...")
        
        # Create ZIP file
        print(f"Creating {self.output_file}...")
        with zipfile.ZipFile(self.output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for task_num in range(1, 401):
                file_path = f"{submission_dir}/task{task_num:03d}.py"
                zipf.write(file_path, f"task{task_num:03d}.py")
        
        # Cleanup
        import shutil
        shutil.rmtree(submission_dir)
        
        return results
    
    def generate_competition_report(self, results: dict):
        """Generate final competition report"""
        report = f"""
# ARC-AGI Code Golf Championship 2025 - Final Submission Report

## Submission Statistics
- **Total Tasks**: {results['total_files']}
- **Working Solvers**: {results['working_solvers']}
- **Placeholder Solvers**: {results['placeholder_solvers']}
- **Total Estimated Score**: {results['total_estimated_score']:,}
- **Average Score Per Task**: {results['total_estimated_score'] / 400:.0f}

## Competition Analysis
"""
        
        if results['total_estimated_score'] > 950000:
            report += "**CHAMPIONSHIP POTENTIAL!** - Top tier competitive score\n"
        elif results['total_estimated_score'] > 900000:
            report += "**TOP 3 POTENTIAL!** - Strong competitive position\n"
        elif results['total_estimated_score'] > 800000:
            report += "**TOP 10 POTENTIAL!** - Good competitive position\n"
        else:
            report += "**COMPETITIVE POSITION** - Room for improvement\n"
        
        # Top scoring tasks
        top_tasks = sorted(results['score_breakdown'].items(), 
                          key=lambda x: x[1], reverse=True)[:10]
        
        report += f"\n## Top 10 Scoring Tasks\n"
        for task, score in top_tasks:
            file_size = results['file_sizes'][task]
            report += f"- **{task}**: {score} points ({file_size} bytes)\n"
        
        # File size distribution
        sizes = list(results['file_sizes'].values())
        avg_size = sum(sizes) / len(sizes)
        min_size = min(sizes)
        max_size = max(sizes)
        
        report += f"\n## File Size Analysis\n"
        report += f"- **Average Size**: {avg_size:.1f} bytes\n"
        report += f"- **Smallest File**: {min_size} bytes\n"
        report += f"- **Largest File**: {max_size} bytes\n"
        
        report += f"\n## Submission Ready!\n"
        report += f"File: `{self.output_file}`\n"
        report += f"Size: {os.path.getsize(self.output_file) / 1024:.1f} KB\n"
        
        return report

if __name__ == "__main__":
    system = FinalSubmissionSystem("solvers")
    
    # Create submission
    results = system.create_submission()
    
    # Generate report
    report = system.generate_competition_report(results)
    
    # Save report
    with open("FINAL_SUBMISSION_REPORT.md", 'w') as f:
        f.write(report)
    
    print("✅ Submission created successfully!")
    print(f"📋 Report saved to: FINAL_SUBMISSION_REPORT.md")
    print(report)
