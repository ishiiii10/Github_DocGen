from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from flask import current_app
import torch
from typing import Dict, Any, List
import re

class AnalysisService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained("Salesforce/codet5-base")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("Salesforce/codet5-base").to(self.device)
        
    def analyze_repository(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze repository code and structure."""
        analysis = {
            'project_summary': self._generate_project_summary(repo_data),
            'tech_stack': self._detect_tech_stack(repo_data),
            'code_analysis': self._analyze_code_structure(repo_data),
            'complexity_metrics': self._calculate_complexity_metrics(repo_data)
        }
        return analysis
        
    def _generate_project_summary(self, repo_data: Dict[str, Any]) -> str:
        """Generate a summary of the project using CodeT5."""
        # Combine relevant information for summary generation
        context = f"""
        Project: {repo_data['name']}
        Description: {repo_data['description']}
        Language: {repo_data['language']}
        Topics: {', '.join(repo_data['topics'])}
        """
        
        # Generate summary using CodeT5
        inputs = self.tokenizer.encode(
            f"summarize: {context}",
            return_tensors="pt",
            max_length=512,
            truncation=True
        ).to(self.device)
        
        summary_ids = self.model.generate(
            inputs,
            max_length=150,
            num_beams=4,
            early_stopping=True
        )
        
        return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        
    def _detect_tech_stack(self, repo_data: Dict[str, Any]) -> List[str]:
        """Detect technologies used in the project."""
        tech_stack = set()
        
        # Add primary language
        if repo_data['language']:
            tech_stack.add(repo_data['language'])
            
        # Detect frameworks and libraries from file patterns
        file_patterns = {
            'Python': ['.py$'],
            'JavaScript': ['.js$', '.jsx$', '.ts$', '.tsx$'],
            'React': ['.jsx$', '.tsx$'],
            'Node.js': ['package.json$'],
            'Django': ['settings.py$', 'urls.py$'],
            'Flask': ['app.py$', 'flask_app.py$'],
            'Java': ['.java$'],
            'C#': ['.cs$'],
            'Ruby': ['.rb$'],
            'PHP': ['.php$']
        }
        
        for file in repo_data['files']:
            for tech, patterns in file_patterns.items():
                if any(re.search(pattern, file['path']) for pattern in patterns):
                    tech_stack.add(tech)
                    
        return list(tech_stack)
        
    def _analyze_code_structure(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the structure of the codebase."""
        structure = {
            'total_files': len(repo_data['files']),
            'file_types': {},
            'main_directories': set(),
            'architecture_patterns': []
        }
        
        # Analyze file types and directories
        for file in repo_data['files']:
            ext = file['path'].split('.')[-1] if '.' in file['path'] else 'no_extension'
            structure['file_types'][ext] = structure['file_types'].get(ext, 0) + 1
            
            # Get main directories
            dir_path = '/'.join(file['path'].split('/')[:-1])
            if dir_path:
                structure['main_directories'].add(dir_path)
                
        # Convert set to list for JSON serialization
        structure['main_directories'] = list(structure['main_directories'])
        
        return structure
        
    def _calculate_complexity_metrics(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate basic complexity metrics."""
        metrics = {
            'total_files': len(repo_data['files']),
            'total_size': sum(file['size'] for file in repo_data['files']),
            'languages': {},
            'file_types': {}
        }
        
        # Calculate metrics by language and file type
        for file in repo_data['files']:
            ext = file['path'].split('.')[-1] if '.' in file['path'] else 'no_extension'
            metrics['file_types'][ext] = metrics['file_types'].get(ext, 0) + 1
            
        return metrics 