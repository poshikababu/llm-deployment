"""
GitHub Manager Module
Handles GitHub repository creation, updates, and GitHub Pages deployment.
"""

import os
import logging
from typing import Tuple
from github import Github
from github.Repository import Repository
from github import InputGitTreeElement

logger = logging.getLogger(__name__)


class GitHubManager:
    """
    Manages GitHub repository operations for code deployment.
    """
    
    def __init__(self):
        """Initialize GitHub manager with authentication."""
        self.github_pat = os.getenv('GITHUB_PAT')
        self.github_username = os.getenv('GITHUB_USERNAME')
        
        if not self.github_pat:
            raise ValueError("GITHUB_PAT environment variable is required")
        if not self.github_username:
            raise ValueError("GITHUB_USERNAME environment variable is required")
        
        try:
            self.github = Github(self.github_pat)
            # Test authentication
            self.user = self.github.get_user()
            logger.info(f"GitHub authenticated as: {self.user.login}")
        except Exception as e:
            logger.error(f"GitHub authentication failed: {str(e)}")
            raise
    
    def _generate_repo_name(self, task_id: str) -> str:
        """
        Generate a unique repository name based on the task ID.
        """
        # Clean the task ID to make it a valid repo name
        repo_name = task_id.lower().replace('_', '-').replace(' ', '-')
        # Remove any invalid characters
        repo_name = ''.join(c for c in repo_name if c.isalnum() or c in '-.')
        return repo_name
    
    def _create_license_content(self) -> str:
        """
        Generate MIT License content.
        """
        return """MIT License

Copyright (c) 2024 LLM Code Deployment

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    
    def _create_readme_content(self, brief: str, repo_name: str) -> str:
        """
        Generate README.md content based on the project brief.
        """
        return f"""# {repo_name.replace('-', ' ').title()}

## Overview

This project was automatically generated based on the following brief:

> {brief}

## Description

This is a web application that implements the requirements specified in the project brief. The application is built using modern web technologies and follows best practices for web development.

## Setup and Usage

This is a static web application that can be run directly in any modern web browser.

### Local Development

1. Clone this repository:
   ```bash
   git clone https://github.com/{self.github_username}/{repo_name}.git
   cd {repo_name}
   ```

2. Open `index.html` in your web browser:
   ```bash
   # On macOS
   open index.html
   
   # On Linux
   xdg-open index.html
   
   # On Windows
   start index.html
   ```

### Live Demo

The application is automatically deployed to GitHub Pages and can be accessed at:
https://{self.github_username}.github.io/{repo_name}/

## Code Structure

- `index.html` - Main application file containing HTML, CSS, and JavaScript
- `README.md` - This documentation file
- `LICENSE` - MIT License file

## Implementation Details

The application is implemented as a single HTML file that includes:

- **HTML Structure**: Semantic markup for the user interface
- **CSS Styling**: Embedded styles for responsive design and visual presentation
- **JavaScript Logic**: Client-side functionality and interactivity

The code follows modern web development best practices including:
- Responsive design principles
- Accessibility considerations
- Error handling and user feedback
- Clean, maintainable code structure

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Auto-Generated

This project was automatically generated using an LLM-based code deployment system.
"""
    
    def _get_or_create_repository(self, repo_name: str, brief: str) -> Repository:
        """
        Get existing repository or create a new one.
        """
        try:
            # Try to get existing repository
            repo = self.user.get_repo(repo_name)
            logger.info(f"Found existing repository: {repo_name}")
            return repo
        except Exception:
            # Repository doesn't exist, create it
            logger.info(f"Creating new repository: {repo_name}")
            
            try:
                # Clean the description to avoid control characters
                clean_description = ''.join(c for c in brief[:100] if ord(c) >= 32 and ord(c) != 127)
                description = f"Auto-generated web application: {clean_description}..."
                
                # Use the authenticated user to create repo
                repo = self.user.create_repo(
                    name=repo_name,
                    description=description,
                    private=False,
                    auto_init=True
                )
                logger.info(f"Successfully created repository: {repo_name}")
                return repo
            except Exception as e:
                logger.error(f"Failed to create repository {repo_name}: {str(e)}")
                # Try alternative method with auto_init
                try:
                    logger.info("Trying alternative repository creation method...")
                    repo = self.user.create_repo(
                        name=repo_name,
                        auto_init=True
                    )
                    logger.info(f"Successfully created repository with alternative method: {repo_name}")
                    return repo
                except Exception as e2:
                    logger.error(f"Alternative method also failed: {str(e2)}")
                    raise Exception(f"Repository creation failed. Primary: {str(e)}, Alternative: {str(e2)}")
    
    def _commit_files(self, repo: Repository, files: dict, commit_message: str) -> str:
        """
        Commit multiple files to the repository.
        
        Args:
            repo: GitHub repository object
            files: Dictionary of {filename: content}
            commit_message: Commit message
            
        Returns:
            Commit SHA
        """
        try:
            # Check if repository is empty
            try:
                # Try to get the default branch
                default_branch = repo.default_branch
                latest_commit = repo.get_branch(default_branch).commit
                base_tree = repo.get_git_tree(latest_commit.sha)
                has_commits = True
                logger.info(f"Repository has existing commits, using branch: {default_branch}")
            except Exception as e:
                # Repository is empty or branch doesn't exist
                logger.info(f"Repository appears empty or no default branch: {str(e)}")
                default_branch = "main"  # Use main as default
                base_tree = None
                latest_commit = None
                has_commits = False
            
            # Create tree elements for all files
            tree_elements = []
            
            for filename, content in files.items():
                logger.info(f"Processing file: {filename} ({len(content)} chars)")
                
                # For empty repos, we need to handle blob creation differently
                if has_commits:
                    # Normal blob creation for repos with commits
                    blob = repo.create_git_blob(content, "utf-8")
                else:
                    # For empty repos, create blob using raw API
                    import base64
                    blob_data = {
                        "content": base64.b64encode(content.encode('utf-8')).decode('ascii'),
                        "encoding": "base64"
                    }
                    headers, data = repo._requester.requestJsonAndCheck(
                        "POST",
                        f"{repo.url}/git/blobs",
                        input=blob_data
                    )
                    blob_sha = data["sha"]
                    
                    # Create a mock blob object
                    class MockBlob:
                        def __init__(self, sha):
                            self.sha = sha
                    blob = MockBlob(blob_sha)
                
                # Create InputGitTreeElement object
                tree_element = InputGitTreeElement(
                    path=filename,
                    mode="100644",
                    type="blob",
                    sha=blob.sha
                )
                tree_elements.append(tree_element)
            
            # Create new tree
            if base_tree:
                tree = repo.create_git_tree(tree_elements, base_tree)
            else:
                tree = repo.create_git_tree(tree_elements)
            
            # Create commit
            if has_commits and latest_commit:
                commit = repo.create_git_commit(
                    commit_message,
                    tree,
                    [latest_commit.commit]
                )
            else:
                # Initial commit
                commit = repo.create_git_commit(
                    commit_message,
                    tree,
                    []
                )
            
            # Create or update branch reference
            try:
                ref = repo.get_git_ref(f"heads/{default_branch}")
                ref.edit(commit.sha)
            except Exception:
                # Branch doesn't exist, create it
                repo.create_git_ref(f"refs/heads/{default_branch}", commit.sha)
            
            logger.info(f"Successfully committed files with SHA: {commit.sha}")
            return commit.sha
            
        except Exception as e:
            logger.error(f"Failed to commit files: {str(e)}")
            raise
    
    def _enable_github_pages(self, repo: Repository) -> str:
        """
        Enable GitHub Pages for the repository using the exact same method as the working curl command.
        
        Returns:
            GitHub Pages URL
        """
        pages_url = f"https://{self.github_username}.github.io/{repo.name}/"
        
        try:
            default_branch = repo.default_branch
            logger.info(f"Enabling GitHub Pages for branch: {default_branch}")
            
            # Use the exact same approach as the working curl command
            import requests
            
            headers = {
                "Authorization": f"token {self.github_pat}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }
            
            pages_config = {
                "source": {
                    "branch": default_branch,
                    "path": "/"
                }
            }
            
            # Make the exact same API call as the working curl command
            response = requests.post(
                f"https://api.github.com/repos/{self.github_username}/{repo.name}/pages",
                json=pages_config,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"GitHub Pages enabled successfully: {response.json()}")
                return pages_url
            elif response.status_code == 409:
                # Pages already exist
                logger.info("GitHub Pages already enabled")
                return pages_url
            else:
                logger.error(f"GitHub Pages API failed: {response.status_code} - {response.text}")
                logger.warning(f"Returning expected pages URL anyway: {pages_url}")
                return pages_url
                
        except Exception as e:
            logger.error(f"Error enabling GitHub Pages: {str(e)}")
            logger.warning(f"Returning expected pages URL: {pages_url}")
            return pages_url
    
    def create_and_deploy_repository(self, task_id: str, generated_code: str, brief: str) -> Tuple[str, str, str]:
        """
        Create a new repository and deploy the generated code.
        
        Args:
            task_id: Unique task identifier
            generated_code: HTML code to deploy
            brief: Project brief for README
            
        Returns:
            Tuple of (repo_url, commit_sha, pages_url)
        """
        try:
            repo_name = self._generate_repo_name(task_id)
            logger.info(f"Creating and deploying repository: {repo_name}")
            
            # Get or create repository
            repo = self._get_or_create_repository(repo_name, brief)
            
            # Prepare files to commit
            files = {
                "index.html": generated_code,
                "LICENSE": self._create_license_content(),
                "README.md": self._create_readme_content(brief, repo_name)
            }
            
            # Commit files
            commit_sha = self._commit_files(
                repo,
                files,
                "Initial deployment: Auto-generated web application"
            )
            
            # Enable GitHub Pages
            pages_url = self._enable_github_pages(repo)
            
            repo_url = repo.html_url
            
            logger.info(f"Repository deployment complete - URL: {repo_url}")
            return repo_url, commit_sha, pages_url
            
        except Exception as e:
            logger.error(f"Failed to create and deploy repository: {str(e)}")
            raise
    
    def update_repository(self, task_id: str, generated_code: str, brief: str) -> Tuple[str, str, str]:
        """
        Update an existing repository with new code (for round > 1).
        
        Args:
            task_id: Unique task identifier
            generated_code: Updated HTML code
            brief: Updated project brief
            
        Returns:
            Tuple of (repo_url, commit_sha, pages_url)
        """
        try:
            repo_name = self._generate_repo_name(task_id)
            logger.info(f"Updating repository: {repo_name}")
            
            # Get existing repository
            try:
                repo = self.user.get_repo(repo_name)
            except Exception as e:
                logger.error(f"Repository {repo_name} not found for update: {str(e)}")
                raise ValueError(f"Repository {repo_name} does not exist for update")
            
            # Prepare updated files
            files = {
                "index.html": generated_code,
                "README.md": self._create_readme_content(brief, repo_name)
            }
            
            # Commit updated files
            commit_sha = self._commit_files(
                repo,
                files,
                "Update: Revised application based on new requirements"
            )
            
            # GitHub Pages should already be enabled, but get the URL
            pages_url = f"https://{self.github_username}.github.io/{repo_name}/"
            
            repo_url = repo.html_url
            
            logger.info(f"Repository update complete - URL: {repo_url}")
            return repo_url, commit_sha, pages_url
            
        except Exception as e:
            logger.error(f"Failed to update repository: {str(e)}")
            raise