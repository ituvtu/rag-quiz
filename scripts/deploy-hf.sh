#!/bin/bash
# Deploy RAG Quiz to Hugging Face Spaces

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 RAG Quiz HF Spaces Deployment${NC}"

# Check if HF CLI is installed
if ! command -v huggingface-cli &> /dev/null; then
    echo -e "${RED}❌ huggingface-cli not found. Install with:${NC}"
    echo "pip install huggingface-hub"
    exit 1
fi

# Check if .hfignore exists
if [ ! -f ".hfignore" ]; then
    echo -e "${RED}❌ .hfignore file not found${NC}"
    exit 1
fi

# Get space name from user
read -p "Enter your HF Space name (e.g., username/rag-quiz): " SPACE_NAME

if [ -z "$SPACE_NAME" ]; then
    echo -e "${RED}❌ Space name is required${NC}"
    exit 1
fi

echo -e "${YELLOW}📤 Deploying to: ${GREEN}${SPACE_NAME}${NC}"

# Use git to push with sparse checkout (respects .hfignore)
git push --force "https://huggingface.co/spaces/${SPACE_NAME}" main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo -e "${GREEN}📍 Space URL: https://huggingface.co/spaces/${SPACE_NAME}${NC}"
else
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi
