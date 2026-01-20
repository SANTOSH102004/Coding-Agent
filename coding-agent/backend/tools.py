import os
import subprocess
import tempfile
from typing import Any
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field

class FileReadTool(BaseTool):
    name = "file_read"
    description = "Read the contents of a file. Input should be the file path."

    def _run(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

class FileWriteTool(BaseTool):
    name = "file_write"
    description = "Write content to a file. Input should be 'file_path::content'"

    def _run(self, input_str: str) -> str:
        try:
            file_path, content = input_str.split('::', 1)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

class CodeExecutionTool(BaseTool):
    name = "code_execute"
    description = "Execute code safely in a sandboxed environment. Input should be the code to execute."

    def _run(self, code: str) -> str:
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Execute the code
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Clean up
            os.unlink(temp_file)
            
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR: {result.stderr}"
            
            return output
            
        except subprocess.TimeoutExpired:
            return "Code execution timed out"
        except Exception as e:
            return f"Error executing code: {str(e)}"

class TerminalTool(BaseTool):
    name = "terminal"
    description = "Run terminal commands. Input should be the command to run."

    def _run(self, command: str) -> str:
        try:
            # Safety check - prevent destructive commands
            dangerous_commands = ['rm', 'del', 'format', 'fdisk', 'mkfs']
            if any(cmd in command.lower() for cmd in dangerous_commands):
                return "Command blocked for safety reasons"
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR: {result.stderr}"
            
            return output
            
        except subprocess.TimeoutExpired:
            return "Command timed out"
        except Exception as e:
            return f"Error running command: {str(e)}"
