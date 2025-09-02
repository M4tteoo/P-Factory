# AI Persona Factory

## 🎭 An AI Agent Simulation with LLM-Driven Personas and a Dungeon Master

This project explores the fascinating world of agentic AI by simulating a social interaction between AI-driven personas. Each agent has a unique personality, role, and goal, and they converse naturally, guided by an AI Dungeon Master. The simulation leverages Retrieval-Augmented Generation (RAG) for long-term memory, ensuring coherent and contextually rich interactions.

## ✨ Features

*   **LLM-Powered Agents:** Each character is an AI agent driven by a local Large Language Model (LLM) (via Ollama).
*   **Rich Personas:** Agents are defined with detailed `name`, `role`, `personality`, `goal`, `backstory`, `current_state`, and `relationships` for nuanced behavior.
*   **AI Dungeon Master (DM):** An intelligent orchestrator that:
    *   Decides which agent speaks next, ensuring natural conversational flow.
    *   Introduces narrative events and environmental changes.
    *   Prioritizes answering direct questions to maintain coherence.
    *   Manages turns and ensures fair participation.
*   **Retrieval-Augmented Generation (RAG):** Agents and the DM utilize a ChromaDB vector store for:
    *   **Long-Term Memory:** Storing past thoughts and dialogue.
    *   **Contextual Retrieval:** Recalling relevant public and personal memories to inform current decisions.
*   **Streamlit UI:** An interactive web interface to visualize the conversation log, agent profiles, and control the simulation turn by turn.
*   **Local-First:** Designed to run entirely locally using Ollama, offering privacy and control over models.

## 🚀 Getting Started

Follow these steps to set up and run your AI Persona Factory.

### 1. Prerequisites

*   **Python 3.8+:** Ensure you have Python installed.
*   **Ollama:** Install Ollama to run local LLMs.
    *   Download from: [ollama.com](https://ollama.com/)
    *   Once installed, pull a model (e.g., Mistral):
        ```bash
        ollama pull mistral
        ```
        (You can choose other models like `phi3`, `llama2`, etc., but `mistral` is a good starting point.)
*   **Git:** For cloning the repository.

### 2. Clone the Repository

git clone https://github.com/M4tteoo/P-Factory 
cd P-Factory 

### 3. Set up Python Environment
Its recommended to use a virtual environment:

`python -m venv .venv`
`source .venv/bin/activate # On Windows: .venv\Scripts\activate`
`pip install -r requirements.txt`

### 4. Create requirements.txt
In your project root, create a file named requirements.txt with the following content:
requests
streamlit
chromadb
sentence-transformers

### 5. Run the Streamlit UI
Once all dependencies are installed and Ollama is running with a model, start the Streamlit application:
`streamlit run UI.py`
This will open the simulation in your web browser.

### 🎮 How to Use
Agent Profiles (Sidebar): View detailed information about each AI agent.
Conversation: The main area displays the ongoing dialogue and DM narrations.
Controls:
▶️ Advance 1 Turn: Progresses the simulation by one DM decision (which might lead to an agent speaking, a narration, or a pause).
🔄 Reset Simulation: Clears the conversation, memories, and resets agents to their initial state.
### ⚙️ Configuration
Config/agents.json: Define your AI personas here. Customize name, role, personality, goal, backstory, current_state, and relationships.
Simulation/llm_api.py: Modify the model parameter in the call_local_llm function to change the LLM model used (e.g., from mistral to phi3).
Memory/chroma_db: This directory stores the persistent ChromaDB database. It will be created automatically upon first run.
### 🤝 Contributing
This project is a personal exploration of agentic AI. Feel free to fork the repository, experiment, and share your own improvements!
### 💡 Future Enhancements (Ideas)
Spatial Awareness: Implement a visual map (e.g., via Streamlit) where agents can move, explore, and interact with locations and objects.
Goal Tracking & Resolution: More robust mechanics for agents to pursue and complete their goals, potentially with conflict resolution.
Dynamic current_state updates: Allow agents to update their own emotional or mental state based on interactions.
Advanced Event System: DM introduces more complex plot twists or quests.
Resource Management: Agents manage resources (e.g., food, tools) affecting their decisions.


