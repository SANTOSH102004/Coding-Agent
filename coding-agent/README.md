# Local Coding Agent

A complete UI-based Coding Agent that runs 100% locally using Ollama. No cloud dependencies, no paid APIs - everything runs on your machine.

## Features

- 🤖 AI-powered code analysis and generation using Ollama
- 📁 File reading and writing capabilities
- 🖥️ Safe code execution in sandboxed environment
- 💾 Local memory with ChromaDB for context retention
- 🔄 Agent loop with planning and iteration
- 🖥️ Web UI built with Streamlit
- 🚀 FastAPI backend for robust API endpoints

## Architecture

```
coding-agent/
├── backend/           # FastAPI backend
│   ├── agent.py       # Main agent logic with LangChain
│   ├── tools.py       # Custom tools for file/code operations
│   ├── memory.py      # Local memory using ChromaDB
│   └── main.py        # FastAPI application
├── ui/               # Streamlit frontend
│   └── app.py        # Web interface
├── workspace/        # Working directory for projects
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Prerequisites

1. **Python 3.8+** - Download from [python.org](https://python.org)
2. **Ollama** - Install from [ollama.ai](https://ollama.ai)
3. **Git** - For cloning repositories (optional)

## Installation

### 1. Install Ollama

Download and install Ollama from the official website. Then pull the required model:

```bash
ollama pull llama3
```

### 2. Clone or Download the Project

```bash
git clone <repository-url>
cd coding-agent
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Workspace

The `workspace/` directory is where your coding projects will be stored. You can place existing code there or start fresh.

## Usage

### Starting the Backend

```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

### Starting the UI

In a new terminal:

```bash
cd ui
streamlit run app.py
```

The web interface will open at `http://localhost:8501`

### Using the Agent

1. Open the Streamlit UI in your browser
2. Enter a coding task in the text area (e.g., "Fix bugs in this Python script")
3. Set the workspace path if different from default
4. Click "Execute Task"
5. View the results and logs in the output panel

## Example Tasks

- "Fix bugs in this Python script"
- "Refactor this code to be more efficient"
- "Convert this Java code to Python"
- "Explain what this function does"
- "Add unit tests to this class"
- "Optimize this algorithm for better performance"

## Agent Capabilities

The agent can:

- **Read and analyze code** from files in the workspace
- **Write and modify code** files
- **Execute code safely** in a sandboxed environment
- **Run terminal commands** (with safety restrictions)
- **Maintain context** across multiple interactions
- **Plan and iterate** on complex tasks

## Safety Features

- Code execution is sandboxed and timed out
- Destructive terminal commands are blocked
- File operations are restricted to the workspace
- All operations are logged for transparency

## Configuration

### Ollama Model

You can change the model in `backend/agent.py`:

```python
self.llm = Ollama(model="codellama", temperature=0.1)  # Use CodeLlama instead
```

### Memory Settings

Memory persistence can be configured in `backend/memory.py` by changing the `persist_directory` parameter.

### API Ports

- Backend API: `http://localhost:8000` (configurable in `backend/main.py`)
- Streamlit UI: `http://localhost:8501` (default Streamlit port)

## Troubleshooting

### Common Issues

1. **Ollama not found**: Make sure Ollama is installed and running
2. **Model not available**: Run `ollama pull llama3` to download the model
3. **Port conflicts**: Change ports in the respective files if needed
4. **Memory errors**: Clear ChromaDB cache by deleting the `chroma_db` folder

### Logs

Check the terminal output for detailed logs. The UI also shows agent logs in the expandable section.

## Development

### Adding New Tools

Add custom tools in `backend/tools.py` by extending the `BaseTool` class from LangChain.

### Modifying Agent Behavior

Edit the system prompt and agent configuration in `backend/agent.py`.

### UI Customization

Modify `ui/app.py` to customize the Streamlit interface.

## License

This project is open source. Feel free to modify and distribute.

## Contributing

Contributions are welcome! Please submit issues and pull requests on GitHub.

---

**Built with:** Ollama, LangChain, FastAPI, Streamlit, ChromaDB
