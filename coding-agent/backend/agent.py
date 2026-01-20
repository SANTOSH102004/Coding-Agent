import os
import asyncio
from typing import List, Tuple, Dict, Any
from langchain_community.llms import Ollama
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from tools import FileReadTool, FileWriteTool, CodeExecutionTool, TerminalTool
from memory import LocalMemory
import time

class CodingAgent:
    def __init__(self):
        # Initialize Ollama LLM
        self.llm = Ollama(model="llama3", temperature=0.1)
        
        # Initialize tools
        self.tools = [
            FileReadTool(),
            FileWriteTool(),
            CodeExecutionTool(),
            TerminalTool()
        ]
        
        # Initialize memory
        self.memory = LocalMemory()
        self.conversation_memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # System prompt for the agent
        self.system_prompt = """
        You are an expert coding assistant that can read, write, and modify code files.
        You have access to tools for file operations, code execution, and terminal commands.
        
        Your capabilities:
        - Read and analyze existing code
        - Write new code or modify existing code
        - Execute code safely to test it
        - Run terminal commands (with safety restrictions)
        
        Guidelines:
        1. Always plan your approach before taking action
        2. Use tools when needed - don't assume file contents
        3. Explain your reasoning clearly
        4. Be safe - avoid destructive operations
        5. Iterate until the task is complete
        6. Provide clear explanations of changes made
        
        When working on tasks:
        - First understand the current codebase
        - Plan the changes needed
        - Implement changes step by step
        - Test your changes
        - Explain what was done
        
        Remember: You can use multiple tools in sequence to accomplish complex tasks.
        """
        
        # Initialize the agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.conversation_memory,
            verbose=True,
            max_iterations=10,
            early_stopping_method="generate"
        )
    
    async def run_task(self, task: str, workspace_path: str = "workspace") -> Tuple[str, List[str]]:
        """
        Run a coding task using the agent
        
        Args:
            task: The coding task description
            workspace_path: Path to the workspace directory
            
        Returns:
            Tuple of (result, logs)
        """
        logs = []
        
        # Change to workspace directory
        original_cwd = os.getcwd()
        try:
            os.chdir(workspace_path)
            logs.append(f"Changed to workspace: {workspace_path}")
        except Exception as e:
            logs.append(f"Warning: Could not change to workspace {workspace_path}: {e}")
        
        try:
            # Add task to memory
            self.memory.add_memory(
                content=f"Task: {task}",
                metadata={
                    "type": "task",
                    "timestamp": time.time(),
                    "workspace": workspace_path
                }
            )
            
            # Create the full prompt
            full_prompt = f"{self.system_prompt}\n\nTask: {task}\n\nPlease complete this task step by step."
            
            # Run the agent
            logs.append("Starting agent execution...")
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                self.agent.run, 
                full_prompt
            )
            
            logs.append("Agent execution completed")
            
            # Store result in memory
            self.memory.add_memory(
                content=f"Result: {result}",
                metadata={
                    "type": "result",
                    "timestamp": time.time(),
                    "task": task
                }
            )
            
            return result, logs
            
        except Exception as e:
            error_msg = f"Error during task execution: {str(e)}"
            logs.append(error_msg)
            return error_msg, logs
            
        finally:
            # Restore original directory
            try:
                os.chdir(original_cwd)
            except:
                pass
    
    def get_memory_context(self, query: str) -> str:
        """Get relevant context from memory"""
        memories = self.memory.search_memory(query)
        if not memories:
            return ""
        
        context = "Relevant previous context:\n"
        for memory in memories:
            context += f"- {memory['content']}\n"
        return context
