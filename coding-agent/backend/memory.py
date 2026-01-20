import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import json
from datetime import datetime

class LocalMemory:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize local memory using ChromaDB

        Args:
            persist_directory: Directory to persist the database
        """
        self.persist_directory = persist_directory

        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        try:
            self.collection = self.client.get_collection("coding_agent_memory")
        except:
            self.collection = self.client.create_collection("coding_agent_memory")

    def add_memory(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """
        Add a memory entry

        Args:
            content: The memory content
            metadata: Additional metadata

        Returns:
            Memory ID
        """
        memory_id = f"memory_{datetime.now().timestamp()}_{hash(content)}"

        # Prepare metadata
        if metadata is None:
            metadata = {}

        metadata["timestamp"] = datetime.now().isoformat()
        metadata["content_length"] = len(content)

        # Add to collection
        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[memory_id]
        )

        return memory_id

    def search_memory(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant memories

        Args:
            query: Search query
            n_results: Number of results to return

        Returns:
            List of memory entries with scores
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )

            memories = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    memory = {
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "score": 1 - (results["distances"][0][i] if results["distances"] else 0)
                    }
                    memories.append(memory)

            return memories

        except Exception as e:
            print(f"Error searching memory: {e}")
            return []

    def get_recent_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent memories

        Args:
            limit: Number of recent memories to return

        Returns:
            List of recent memory entries
        """
        try:
            # Get all memories and sort by timestamp
            all_results = self.collection.get(include=["documents", "metadatas"])

            if not all_results["documents"]:
                return []

            # Sort by timestamp (most recent first)
            memories_with_time = []
            for i, metadata in enumerate(all_results["metadatas"]):
                try:
                    timestamp = metadata.get("timestamp", "2000-01-01T00:00:00")
                    memories_with_time.append({
                        "content": all_results["documents"][i],
                        "metadata": metadata,
                        "timestamp": timestamp
                    })
                except:
                    continue

            # Sort by timestamp descending
            memories_with_time.sort(key=lambda x: x["timestamp"], reverse=True)

            return memories_with_time[:limit]

        except Exception as e:
            print(f"Error getting recent memories: {e}")
            return []

    def clear_memory(self) -> bool:
        """
        Clear all memories

        Returns:
            Success status
        """
        try:
            self.client.delete_collection("coding_agent_memory")
            self.collection = self.client.create_collection("coding_agent_memory")
            return True
        except Exception as e:
            print(f"Error clearing memory: {e}")
            return False

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics

        Returns:
            Dictionary with memory stats
        """
        try:
            count = self.collection.count()
            recent = self.get_recent_memories(1)

            stats = {
                "total_memories": count,
                "last_updated": recent[0]["timestamp"] if recent else None
            }

            return stats

        except Exception as e:
            print(f"Error getting memory stats: {e}")
            return {"error": str(e)}
