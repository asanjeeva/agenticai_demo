"""JIRA integration tool for MyAssistant."""

from typing import Optional
from jira import JIRA
from langchain_core.tools import tool

from ..config import get_config


def get_jira_client() -> JIRA:
    """Create and return a JIRA client instance."""
    config = get_config()
    return JIRA(
        server=config.jira_server,
        basic_auth=(config.jira_email, config.jira_api_token),
    )


@tool
def create_jira_ticket(
    summary: str,
    description: str,
    issue_type: str = "Task",
    priority: Optional[str] = None,
    labels: Optional[list[str]] = None,
    assignee: Optional[str] = None,
    story_points: Optional[int] = None,
) -> str:
    """
    Create a JIRA ticket with the specified fields.

    Args:
        summary: The ticket title/summary (required)
        description: Detailed description of the ticket (required)
        issue_type: Type of issue - Task, Bug, Story, Epic (default: Task)
        priority: Priority level - Highest, High, Medium, Low, Lowest (optional)
        labels: List of labels to apply to the ticket (optional)
        assignee: Username or email of the assignee (optional)
        story_points: Story points for estimation (optional, for Stories)

    Returns:
        A message confirming ticket creation with the ticket key
    """
    try:
        config = get_config()
        jira = get_jira_client()

        # Build the issue fields
        issue_dict = {
            "project": {"key": config.jira_project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type},
        }

        # Add optional fields if provided
        if priority:
            issue_dict["priority"] = {"name": priority}

        if labels:
            issue_dict["labels"] = labels

        if assignee:
            # Try to find user by email or username
            try:
                users = jira.search_users(query=assignee)
                if users:
                    issue_dict["assignee"] = {"accountId": users[0].accountId}
            except Exception:
                pass  # Skip assignee if user not found

        # Create the issue
        new_issue = jira.create_issue(fields=issue_dict)

        # Add story points if provided (this is typically a custom field)
        if story_points and issue_type in ["Story", "Task"]:
            try:
                # Story points field ID varies by JIRA instance
                # Common field names: customfield_10016, customfield_10026
                for field_id in ["customfield_10016", "customfield_10026", "customfield_10004"]:
                    try:
                        new_issue.update(fields={field_id: float(story_points)})
                        break
                    except Exception:
                        continue
            except Exception:
                pass  # Skip if story points field not found

        # Build response message
        result = f"Successfully created JIRA ticket: {new_issue.key}\n"
        result += f"  Summary: {summary}\n"
        result += f"  Type: {issue_type}\n"
        if priority:
            result += f"  Priority: {priority}\n"
        if labels:
            result += f"  Labels: {', '.join(labels)}\n"
        if assignee:
            result += f"  Assignee: {assignee}\n"
        if story_points:
            result += f"  Story Points: {story_points}\n"
        result += f"  URL: {config.jira_server}/browse/{new_issue.key}"

        return result

    except Exception as e:
        return f"Failed to create JIRA ticket: {str(e)}"


@tool
def search_jira_tickets(query: str, max_results: int = 10) -> str:
    """
    Search for JIRA tickets using JQL.

    Args:
        query: JQL query string or simple text search
        max_results: Maximum number of results to return (default: 10)

    Returns:
        A formatted list of matching tickets
    """
    try:
        config = get_config()
        jira = get_jira_client()

        # If it's a simple text query, convert to JQL
        if not any(keyword in query.lower() for keyword in ["=", "~", "and", "or", "order by"]):
            query = f'project = {config.jira_project_key} AND text ~ "{query}" ORDER BY created DESC'

        issues = jira.search_issues(query, maxResults=max_results)

        if not issues:
            return "No tickets found matching your query."

        result = f"Found {len(issues)} ticket(s):\n\n"
        for issue in issues:
            result += f"  {issue.key}: {issue.fields.summary}\n"
            result += f"    Status: {issue.fields.status.name}\n"
            if issue.fields.priority:
                result += f"    Priority: {issue.fields.priority.name}\n"
            result += f"    URL: {config.jira_server}/browse/{issue.key}\n\n"

        return result

    except Exception as e:
        return f"Failed to search JIRA tickets: {str(e)}"
