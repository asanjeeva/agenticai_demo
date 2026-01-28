# MyAssistant

An agentic AI assistant that helps you create JIRA tickets and commit code to GitHub using natural language.

## Features

- **JIRA Integration**: Create tickets from natural language descriptions with full field support (summary, description, type, priority, labels, assignee, story points)
- **GitHub Integration**: Commit files to repositories, list repos, and read file contents
- **Natural Language Processing**: Powered by GPT-4 via LangChain/LangGraph
- **Interactive CLI**: Beautiful terminal interface with rich formatting

## Prerequisites

- Python 3.10+
- OpenAI API key
- JIRA account with API token
- GitHub personal access token

## Installation

1. Clone or navigate to the project directory:
   ```bash
   cd /Users/architsanjeeva/MyAssistant
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

5. Edit `.env` with your credentials (see Configuration section below)

## Configuration

Edit the `.env` file with your credentials:

### OpenAI
- `OPENAI_API_KEY`: Your OpenAI API key from https://platform.openai.com/api-keys

### JIRA
- `JIRA_SERVER`: Your JIRA instance URL (e.g., `https://yourcompany.atlassian.net`)
- `JIRA_EMAIL`: Your JIRA account email
- `JIRA_API_TOKEN`: Generate at https://id.atlassian.com/manage-profile/security/api-tokens
- `JIRA_PROJECT_KEY`: Default project key for tickets (e.g., `PROJ`)

### GitHub
- `GITHUB_TOKEN`: Personal access token from https://github.com/settings/tokens
  - Required scopes: `repo` (for private repos) or `public_repo` (for public only)

## Usage

Run the assistant:

```bash
python -m myassistant
```

Or after installing with pip:
```bash
pip install -e .
myassistant
```

### Example Commands

**Creating JIRA Tickets:**
```
You: Create a high priority bug ticket for login page not loading on mobile
You: Log a story to implement user authentication with 5 story points
You: Create a task to update documentation, assign to john@company.com
```

**GitHub Operations:**
```
You: List my repositories
You: Commit this Python code to user/repo: def hello(): print("Hello")
You: Show me the README.md from user/repo
```

**Other Commands:**
- `/help` - Show help message
- `/reset` - Clear conversation history
- `/quit` or `/exit` - Exit the assistant

## Project Structure

```
MyAssistant/
├── myassistant/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # CLI entry point
│   ├── agent.py             # LangGraph agent definition
│   ├── config.py            # Configuration management
│   └── tools/
│       ├── __init__.py      # Tools package
│       ├── jira_tool.py     # JIRA integration
│       └── github_tool.py   # GitHub integration
├── requirements.txt         # Python dependencies
├── setup.py                 # Package setup
├── .env.example             # Environment template
└── README.md                # This file
```

## How It Works

1. **User Input**: You describe what you want in natural language
2. **AI Processing**: GPT-4 interprets your request and extracts relevant information
3. **Tool Execution**: The agent calls the appropriate tools (JIRA/GitHub APIs)
4. **Response**: Results are displayed in a formatted output

The agent uses LangGraph to manage the conversation flow and tool execution, allowing for multi-step interactions when needed.

## Troubleshooting

**"Missing required environment variables"**
- Ensure you've copied `.env.example` to `.env` and filled in all values

**JIRA authentication failed**
- Verify your JIRA API token is valid
- Check that your email matches the JIRA account

**GitHub permission denied**
- Ensure your token has the `repo` scope
- Check that you have write access to the repository

**OpenAI rate limit**
- Wait a moment and try again
- Consider upgrading your OpenAI plan for higher limits
