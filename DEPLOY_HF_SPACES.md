# Deploy to Hugging Face Spaces

This project is ready for deployment to **Hugging Face Spaces** - a free hosting platform for Chainlit and other ML apps.

## Quick Start

### 1. Create HF Space

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Enter:
   - **Name**: `rag-quiz` (or your choice)
   - **License**: Apache 2.0
   - **Visibility**: Public or Private
4. Click "Create Space"

### 2. Set Up Secrets

In your Space settings, add these secrets:
- **HUGGINGFACEHUB_API_TOKEN**: Your HF API token ([get here](https://huggingface.co/settings/tokens))

### 3. Deploy Code

Option A: Using Git (Recommended)

```bash
cd rag-quiz

# Add HF Space as remote
git remote add hf https://huggingface.co/spaces/USERNAME/rag-quiz

# Push code
git push -u hf main
```

Option B: Using deployment script

```bash
# Linux/Mac
bash scripts/deploy-hf.sh

# Windows
scripts\deploy-hf.bat
```

Option C: Manual upload

1. Go to your Space
2. Click "Files" tab
3. Click "Add file" → "Upload file"
4. Upload all project files except those in `.hfignore`

## What Gets Deployed

✅ **Included:**
- `app_c.py` - Main application
- `setup_core.py` - LLM initialization
- `modules/` - RAG pipeline
- `requirements.txt` - Dependencies
- `README.md` - Documentation
- `ARCHITECTURE.md` - System design
- `CONFIGURATION.md` - Config reference
- `TECH_SUMMARY.md` - Technical overview

❌ **Excluded** (via `.hfignore`):
- `Dockerfile`, `docker-compose.yml` - Not needed for HF Spaces
- `DEVELOPMENT.md`, `PRODUCTION_CHECKLIST.md` - For self-hosted only
- `.vscode/`, `.github/`, `.chainlit/` - IDE and CI/CD configs
- `temp_sessions/`, `__pycache__/` - Temporary files
- `.git/`, `.venv/` - Development artifacts

## After Deployment

Your Space will:
1. Install dependencies from `requirements.txt`
2. Start the Chainlit app automatically
3. Be accessible at: `huggingface.co/spaces/USERNAME/rag-quiz`
4. Get a public URL for sharing

## Important Notes

### File Size Limit
HF Spaces has a 50GB file size limit. This project is well under that.

### Session Storage
The `temp_sessions/` folder is automatically created at runtime and cleaned up. Don't worry about manual session management.

### API Token
Your `HUGGINGFACEHUB_API_TOKEN` is set as a Secret in the Space settings. It's:
- ✅ Never visible in code or logs
- ✅ Automatically injected at runtime
- ✅ Rotatable from Space settings

### Cold Start
The first request may take ~1-2 minutes as the space boots up. Subsequent requests are instant.

## Troubleshooting

### Space fails to load
Check logs in Space settings → "Logs" tab:
- Verify `HUGGINGFACEHUB_API_TOKEN` is set
- Check internet connection
- Verify HF token has proper permissions

### App loads but PDFs don't upload
- Check file size limits (MAX_FILE_SIZE_MB in code)
- Verify storage space available
- Check browser console for errors

### Slow performance
- HF Spaces CPU instances are for demos only
- For production, consider self-hosting with Docker
- See PRODUCTION_CHECKLIST.md for deployment options

## Update Deployment

To update your Space:

```bash
# Make changes locally
# Commit to git
git add .
git commit -m "Update: description of changes"

# Push to HF Space
git push hf main
```

The Space will auto-rebuild and deploy in ~1-2 minutes.

## Self-Hosting Alternative

For production deployment, see:
- `PRODUCTION_CHECKLIST.md` - Full deployment guide
- `Dockerfile` - Docker containerization
- `docker-compose.yml` - One-command deployment

## Support

- 📖 [HF Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- 🔗 [Chainlit Documentation](https://docs.chainlit.io)
- 💬 [HF Community Forums](https://huggingface.co/discussions)
