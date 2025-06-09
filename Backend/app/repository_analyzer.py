import os
import tempfile
from typing import Dict, List, Tuple
from github import Github
from git import Repo
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from sentence_transformers import SentenceTransformer
import markdown
from bs4 import BeautifulSoup
import re
import ast
import networkx as nx
from collections import defaultdict
import json

class RepositoryAnalyzer:
    def __init__(self, github_token: str, huggingface_token: str):
        self.github = Github(github_token)
        self.huggingface_token = huggingface_token
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize models
        self.code_model = AutoModelForSeq2SeqLM.from_pretrained("Salesforce/codet5-base")
        self.code_tokenizer = AutoTokenizer.from_pretrained("Salesforce/codet5-base")
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        self.code_model.to(self.device)

    def clone_repository(self, repo_url: str) -> Tuple[str, str]:
        """Clone repository to temporary directory and return path and repo name."""
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        temp_dir = tempfile.mkdtemp()
        Repo.clone_from(repo_url, temp_dir)
        return temp_dir, repo_name

    def analyze_code_complexity(self, code: str) -> Dict:
        """Analyze code complexity metrics."""
        try:
            tree = ast.parse(code)
            complexity = {
                'cyclomatic_complexity': 0,
                'function_count': 0,
                'class_count': 0,
                'max_nesting': 0,
                'avg_function_length': 0
            }
            
            function_lengths = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity['function_count'] += 1
                    # Calculate cyclomatic complexity
                    complexity['cyclomatic_complexity'] += 1
                    for child in ast.walk(node):
                        if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.ExceptHandler)):
                            complexity['cyclomatic_complexity'] += 1
                    
                    # Calculate function length
                    function_lengths.append(len(node.body))
                
                elif isinstance(node, ast.ClassDef):
                    complexity['class_count'] += 1
                
                # Calculate nesting depth
                if isinstance(node, (ast.If, ast.While, ast.For, ast.Try)):
                    depth = 0
                    current = node
                    while hasattr(current, 'parent'):
                        current = current.parent
                        depth += 1
                    complexity['max_nesting'] = max(complexity['max_nesting'], depth)
            
            if function_lengths:
                complexity['avg_function_length'] = sum(function_lengths) / len(function_lengths)
            
            return complexity
        except:
            return {}

    def analyze_dependencies(self, repo_path: str) -> Dict:
        """Analyze project dependencies."""
        dependencies = {
            'python': [],
            'javascript': [],
            'java': [],
            'ruby': []
        }
        
        # Python dependencies
        req_file = os.path.join(repo_path, 'requirements.txt')
        if os.path.exists(req_file):
            with open(req_file, 'r') as f:
                dependencies['python'] = [line.strip() for line in f if line.strip()]
        
        # JavaScript dependencies
        package_json = os.path.join(repo_path, 'package.json')
        if os.path.exists(package_json):
            with open(package_json, 'r') as f:
                try:
                    data = json.load(f)
                    dependencies['javascript'] = list(data.get('dependencies', {}).keys())
                except:
                    pass
        
        return dependencies

    def analyze_code_structure(self, repo_path: str) -> Dict:
        """Analyze the repository structure and extract key information."""
        structure = {
            'languages': {},
            'main_files': [],
            'dependencies': set(),
            'entry_points': [],
            'complexity_metrics': defaultdict(dict),
            'dependencies': self.analyze_dependencies(repo_path)
        }
        
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(('.py', '.js', '.java', '.cpp', '.go', '.rb')):
                    ext = os.path.splitext(file)[1]
                    structure['languages'][ext] = structure['languages'].get(ext, 0) + 1
                    
                    file_path = os.path.join(root, file)
                    if file in ['main.py', 'app.py', 'index.js', 'main.go']:
                        structure['entry_points'].append(file_path)
                    
                    # Analyze code complexity
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            code = f.read()
                            structure['complexity_metrics'][file_path] = self.analyze_code_complexity(code)
                    except:
                        pass
                    
                    # Check for dependency files
                    if file in ['requirements.txt', 'package.json', 'go.mod', 'Gemfile']:
                        structure['dependencies'].add(os.path.join(root, file))
        
        return structure

    def generate_code_summary(self, code: str) -> str:
        """Generate a summary of the code using CodeT5 model."""
        inputs = self.code_tokenizer.encode(
            "summarize: " + code,
            return_tensors="pt",
            max_length=512,
            truncation=True
        ).to(self.device)
        
        outputs = self.code_model.generate(
            inputs,
            max_length=150,
            num_beams=4,
            early_stopping=True
        )
        
        return self.code_tokenizer.decode(outputs[0], skip_special_tokens=True)

    def analyze_repository(self, repo_url: str) -> Dict:
        """Main method to analyze a repository and generate documentation."""
        try:
            # Clone repository
            repo_path, repo_name = self.clone_repository(repo_url)
            
            # Analyze structure
            structure = self.analyze_code_structure(repo_path)
            
            # Generate README content
            readme_content = self.generate_readme(repo_name, structure)
            
            # Clean up
            import shutil
            shutil.rmtree(repo_path)
            
            return {
                'repository_name': repo_name,
                'structure': structure,
                'readme_content': readme_content
            }
            
        except Exception as e:
            raise Exception(f"Error analyzing repository: {str(e)}")

    def generate_readme(self, repo_name: str, structure: Dict) -> str:
        """Generate a comprehensive README.md file."""
        readme = f"# {repo_name}\n\n"
        
        # Project Overview
        readme += "## Project Overview\n"
        readme += "This is an automatically generated documentation for the repository.\n\n"
        
        # Technologies Used
        readme += "## Technologies Used\n"
        for lang, count in structure['languages'].items():
            readme += f"- {lang[1:].upper()}: {count} files\n"
        
        # Dependencies
        if structure['dependencies']:
            readme += "\n## Dependencies\n"
            for lang, deps in structure['dependencies'].items():
                if deps:
                    readme += f"\n### {lang.title()}\n"
                    for dep in deps:
                        readme += f"- {dep}\n"
        
        # Project Structure
        readme += "\n## Project Structure\n"
        readme += "The project contains the following main components:\n"
        for entry in structure['entry_points']:
            readme += f"- {os.path.basename(entry)}\n"
        
        # Code Complexity
        readme += "\n## Code Complexity Analysis\n"
        for file_path, metrics in structure['complexity_metrics'].items():
            if metrics:
                readme += f"\n### {os.path.basename(file_path)}\n"
                readme += f"- Cyclomatic Complexity: {metrics.get('cyclomatic_complexity', 'N/A')}\n"
                readme += f"- Function Count: {metrics.get('function_count', 'N/A')}\n"
                readme += f"- Class Count: {metrics.get('class_count', 'N/A')}\n"
                readme += f"- Max Nesting Depth: {metrics.get('max_nesting', 'N/A')}\n"
                readme += f"- Average Function Length: {metrics.get('avg_function_length', 'N/A'):.2f} lines\n"
        
        return readme 