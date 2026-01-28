"""GitHub integration tool for MyAssistant."""

from typing import Optional
from github import Github, GithubException
from langchain_core.tools import tool

from ..config import get_config


def get_github_client() -> Github:
    """Create and return a GitHub client instance."""
    config = get_config()
    return Github(config.github_token)


@tool
def list_repositories(include_private: bool = True) -> str:
    """
    List all repositories accessible to the authenticated user.

    Args:
        include_private: Whether to include private repositories (default: True)

    Returns:
        A formatted list of repositories
    """
    try:
        github = get_github_client()
        user = github.get_user()

        repos = []
        for repo in user.get_repos():
            if not include_private and repo.private:
                continue
            repos.append(repo)

        if not repos:
            return "No repositories found."

        result = f"Found {len(repos)} repository(ies):\n\n"
        for repo in repos[:20]:  # Limit to 20 repos
            visibility = "Private" if repo.private else "Public"
            result += f"  {repo.full_name} ({visibility})\n"
            if repo.description:
                result += f"    {repo.description[:60]}...\n" if len(repo.description or "") > 60 else f"    {repo.description}\n"

        if len(repos) > 20:
            result += f"\n  ... and {len(repos) - 20} more repositories"

        return result

    except GithubException as e:
        return f"Failed to list repositories: {str(e)}"


@tool
def commit_to_github(
    repo_name: str,
    file_path: str,
    content: str,
    commit_message: str,
    branch: str = "main",
) -> str:
    """
    Commit a file to a GitHub repository.

    Args:
        repo_name: Full repository name (e.g., 'username/repo')
        file_path: Path where the file should be created/updated in the repo
        content: The content of the file to commit
        commit_message: The commit message
        branch: Branch to commit to (default: main)

    Returns:
        A message confirming the commit with the commit SHA
    """
    try:
        github = get_github_client()
        repo = github.get_repo(repo_name)

        # Check if file already exists
        try:
            existing_file = repo.get_contents(file_path, ref=branch)
            # Update existing file
            result = repo.update_file(
                path=file_path,
                message=commit_message,
                content=content,
                sha=existing_file.sha,
                branch=branch,
            )
            action = "Updated"
        except GithubException:
            # Create new file
            result = repo.create_file(
                path=file_path,
                message=commit_message,
                content=content,
                branch=branch,
            )
            action = "Created"

        commit_sha = result["commit"].sha[:7]

        return (
            f"Successfully committed to GitHub!\n"
            f"  Repository: {repo_name}\n"
            f"  Branch: {branch}\n"
            f"  File: {file_path}\n"
            f"  Action: {action}\n"
            f"  Commit: {commit_sha}\n"
            f"  Message: {commit_message}\n"
            f"  URL: https://github.com/{repo_name}/blob/{branch}/{file_path}"
        )

    except GithubException as e:
        return f"Failed to commit to GitHub: {str(e)}"


@tool
def commit_local_file_to_github(
    local_file_path: str,
    repo_name: str,
    repo_file_path: str,
    commit_message: str,
    branch: str = "main",
) -> str:
    """
    Read a local file from the user's machine and commit it to a GitHub repository.

    Args:
        local_file_path: Absolute path to the local file to commit (e.g., '/Users/user/project/file.py')
        repo_name: Full repository name (e.g., 'username/repo')
        repo_file_path: Path where the file should be created/updated in the repo (e.g., 'src/file.py')
        commit_message: The commit message
        branch: Branch to commit to (default: main)

    Returns:
        A message confirming the commit with the commit SHA
    """
    import os

    # Read the local file
    try:
        if not os.path.exists(local_file_path):
            return f"Error: Local file not found: {local_file_path}"

        if not os.path.isfile(local_file_path):
            return f"Error: Path is not a file: {local_file_path}"

        with open(local_file_path, "r", encoding="utf-8") as f:
            content = f.read()

    except Exception as e:
        return f"Error reading local file: {str(e)}"

    # Commit to GitHub
    try:
        github = get_github_client()
        repo = github.get_repo(repo_name)

        # Check if file already exists
        try:
            existing_file = repo.get_contents(repo_file_path, ref=branch)
            # Update existing file
            result = repo.update_file(
                path=repo_file_path,
                message=commit_message,
                content=content,
                sha=existing_file.sha,
                branch=branch,
            )
            action = "Updated"
        except GithubException:
            # Create new file
            result = repo.create_file(
                path=repo_file_path,
                message=commit_message,
                content=content,
                branch=branch,
            )
            action = "Created"

        commit_sha = result["commit"].sha[:7]
        file_name = os.path.basename(local_file_path)

        return (
            f"Successfully committed local file to GitHub!\n"
            f"  Local file: {local_file_path}\n"
            f"  Repository: {repo_name}\n"
            f"  Branch: {branch}\n"
            f"  Repo path: {repo_file_path}\n"
            f"  Action: {action}\n"
            f"  Commit: {commit_sha}\n"
            f"  Message: {commit_message}\n"
            f"  URL: https://github.com/{repo_name}/blob/{branch}/{repo_file_path}"
        )

    except GithubException as e:
        return f"Failed to commit to GitHub: {str(e)}"


@tool
def get_file_from_github(
    repo_name: str,
    file_path: str,
    branch: str = "main",
) -> str:
    """
    Get the contents of a file from a GitHub repository.

    Args:
        repo_name: Full repository name (e.g., 'username/repo')
        file_path: Path to the file in the repository
        branch: Branch to read from (default: main)

    Returns:
        The contents of the file
    """
    try:
        github = get_github_client()
        repo = github.get_repo(repo_name)

        file_content = repo.get_contents(file_path, ref=branch)

        if isinstance(file_content, list):
            return f"Error: {file_path} is a directory, not a file."

        content = file_content.decoded_content.decode("utf-8")

        return (
            f"File: {file_path}\n"
            f"Repository: {repo_name}\n"
            f"Branch: {branch}\n"
            f"---\n{content}"
        )

    except GithubException as e:
        return f"Failed to get file from GitHub: {str(e)}"
