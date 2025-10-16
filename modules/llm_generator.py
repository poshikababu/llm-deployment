"""
LLM Generator Module
Handles code generation using OpenRouter API.
"""

import os
import logging
import base64
from typing import List, Dict, Any
from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMGenerator:
    """
    Handles LLM-based code generation using OpenRouter API.
    """
    
    def __init__(self):
        """Initialize the LLM generator with OpenRouter configuration."""
        # Get OpenRouter API key
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        if not openrouter_key:
            raise ValueError("OPENROUTER_API_KEY is required")
        
        # Initialize OpenRouter client
        self.client = OpenAI(
            api_key=openrouter_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Default model configuration
        self.model = os.getenv('LLM_MODEL', 'tngtech/deepseek-r1t2-chimera:free')
        
        logger.info(f"LLM Generator initialized with OpenRouter - Model: {self.model}")
    
    def _process_attachments(self, attachments: List[Dict[str, Any]]) -> str:
        """
        Process attachments and return formatted text for the LLM prompt.
        """
        if not attachments:
            return ""
        
        attachment_text = "\n\nATTACHMENTS:\n"
        
        for attachment in attachments:
            name = attachment.get('name', 'unknown')
            url = attachment.get('url', '')
            
            attachment_text += f"\nFile: {name}\n"
            
            # Handle data URIs
            if url.startswith('data:'):
                try:
                    # Parse data URI: data:mime/type;base64,data
                    header, data = url.split(',', 1)
                    mime_info = header.split(';')[0].replace('data:', '')
                    
                    if 'base64' in header:
                        decoded_data = base64.b64decode(data)
                        
                        # Handle different file types
                        if mime_info.startswith('text/') or name.endswith(('.txt', '.csv', '.md')):
                            try:
                                content = decoded_data.decode('utf-8')
                                attachment_text += f"Content:\n{content}\n"
                            except UnicodeDecodeError:
                                attachment_text += f"Binary file ({len(decoded_data)} bytes)\n"
                        else:
                            attachment_text += f"Binary file: {mime_info} ({len(decoded_data)} bytes)\n"
                            attachment_text += f"Data URI: {url[:100]}...\n"
                    else:
                        attachment_text += f"Data URI: {url}\n"
                        
                except Exception as e:
                    logger.warning(f"Error processing attachment {name}: {str(e)}")
                    attachment_text += f"Error processing attachment: {str(e)}\n"
            else:
                attachment_text += f"URL: {url}\n"
        
        return attachment_text
    
    def _create_prompt(self, brief: str, attachments: List[Dict[str, Any]]) -> str:
        """
        Create a detailed prompt for code generation.
        """
        attachment_info = self._process_attachments(attachments)
        
        prompt = f"""You are an expert web developer. Generate a complete, self-contained HTML file based on the following requirements.

PROJECT BRIEF:
{brief}

{attachment_info}

REQUIREMENTS:
1. Create a single HTML file that includes ALL necessary code
2. Include CSS within <style> tags in the <head> section
3. Include JavaScript within <script> tags (can be in <head> or before </body>)
4. The application must be fully functional and self-contained
5. Handle any provided attachments appropriately (decode base64 data if needed)
6. Use modern web standards and best practices
7. Make the interface responsive and user-friendly
8. Include proper error handling in JavaScript
9. Add appropriate comments in the code

IMPORTANT GUIDELINES:
- The HTML file must work when opened directly in a browser
- Do not use external dependencies unless absolutely necessary
- If external libraries are needed, use CDN links
- Ensure the code is clean, well-structured, and documented
- Handle edge cases and provide user feedback
- Make the interface intuitive and accessible

Generate ONLY the complete HTML file content. Do not include any explanations or additional text outside the HTML."""

        return prompt
    
    def _validate_generated_code(self, code: str) -> bool:
        """
        Validate that the generated code is a proper HTML document.
        """
        if not code or len(code.strip()) < 50:
            logger.error("Generated code is too short or empty")
            return False
        
        # Check for basic HTML structure
        code_lower = code.lower()
        required_tags = ['<html', '<head', '<body', '</html>']
        
        for tag in required_tags:
            if tag not in code_lower:
                logger.error(f"Generated code missing required tag: {tag}")
                return False
        
        logger.info("Generated code validation passed")
        return True
    
    def generate_code(self, brief: str, attachments: List[Dict[str, Any]] | None = None) -> str:
        """
        Generate code based on the project brief and attachments.
        
        Args:
            brief: Project description and requirements
            attachments: List of attachment objects with name and data URI
            
        Returns:
            Generated HTML code as a string
        """
        if attachments is None:
            attachments = []
        
        logger.info(f"Generating code for brief: {brief[:100]}...")
        
        # Create the prompt
        prompt = self._create_prompt(brief, attachments)
        
        try:
            logger.info("Using OpenRouter LLM client")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert web developer who creates complete, functional web applications."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.7
            )
            
            generated_code = response.choices[0].message.content
            if not generated_code:
                raise ValueError("Empty response from LLM")
            
            generated_code = generated_code.strip()
            
            # Validate the generated code
            if self._validate_generated_code(generated_code):
                logger.info("Code generation successful")
                return generated_code
            else:
                raise ValueError("Generated code validation failed")
                
        except Exception as e:
            logger.error(f"LLM code generation failed: {str(e)}")
            raise Exception(f"Code generation failed: {str(e)}")