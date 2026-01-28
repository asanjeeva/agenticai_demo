"""LangGraph agent for MyAssistant."""

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from .config import get_config
from .tools.jira_tool import create_jira_ticket, search_jira_tickets
from .tools.github_tool import commit_to_github, list_repositories, get_file_from_github, commit_local_file_to_github


# Define the agent state
class AgentState(TypedDict):
    """State for the agent graph."""
    messages: Annotated[list[BaseMessage], add_messages]


# System prompt for the agent
SYSTEM_PROMPT = """You are MyAssistant, an AI agent that helps users with JIRA and GitHub tasks.

You have the following capabilities:

**JIRA Operations:**
- Create tickets with full field support (summary, description, type, priority, labels, assignee, story points)
- Search for existing tickets

**GitHub Operations:**
- List repositories
- Commit files to repositories (provide content directly)
- **IMPORTANT: Commit LOCAL files from the user's machine to repositories using the `commit_local_file_to_github` tool - YOU CAN read local files!**
- Read files from repositories

**Guidelines:**
1. For JIRA tickets, extract as much information as possible from the user's natural language request:
   - Identify the ticket type (Bug, Task, Story, Epic) from context
   - Infer priority from urgency words (critical, urgent, important, etc.)
   - Extract any mentioned labels or tags
   - Note any assignee mentions

2. For GitHub commits:
   - If the user provides a LOCAL FILE PATH (e.g., /Users/...), use the `commit_local_file_to_github` tool to read and commit it
   - Ask for the repository name if not provided
   - Confirm the commit message

3. Be concise and helpful. Execute actions directly when the user provides clear instructions.

4. If you're unsure about any details, ask for clarification.

Remember: You CAN access local files on the user's machine using the commit_local_file_to_github tool. Use it when users want to commit files from their local filesystem."""


def create_agent():
    """Create and return the LangGraph agent."""
    config = get_config()

    # Initialize the LLM
    llm = ChatOpenAI(
        model="gpt-4-turbo-preview",
        api_key=config.openai_api_key,
        temperature=0.1,
    )

    # Define tools
    tools = [
        create_jira_ticket,
        search_jira_tickets,
        commit_to_github,
        commit_local_file_to_github,
        list_repositories,
        get_file_from_github,
    ]

    # Bind tools to the LLM
    llm_with_tools = llm.bind_tools(tools)

    # Create a tools lookup dictionary
    tools_by_name = {tool.name: tool for tool in tools}

    # Define the tool node function
    def tool_node(state: AgentState) -> AgentState:
        """Execute tools based on the last message's tool calls."""
        messages = state["messages"]
        last_message = messages[-1]

        tool_messages = []
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]

                if tool_name in tools_by_name:
                    try:
                        result = tools_by_name[tool_name].invoke(tool_args)
                        tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_id))
                    except Exception as e:
                        tool_messages.append(ToolMessage(content=f"Error: {str(e)}", tool_call_id=tool_id))
                else:
                    tool_messages.append(ToolMessage(content=f"Tool {tool_name} not found", tool_call_id=tool_id))

        return {"messages": tool_messages}

    # Define the agent node
    def agent_node(state: AgentState) -> AgentState:
        """Process the current state and generate a response."""
        messages = state["messages"]

        # Add system message if not present
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    # Define the routing function
    def should_continue(state: AgentState) -> str:
        """Determine whether to continue to tools or end."""
        messages = state["messages"]
        last_message = messages[-1]

        # If there are tool calls, route to tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"

        # Otherwise, end
        return END

    # Build the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)

    # Set entry point
    workflow.set_entry_point("agent")

    # Add edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END,
        },
    )
    workflow.add_edge("tools", "agent")

    # Compile the graph
    return workflow.compile()


class MyAssistantAgent:
    """Wrapper class for the MyAssistant agent."""

    def __init__(self):
        """Initialize the agent."""
        self.graph = create_agent()
        self.messages: list[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)]

    def chat(self, user_message: str) -> str:
        """
        Send a message to the agent and get a response.

        Args:
            user_message: The user's input message

        Returns:
            The agent's response
        """
        # Add user message
        self.messages.append(HumanMessage(content=user_message))

        # Run the graph
        result = self.graph.invoke({"messages": self.messages})

        # Update messages with the full conversation
        self.messages = result["messages"]

        # Get the last AI message
        for message in reversed(result["messages"]):
            if isinstance(message, AIMessage) and message.content:
                return message.content

        return "I apologize, but I couldn't generate a response. Please try again."

    def reset(self):
        """Reset the conversation history."""
        self.messages = [SystemMessage(content=SYSTEM_PROMPT)]
