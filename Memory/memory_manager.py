import chromadb
from sentence_transformers import SentenceTransformer

class MemoryManager:
    def __init__(self, db_path="Memory/chroma_db"):
        # pre-trained model for creating embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Setup ChromaDB client. The "PersistentClient" saves the DB to disk.
        self.client = chromadb.PersistentClient(path=db_path)

        # store all agent memories in one collection.
        self.collection = self.client.get_or_create_collection(
            name="agent_memories",
            metadata={"hnsw:space": "cosine"} # cosine distance for similarity
        )

    def add_memory(self, agent_name, memory_text, turn_number):
        """Adds a memory for a specific agent to the database."""
        # Create a unique ID for the memory by combining agent name and turn number
        memory_id = f"{agent_name}_turn_{turn_number}"
        
        # Create the embedding from the memory
        embedding = self.embedding_model.encode(memory_text).tolist()

        # Add the memory to the collection
        self.collection.add(
            embeddings=[embedding],
            documents=[memory_text],
            metadatas=[{"agent": agent_name, "turn": turn_number}],
            ids=[memory_id]
        )
        print(f"INFO: Added memory for {agent_name}: '{memory_text}'")

    def retrieve_public_memories(self, query_text, n_results=5):
        """
        Retrieves the most relevant memories from ANY agent.
        This is for "situational awareness" of the conversation.
        """
        if self.collection.count() == 0:
            return []
            
        query_embedding = self.embedding_model.encode(query_text).tolist()

        # Query the collection for the most similar memories, with NO 'where' filter
        # on the agent's name. This searches everything.
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )
        
        # We get back documents and metadata. Let's combine them for clarity.
        # Example: ["Eldrin (Turn 5): The ancient texts speak of a shadow.", "Lina (Turn 6): A shadow? What kind?"]
        combined_results = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                agent = results['metadatas'][0][i]['agent']
                turn = results['metadatas'][0][i]['turn']
                combined_results.append(f"{agent} (Turn {turn}): {doc}")

        return combined_results

    def retrieve_personal_memories(self, agent_name, query_text, n_results=3):
        """
        Retrieves the most relevant memories for a SPECIFIC agent (self-reflection).
        """
        if self.collection.count() == 0:
            return []
            
        query_embedding = self.embedding_model.encode(query_text).tolist()

        # Query the collection, but filter for ONLY this agent's memories.
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"agent": agent_name} # The crucial filter for self-reflection
        )
        
        return results['documents'][0] if results['documents'] else []

    def clear_all_memories(self):
        """A utility function to reset the database for a new simulation."""
        self.client.delete_collection(name="agent_memories")
        self.collection = self.client.get_or_create_collection(name="agent_memories")