"""Setup script for MyAssistant."""

from setuptools import setup, find_packages

setup(
    name="myassistant",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.1.0",
        "langchain-openai>=0.0.5",
        "langgraph>=0.0.40",
        "openai>=1.0.0",
        "jira>=3.5.0",
        "PyGithub>=2.1.0",
        "python-dotenv>=1.0.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "myassistant=myassistant.main:main",
        ],
    },
    python_requires=">=3.10",
)
