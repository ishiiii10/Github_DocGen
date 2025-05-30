from flask import Blueprint, request, jsonify
from .services.github_service import GitHubService
from .services.analysis_service import AnalysisService
from .services.documentation_service import DocumentationService

main = Blueprint('main', __name__)

@main.route('/api/analyze', methods=['POST'])
def analyze_repository():
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        
        if not repo_url:
            return jsonify({'error': 'Repository URL is required'}), 400
            
        # Initialize services
        github_service = GitHubService()
        analysis_service = AnalysisService()
        documentation_service = DocumentationService()
        
        # Fetch repository data
        repo_data = github_service.fetch_repository(repo_url)
        
        # Analyze repository
        analysis_results = analysis_service.analyze_repository(repo_data)
        
        # Generate documentation
        documentation = documentation_service.generate_documentation(
            repo_data,
            analysis_results
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'repository_info': repo_data,
                'analysis': analysis_results,
                'documentation': documentation
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}) 