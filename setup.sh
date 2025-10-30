#!/bin/bash
set -e

echo "========================================"
echo " AIDA - Emergency Diagnostic Agent Setup"
echo "========================================"

# 1. Install Dependencies
echo "[1/4] Installing Python dependencies..."
pip install -r requirements.txt
echo "Dependencies installed."

# 2. Fetch Osquery Specifications
echo "[2/4] Fetching osquery specifications..."
if [ -d "osquery_data" ]; then
    echo "'osquery_data' directory already exists. Skipping clone."
else
    git clone --depth 1 --filter=blob:none --sparse https://github.com/osquery/osquery.git osquery_data
    cd osquery_data
    git sparse-checkout set specs
    cd ..
    echo "Osquery specs fetched."
fi

# 3. Download Embedding Model
echo "[3/4] Downloading embedding model (embeddinggemma-300m)..."
python3 -c "from huggingface_hub import hf_hub_download; import os; os.makedirs('models/unsloth/embeddinggemma-300m-GGUF', exist_ok=True); hf_hub_download(repo_id='unsloth/embeddinggemma-300m-GGUF', filename='embeddinggemma-300M-Q8_0.gguf', local_dir='models/unsloth/embeddinggemma-300m-GGUF')"
echo "Model downloaded."

# 4. Run Ingestion
echo "[4/4] Building knowledge base (this may take a moment)..."
python3 ingest_osquery.py
echo "Knowledge base built."

echo "========================================"
echo " Setup Complete!"
echo "========================================"
echo "You can now run the agent with:"
echo "  uvicorn main:app --reload"
echo ""
