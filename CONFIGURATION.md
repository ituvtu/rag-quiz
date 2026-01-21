# Configuration

Environment variables for runtime configuration. All settings have sensible defaults.

| Variable | Default | Description |
|----------|---------|-------------|
| `TEMP_SESSIONS_FOLDER` | `temp_sessions` | Session storage directory |
| `CONVERSATION_HISTORY_MESSAGES` | `3` | Context window for question refinement (1-10) |
| `LOG_LEVEL` | `INFO` | Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `MAX_FILE_SIZE_MB` | `50` | Maximum upload size in MB |
| `ALLOWED_FILE_TYPES` | `pdf` | Allowed file types (comma-separated) |
| `HUGGINGFACEHUB_API_TOKEN` | - | HuggingFace API token (required for LLM) |
| `HF_TOKEN` | - | Alternative HuggingFace token variable |

## Setup

```bash
copy .env.example .env
# Edit .env with deployment-specific values
```

## Production Recommendations

- Set `LOG_LEVEL=WARNING` to reduce verbosity
- Use persistent session storage instead of file system
- Set `CONVERSATION_HISTORY_MESSAGES=5` for better context
- Configure `MAX_FILE_SIZE_MB` based on your infrastructure
- Ensure `HUGGINGFACEHUB_API_TOKEN` is securely managed (e.g., via secrets manager)
