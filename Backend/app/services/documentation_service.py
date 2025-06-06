from typing import Dict, Any
from datetime import datetime

class DocumentationService:
    def generate_documentation(self, repo_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive documentation for the repository."""
        documentation = {
            'readme': self._generate_readme(repo_data, analysis_results),
            'project_structure': self._generate_project_structure(repo_data),
            'technical_documentation': self._generate_technical_docs(repo_data, analysis_results)
        }
        return documentation
        
    def _generate_readme(self, repo_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> str:
        """Generate a comprehensive README.md file."""
        readme = f"""# {repo_data['name']}

{repo_data['description'] or 'No description provided.'}

## Project Overview

{analysis_results['project_summary']}

## Technology Stack

The project uses the following technologies:

{self._format_tech_stack(analysis_results['tech_stack'])}

## Project Structure

{self._format_project_structure(repo_data, analysis_results)}

## Getting Started

### Prerequisites

{self._generate_prerequisites(analysis_results['tech_stack'])}

### Installation

```bash
# Clone the repository
git clone https://github.com/{repo_data['owner']}/{repo_data['name']}.git

# Navigate to the project directory
cd {repo_data['name']}

{self._generate_installation_steps(analysis_results['tech_stack'])}
```

## Usage

{self._generate_usage_instructions(repo_data, analysis_results)}

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---
*This documentation was automatically generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return readme
        
    def _format_tech_stack(self, tech_stack: list) -> str:
        """Format the technology stack section."""
        return "\n".join([f"- {tech}" for tech in tech_stack])
        
    def _format_project_structure(self, repo_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> str:
        """Format the project structure section."""
        structure = analysis_results['code_analysis']
        output = f"Total Files: {structure['total_files']}\n\n"
        
        # Add main directories
        output += "Main Directories:\n"
        for directory in sorted(structure['main_directories']):
            output += f"- {directory}/\n"
            
        # Add file types
        output += "\nFile Types:\n"
        for ext, count in sorted(structure['file_types'].items()):
            output += f"- {ext}: {count} files\n"
            
        return output
        
    def _generate_prerequisites(self, tech_stack: list) -> str:
        """Generate prerequisites based on the technology stack."""
        prerequisites = []
        
        if 'Python' in tech_stack:
            prerequisites.append("- Python 3.8 or higher")
        if 'Node.js' in tech_stack:
            prerequisites.append("- Node.js 14 or higher")
        if 'Java' in tech_stack:
            prerequisites.append("- Java Development Kit (JDK) 11 or higher")
            
        return "\n".join(prerequisites) if prerequisites else "No specific prerequisites required."
        
    def _generate_installation_steps(self, tech_stack: list) -> str:
        """Generate installation steps based on the technology stack."""
        steps = []
        
        if 'Python' in tech_stack:
            steps.extend([
                "# Create and activate virtual environment",
                "python -m venv venv",
                "source venv/bin/activate  # On Windows: venv\\Scripts\\activate",
                "",
                "# Install dependencies",
                "pip install -r requirements.txt"
            ])
        elif 'Node.js' in tech_stack:
            steps.extend([
                "# Install dependencies",
                "npm install"
            ])
            
        return "\n".join(steps)
        
    def _generate_usage_instructions(self, repo_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> str:
        """Generate usage instructions based on the project type."""
        if 'Python' in analysis_results['tech_stack']:
            return """```bash
# Run the application
python main.py
```"""
        elif 'Node.js' in analysis_results['tech_stack']:
            return """```bash
# Start the development server
npm start
```"""
        else:
            return "Please refer to the project's documentation for specific usage instructions."
            
    def _generate_project_structure(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a detailed project structure documentation."""
        structure = {
            'root': {
                'name': repo_data['name'],
                'type': 'directory',
                'children': {}
            }
        }
        
        # Organize files into a tree structure
        for file in repo_data['files']:
            path_parts = file['path'].split('/')
            current = structure['root']
            
            for i, part in enumerate(path_parts[:-1]):
                if part not in current['children']:
                    current['children'][part] = {
                        'name': part,
                        'type': 'directory',
                        'children': {}
                    }
                current = current['children'][part]
                
            current['children'][path_parts[-1]] = {
                'name': path_parts[-1],
                'type': 'file',
                'size': file['size']
            }
            
        return structure
        
    def _generate_technical_docs(self, repo_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate technical documentation."""
        return {
            'architecture': {
                'overview': analysis_results['project_summary'],
                'components': self._identify_components(repo_data),
                'dependencies': analysis_results['tech_stack']
            },
            'metrics': analysis_results['complexity_metrics'],
            'code_analysis': analysis_results['code_analysis']
        }
        
    def _identify_components(self, repo_data: Dict[str, Any]) -> list:
        """Identify main components of the project."""
        components = []
        common_patterns = {
            'frontend': ['src/', 'public/', 'components/'],
            'backend': ['api/', 'server/', 'controllers/'],
            'database': ['models/', 'db/', 'migrations/'],
            'tests': ['tests/', 'spec/', '__tests__/'],
            'docs': ['docs/', 'documentation/']
        }
        
        for file in repo_data['files']:
            for component, patterns in common_patterns.items():
                if any(pattern in file['path'] for pattern in patterns):
                    if component not in components:
                        components.append(component)
                        
        return components 