# RuneScape Wiki Project

This project contains tools for analyzing and querying RuneScape Wiki content.

## RAG Chatbot

A simple RAG (Retrieval-Augmented Generation) chatbot that answers questions about RuneScape using wiki content.

### Quick Start

1. **Create and activate virtual environment:**
   ```bash
   cd Applications/Genre_Analysis
   python3 -m venv .venv        # Run this once
   
   # Run this each time to activate:
   source .venv/bin/activate    # On WSL/Linux
   ```

2. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Install and start Ollama** (in a separate terminal):
   
   **Option A: Install via snap (WSL/Linux):**
   ```bash
   sudo snap install ollama
   ollama serve
   ollama pull llama3.1:8b
   ```

   
   **Note:** Keep `ollama serve` running in a separate terminal while using the chatbot.

4. **Build the index** (one-time setup):
   ```bash
   python indexer.py
   ```

5. **Run the chatbot:**
   
   ```bash
   python chatbot_cli.py
   ```

   Startup takes a while since it is a local model, so some example prompts from testing will also be provided in the final report. 