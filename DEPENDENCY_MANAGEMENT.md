# Dependency Management with pip-tools

## Overview

This project uses **pip-tools** for deterministic dependency management. This ensures reproducible builds and exact version control across all environments (development, testing, production).

## Files

- **requirements.in**: Base dependencies with flexible version ranges (human-readable)
- **requirements.txt**: Complete dependency tree with pinned versions (auto-generated)

## Workflow

### 1. Installing Dependencies

```bash
# Install from the pinned requirements
pip install -r requirements.txt
```

### 2. Updating Dependencies

When you need to add or update packages:

```bash
# 1. Edit requirements.in with your changes
#    Examples:
#      langchain>=0.2.0
#      new-package==1.2.3

# 2. Run pip-compile to resolve all dependencies
pip-compile requirements.in --output-file=requirements.txt --resolver=backtracking

# 3. Review the changes
git diff requirements.txt

# 4. Commit if everything looks good
git add requirements.txt
git commit -m "chore: update dependencies via pip-tools"
```

### 3. Upgrading All Dependencies

```bash
pip-compile --upgrade requirements.in --output-file=requirements.txt --resolver=backtracking
```

## Current Versions

Generated with pip-tools 7.5.2:

- **Python**: 3.10+
- **langchain**: 1.2.6
- **langchain-community**: 0.4.1
- **langchain-huggingface**: 1.0.1
- **chainlit**: 1.3.2
- **sentence-transformers**: 2.7.0
- **faiss-cpu**: 1.7.4
- **pypdf**: 4.3.1

## Version Resolution Strategy

The current setup resolves the LangChain ecosystem by:

1. Using **langchain >= 0.2.0** (requires langchain-core >= 1.0.0)
2. Using **langchain-community >= 0.2.0** (compatible with langchain 1.2.x)
3. Using **langchain-huggingface 1.0.1** (compatible with langchain-core >= 1.0.3)

This avoids the conflict between:
- Old langchain 0.1.x (requires core < 0.2.0)
- New langchain-huggingface 1.0.x (requires core >= 1.0.3)

## Installation

```bash
pip install pip-tools
```

## References

- [pip-tools Documentation](https://github.com/jazzband/pip-tools)
- [LangChain Compatibility](https://python.langchain.com/)
