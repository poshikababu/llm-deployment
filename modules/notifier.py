"""
Notification Module
Handles sending notifications to evaluation services with retry logic.
"""

import time
import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)


class EvaluationNotifier:
    """
    Handles notifications to evaluation services with retry mechanisms.
    """
    
    def __init__(self):
        """Initialize the notifier."""
        self.max_retries = 4  # Will retry with delays: 1s, 2s, 4s, 8s
        self.base_delay = 1.0  # Base delay in seconds
        
    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay.
        
        Args:
            attempt: Current attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        return self.base_delay * (2 ** attempt)
    
    def _send_notification_request(self, url: str, data: Dict[str, Any]) -> bool:
        """
        Send a single notification request.
        
        Args:
            url: Evaluation URL to send notification to
            data: Notification payload
            
        Returns:
            True if successful (200 OK), False otherwise
        """
        try:
            logger.info(f"Sending notification to: {url}")
            logger.debug(f"Notification payload: {data}")
            
            response = requests.post(
                url,
                json=data,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'LLM-Code-Deployment/1.0'
                },
                timeout=30  # 30 second timeout
            )
            
            logger.info(f"Notification response: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("Notification sent successfully")
                return True
            else:
                logger.warning(f"Notification failed with status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("Notification request timed out")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("Connection error while sending notification")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error while sending notification: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while sending notification: {str(e)}")
            return False
    
    def send_notification(self, evaluation_url: str, notification_data: Dict[str, Any]) -> bool:
        """
        Send notification with retry logic and exponential backoff.
        
        Args:
            evaluation_url: URL to send the notification to
            notification_data: Data to send in the notification
            
        Returns:
            True if notification was sent successfully, False otherwise
        """
        logger.info(f"Starting notification process for task: {notification_data.get('task')}")
        
        # Validate required fields
        required_fields = ['email', 'task', 'round', 'nonce', 'repo_url', 'commit_sha', 'pages_url']
        missing_fields = [field for field in required_fields if field not in notification_data]
        
        if missing_fields:
            logger.error(f"Missing required fields in notification data: {missing_fields}")
            return False
        
        # Validate URL
        if not evaluation_url or not evaluation_url.startswith(('http://', 'https://')):
            logger.error(f"Invalid evaluation URL: {evaluation_url}")
            return False
        
        # Attempt to send notification with retries
        for attempt in range(self.max_retries + 1):  # 0 to max_retries (inclusive)
            try:
                logger.info(f"Notification attempt {attempt + 1}/{self.max_retries + 1}")
                
                success = self._send_notification_request(evaluation_url, notification_data)
                
                if success:
                    logger.info(f"Notification successful on attempt {attempt + 1}")
                    return True
                
                # If this wasn't the last attempt, wait before retrying
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.info(f"Notification failed, retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"Notification failed after {self.max_retries + 1} attempts")
                    
            except Exception as e:
                logger.error(f"Unexpected error in notification attempt {attempt + 1}: {str(e)}")
                
                # If this wasn't the last attempt, wait before retrying
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.info(f"Retrying in {delay} seconds due to error...")
                    time.sleep(delay)
        
        logger.error("All notification attempts failed")
        return False
    
    def validate_notification_data(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate notification data structure and content.
        
        Args:
            data: Notification data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = {
            'email': str,
            'task': str,
            'round': int,
            'nonce': str,
            'repo_url': str,
            'commit_sha': str,
            'pages_url': str
        }
        
        # Check for missing fields
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        # Check field types
        for field, expected_type in required_fields.items():
            if not isinstance(data[field], expected_type):
                return False, f"Field '{field}' must be of type {expected_type.__name__}, got {type(data[field]).__name__}"
        
        # Validate URLs
        if not data['repo_url'].startswith(('http://', 'https://')):
            return False, f"Invalid repo_url format: {data['repo_url']}"
        
        if not data['pages_url'].startswith(('http://', 'https://')):
            return False, f"Invalid pages_url format: {data['pages_url']}"
        
        # Validate round number
        if data['round'] < 1:
            return False, f"Round number must be >= 1, got {data['round']}"
        
        # Validate commit SHA format (basic check)
        commit_sha = data['commit_sha']
        if not commit_sha or len(commit_sha) < 7:
            return False, f"Invalid commit SHA format: {commit_sha}"
        
        # Validate email format (basic check)
        email = data['email']
        if '@' not in email or '.' not in email:
            return False, f"Invalid email format: {email}"
        
        return True, "Validation passed"