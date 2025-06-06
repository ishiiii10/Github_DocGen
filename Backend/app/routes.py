from flask import Blueprint, request, jsonify, current_app
from .services.github_service import GitHubService
from .services.analysis_service import AnalysisService
from .services.documentation_service import DocumentationService
import logging

main = Blueprint('main', __name__)

@main.route('/api/analyze', methods=['POST'])
def analyze_repository():
    current_app.logger.info('Received analyze request')
    try:
        data = request.get_json()
        current_app.logger.info(f'Request data: {data}')
        
        repo_url = data.get('repo_url')
        if not repo_url:
            current_app.logger.error('Repository URL is missing')
            return jsonify({'error': 'Repository URL is required'}), 400
            
        # Initialize services
        github_service = GitHubService()
        analysis_service = AnalysisService()
        documentation_service = DocumentationService()
        
        # Fetch repository data
        current_app.logger.info(f'Fetching repository data for: {repo_url}')
        repo_data = github_service.fetch_repository(repo_url)
        
        # Analyze repository
        current_app.logger.info('Analyzing repository')
        analysis_results = analysis_service.analyze_repository(repo_data)
        
        # Generate documentation
        current_app.logger.info('Generating documentation')
        documentation = documentation_service.generate_documentation(
            repo_data,
            analysis_results
        )
        
        current_app.logger.info('Successfully generated documentation')
        return jsonify({
            'status': 'success',
            'data': {
                'repository_info': repo_data,
                'analysis': analysis_results,
                'documentation': documentation
            }
        })
        
    except Exception as e:
        current_app.logger.error(f'Error processing request: {str(e)}')
        return jsonify({'error': str(e)}), 500

@main.route('/api/health', methods=['GET'])
def health_check():
    current_app.logger.info('Health check request received')
    return jsonify({'status': 'healthy'}) 