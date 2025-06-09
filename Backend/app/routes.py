from flask import Blueprint, request, jsonify, current_app
from .repository_analyzer import RepositoryAnalyzer

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return jsonify({
        'status': 'API is running',
        'endpoints': {
            '/api/analyze': {
                'method': 'POST',
                'description': 'Analyze a GitHub repository',
                'body': {
                    'repo_url': 'GitHub repository URL'
                }
            }
        }
    })

@main.route('/api/analyze', methods=['POST'])
def analyze_repository():
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        
        if not repo_url:
            return jsonify({'error': 'Repository URL is required'}), 400
            
        # Initialize analyzer with tokens from config
        analyzer = RepositoryAnalyzer(
            github_token=current_app.config['GITHUB_TOKEN'],
            huggingface_token=current_app.config['HUGGINGFACE_TOKEN']
        )
        
        # Analyze repository
        result = analyzer.analyze_repository(repo_url)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/health', methods=['GET'])
def health_check():
    current_app.logger.info('Health check request received')
    return jsonify({'status': 'healthy'}) 