import streamlit as st
import requests
import json
import os
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Local Coding Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Local Coding Agent")
st.markdown("A complete UI-based Coding Agent that runs 100% locally using Ollama")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    workspace_path = st.text_input(
        "Workspace Path",
        value="./workspace",
        help="Path to the workspace directory"
    )
    
    if st.button("Check API Status"):
        try:
            response = requests.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                st.success("✅ API is running")
            else:
                st.error("❌ API is not responding")
        except:
            st.error("❌ Cannot connect to API")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Task Input")
    
    task_input = st.text_area(
        "Enter your coding task:",
        height=200,
        placeholder="e.g., Fix bugs in this Python script\nRefactor this code to be more efficient\nAdd unit tests to this function"
    )
    
    if st.button("Execute Task", type="primary"):
        if not task_input.strip():
            st.error("Please enter a task description")
        else:
            with st.spinner("Executing task..."):
                try:
                    payload = {
                        "task": task_input,
                        "workspace_path": workspace_path
                    }
                    
                    response = requests.post(
                        f"{API_BASE_URL}/execute-task",
                        json=payload,
                        timeout=300  # 5 minutes timeout
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.last_result = result
                        st.success("Task completed!")
                    else:
                        st.error(f"API Error: {response.status_code}")
                        
                except requests.exceptions.Timeout:
                    st.error("Task timed out. Try a simpler task or check your setup.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with col2:
    st.subheader("Agent Output")
    
    if "last_result" in st.session_state:
        result = st.session_state.last_result
        
        # Result
        st.markdown("**Result:**")
        st.code(result.get("result", "No result"), language="text")
        
        # Logs
        with st.expander("View Logs"):
            logs = result.get("logs", [])
            for log in logs:
                st.text(log)
    
    else:
        st.info("Execute a task to see the output here")

# File Explorer
st.subheader("Workspace Files")

if os.path.exists(workspace_path):
    files = list(Path(workspace_path).rglob("*"))
    files = [f for f in files if f.is_file()]
    
    if files:
        file_names = [str(f.relative_to(workspace_path)) for f in files]
        selected_file = st.selectbox("Select a file to view:", file_names)
        
        if selected_file:
            file_path = Path(workspace_path) / selected_file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                st.code(content, language=get_language_from_extension(selected_file))
                
                # Edit functionality
                if st.button(f"Edit {selected_file}"):
                    st.session_state.edit_file = selected_file
                    st.session_state.edit_content = content
                    
            except Exception as e:
                st.error(f"Error reading file: {e}")
    else:
        st.info("No files found in workspace")
else:
    st.warning(f"Workspace directory '{workspace_path}' does not exist")

# Edit file modal
if "edit_file" in st.session_state:
    with st.form("edit_form"):
        st.subheader(f"Editing: {st.session_state.edit_file}")
        
        new_content = st.text_area(
            "File Content:",
            value=st.session_state.edit_content,
            height=400
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Save Changes"):
                try:
                    file_path = Path(workspace_path) / st.session_state.edit_file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    st.success("File saved successfully!")
                    del st.session_state.edit_file
                    del st.session_state.edit_content
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving file: {e}")
        
        with col2:
            if st.form_submit_button("Cancel"):
                del st.session_state.edit_file
                del st.session_state.edit_content
                st.rerun()

# Footer
st.markdown("---")
st.markdown("""
**Local Coding Agent** - Powered by Ollama, LangChain, and FastAPI

Features:
- 🤖 AI-powered code analysis and generation
- 📁 File reading and writing
- 🖥️ Safe code execution
- 💾 Local memory with ChromaDB
- 🔄 Agent loop with planning and iteration
""")

def get_language_from_extension(filename: str) -> str:
    """Get programming language from file extension"""
    ext = Path(filename).suffix.lower()
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.md': 'markdown',
        '.sql': 'sql',
        '.sh': 'bash',
        '.yml': 'yaml',
        '.yaml': 'yaml'
    }
    return language_map.get(ext, 'text')
