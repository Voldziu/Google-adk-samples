#!/bin/bash
echo "Starting deployment preparation..."
if [ -d "gcloud_deploy" ]; then
    echo "Cleaning gcloud_deploy directory (preserving main.py)..."
    find gcloud_deploy -mindepth 1 ! -name 'main.py' ! -name 'dockerfile' -delete
fi

echo "Creating new deployment structure..."
mkdir -p gcloud_deploy

AGENTS=("llm_auditor" "marketing_agency" "rag" "travel_concierge" "short_movie")

# Copy each agent
for agent in "${AGENTS[@]}"; do
    if [ -d "$agent" ]; then
        echo "Processing $agent..."
        
        # Create agent directory in deployment
        mkdir -p "gcloud_deploy/$agent"
        
        # Copy source_code contents to agent directory
        if [ -d "$agent/$agent" ]; then
            cp -r "$agent/$agent/"* "gcloud_deploy/$agent/"
        fi
        
        echo "  ✓ $agent copied"
    else
        echo "  ✗ Warning: $agent directory not found"
    fi
done

# Merge all packages
cd gcloud_deploy
uv venv --python 3.11 --clear
cd ..
source gcloud_deploy/.venv/bin/activate

# Install all agents
for agent in "${AGENTS[@]}"; do
  uv pip install -e "./${agent}"
done

uv pip list

uv pip freeze | grep -v "^-e" > gcloud_deploy/requirements.txt



