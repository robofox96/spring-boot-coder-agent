# Spring Boot Java AI Dev (LangGraph + LangChain)

This project is a Backend AI Developer for Spring Boot Apps, built using [LangGraph](https://github.com/langchain-ai/langgraph) and [LangChain](https://github.com/langchain-ai/langchain) for orchestrating code generation and tool use with LLMs.

## Features

- Automated code planning and generation using LLMs
- Modular graph-based workflow for code implementation
- Tool integration for file operations and project structure management
- Error handling and build process automation

## Project Structure

- `main.py`: Entry point, defines and runs the LangGraph workflow
- `states/`: Contains state definitions for the graph
- `tools/`: Implements file and project management tools
- `nodes/`: Contains nodes for code generation, planning, and orchestration

## Requirements

- Python 3.8+
- [LangChain](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- OpenAI API key (for LLM access)

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/robofox96/spring-boot-coder-agent.git
   cd spring-boot-coder-agent

2. Install the required packages:
   ```bash
    pip install -r requirements.txt
    ```
3. Set up your OpenAI API key:
   Create a `.env` file in the root directory with the following content:
   ```plaintext
   OPENAI_API_KEY=your_openai_api_key
   ```
4. Run the application:
   ```bash
    python main.py
    ```
## Usage
You can interact with the application through the defined nodes and tools. The main workflow is orchestrated in `main.py`, where you can modify the graph to add new functionalities or change existing ones.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or features you would like to add.

## Acknowledgements
This project uses LangGraph and LangChain for advanced code generation and orchestration capabilities. Special thanks to the developers of these libraries for their contributions to the open-source community.

## Contact
For any questions or feedback, please open an issue on the GitHub repository or contact the project maintainers.
