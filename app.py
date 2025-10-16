"""
LLM Code Deployment Application
Main Flask server that handles project brief requests and automates code deployment.
"""

import os
import json
import threading
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from modules.llm_generator import LLMGenerator
from modules.github_manager import GitHubManager
from modules.notifier import EvaluationNotifier

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global configuration
SHARED_SECRET = os.getenv('SHARED_SECRET')
if not SHARED_SECRET:
    logger.error("SHARED_SECRET environment variable is required")
    raise ValueError("SHARED_SECRET environment variable is required")


def process_request_background(request_data):
    """
    Process the deployment request in the background.
    This function runs in a separate thread to avoid blocking the HTTP response.
    """
    try:
        # Ensure environment variables are loaded in the background thread
        load_dotenv()
        
        logger.info(f"Starting background processing for task: {request_data.get('task')}")
        
        # Initialize components
        llm_generator = LLMGenerator()
        github_manager = GitHubManager()
        notifier = EvaluationNotifier()
        
        # Extract request data
        email = request_data['email']
        task = request_data['task']
        round_num = request_data['round']
        nonce = request_data['nonce']
        brief = request_data['brief']
        attachments = request_data.get('attachments', [])
        evaluation_url = request_data['evaluation_url']
        
        logger.info(f"Processing request - Task: {task}, Round: {round_num}")
        
        # Step 1: Generate code using LLM
        logger.info("Generating code with LLM...")
        generated_code = llm_generator.generate_code(brief, attachments)
        
        # Step 2: Handle GitHub repository operations
        logger.info("Managing GitHub repository...")
        if round_num == 1:
            # Create new repository for round 1
            repo_url, commit_sha, pages_url = github_manager.create_and_deploy_repository(
                task, generated_code, brief
            )
        else:
            # Update existing repository for round > 1
            repo_url, commit_sha, pages_url = github_manager.update_repository(
                task, generated_code, brief
            )
        
        logger.info(f"Repository deployed - URL: {repo_url}, Pages: {pages_url}")
        
        # Step 3: Notify evaluation service
        logger.info("Sending evaluation notification...")
        notification_data = {
            "email": email,
            "task": task,
            "round": round_num,
            "nonce": nonce,
            "repo_url": repo_url,
            "commit_sha": commit_sha,
            "pages_url": pages_url
        }
        
        success = notifier.send_notification(evaluation_url, notification_data)
        
        if success:
            logger.info(f"Successfully completed processing for task: {task}")
        else:
            logger.error(f"Failed to send notification for task: {task}")
            
    except Exception as e:
        logger.error(f"Error in background processing: {str(e)}", exc_info=True)


@app.route('/api-endpoint', methods=['POST'])
def handle_deployment_request():
    """
    Main API endpoint that receives project briefs and initiates deployment process.
    """
    try:
        # Validate content type
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        # Parse request data
        request_data = request.get_json()
        if not request_data:
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        # Verify required fields
        required_fields = ['email', 'secret', 'task', 'round', 'nonce', 'brief', 'evaluation_url']
        missing_fields = [field for field in required_fields if field not in request_data]
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Verify secret
        provided_secret = request_data.get('secret')
        if provided_secret != SHARED_SECRET:
            logger.warning(f"Invalid secret provided for task: {request_data.get('task')}")
            return jsonify({"error": "Unauthorized"}), 401
        
        logger.info(f"Received valid request for task: {request_data.get('task')}, round: {request_data.get('round')}")
        
        # Start background processing
        background_thread = threading.Thread(
            target=process_request_background,
            args=(request_data,),
            daemon=True
        )
        background_thread.start()
        
        # Return immediate response
        return jsonify({
            "status": "Request received and is being processed."
        }), 200
        
    except Exception as e:
        logger.error(f"Error handling request: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "llm-code-deployment"}), 200


if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=3000, debug=True)