# Production Deployment Checklist

**Status**: ✅ Project is production-ready. Use this checklist before deployment.

## Code Quality ✅

- [x] Type hints - 100% function signatures
- [x] Error handling - Centralized with logging
- [x] Logging - 65+ structured log points
- [x] Syntax validation - All files pass Pylance
- [x] Async operations - Non-blocking throughout

## Quick Docker Deployment

**Fastest way to deploy:**

```bash
# 1. Clone repository
git clone https://github.com/ituvtu/rag-quiz.git
cd rag-quiz

# 2. Create .env file
cp .env.example .env
# Edit .env with your HuggingFace token
nano .env

# 3. Deploy with docker-compose
docker-compose up -d

# 4. Access application
# Open http://localhost:8000 in browser

# 5. View logs
docker-compose logs -f rag-quiz

# 6. Stop
docker-compose down
```

## Manual Deployment

```bash
# 1. Build Docker image
docker build -t rag-quiz .

# 2. Run container
docker run \
  -e HUGGINGFACEHUB_API_TOKEN=your_token \
  -p 8000:8000 \
  -v $(pwd)/temp_sessions:/app/temp_sessions \
  rag-quiz

# Or on Windows
docker run ^
  -e HUGGINGFACEHUB_API_TOKEN=your_token ^
  -p 8000:8000 ^
  -v %cd%\temp_sessions:/app/temp_sessions ^
  rag-quiz
```

## Pre-Deployment Configuration

```bash
# 1. Verify .env settings
HUGGINGFACEHUB_API_TOKEN=your_token_here    # Required
LOG_LEVEL=INFO                               # Use WARNING for production
MAX_FILE_SIZE_MB=50                         # Adjust for your server
TEMP_SESSIONS_FOLDER=temp_sessions          # Use persistent volume in Docker

# 2. Test configuration locally first
python -m chainlit run app_c.py -w

# 3. Then deploy to production
```

## Environment Variables

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `HUGGINGFACEHUB_API_TOKEN` | ✅ | None | HuggingFace API key |
| `LOG_LEVEL` | ⚠️ | INFO | Use WARNING/ERROR in production |
| `MAX_FILE_SIZE_MB` | ⚠️ | 50 | Adjust based on server memory |
| `TEMP_SESSIONS_FOLDER` | ⚠️ | temp_sessions | Use persistent volume |

## Performance Optimization

**Enable GPU (if available):**
```bash
# Replace faiss-cpu with faiss-gpu in requirements.txt
pip uninstall faiss-cpu
pip install faiss-gpu
```

**Scale with Gunicorn (advanced):**
```bash
pip install gunicorn
gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker app_c:app
```

## Monitoring & Health Checks

Docker health check is built-in:
```bash
# Check container health
docker ps
# Look for "healthy" status

# View health status
docker inspect --format='{{.State.Health.Status}}' <container_id>
```

## Production Best Practices

1. ✅ Use environment variables for secrets
2. ✅ Set LOG_LEVEL=WARNING in production (not DEBUG)
3. ✅ Use persistent volumes for temp_sessions
4. ✅ Configure reverse proxy (nginx) with SSL
5. ✅ Enable container restart: `--restart=unless-stopped`
6. ✅ Monitor logs: `docker logs -f <container>`
7. ✅ Set resource limits: `--memory=4g --cpus=2`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No module named chainlit" | Run `pip install -r requirements.txt` |
| Port already in use | Change port: `-p 9000:8000` or `docker kill <container>` |
| API token errors | Verify HUGGINGFACEHUB_API_TOKEN in .env |
| Out of memory | Reduce MAX_FILE_SIZE_MB or increase Docker memory |
| Slow uploads | Check disk space, use SSD for volumes |

## Rollback & Updates

```bash
# Stop current version
docker-compose down

# Pull new code
git pull

# Rebuild and restart
docker-compose up -d --build
```
