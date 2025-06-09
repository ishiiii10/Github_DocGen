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

    def analyze_code_structure(self, repo_path: str) -> Dict:
        """Analyze the repository structure and extract key information."""
        structure = {
            'languages': {},
            'main_files': [],
            'dependencies': set(),
            'entry_points': []
        }
        
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(('.py', '.js', '.java', '.cpp', '.go', '.rb')):
                    ext = os.path.splitext(file)[1]
                    structure['languages'][ext] = structure['languages'].get(ext, 0) + 1
                    
                    if file in ['main.py', 'app.py', 'index.js', 'main.go']:
                        structure['entry_points'].append(os.path.join(root, file))
                    
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
            for dep in structure['dependencies']:
                readme += f"- {os.path.basename(dep)}\n"
        
        # Project Structure
        readme += "\n## Project Structure\n"
        readme += "The project contains the following main components:\n"
        for entry in structure['entry_points']:
            readme += f"- {os.path.basename(entry)}\n"
        
        return readme 