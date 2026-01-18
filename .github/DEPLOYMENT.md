# GitHub Actions CI/CD Setup

## Автоматичний деплой на Hugging Face Spaces

Цей workflow автоматично будує Docker образ та пушить його на HF Spaces при кожному push на `main`.

### Налаштування (One-time)

1. **Перейди на GitHub:** https://github.com/ituvtu/rag-quiz/settings/secrets/actions

2. **Додай `HF_TOKEN` secret:**
   - Click "New repository secret"
   - Name: `HF_TOKEN`
   - Value: твій Hugging Face Access Token (з https://huggingface.co/settings/tokens)
   - Клацни "Add secret"

3. **Перевір, що HF Space готів:**
   - Перейди на https://huggingface.co/spaces/ituvtu/rag-quiz-demo/settings
   - Ensure owner is correct

### Як це працює

Коли ти push'иш на `main`:
1. ✅ GitHub Actions запускається
2. 🐳 Будує Docker образ з ARG HF_TOKEN
3. 📤 Пушить на `registry.hf.space`
4. 🚀 HF Spaces автоматично деплойить новий образ

### Помилки?

Дивись логи в: https://github.com/ituvtu/rag-quiz/actions

Найчастіші помилки:
- ❌ `HF_TOKEN` не встановлений → додай в Secrets
- ❌ `registry.hf.space` login failed → перевір токен
- ❌ Space не налаштований → відкрий https://huggingface.co/spaces/ituvtu/rag-quiz-demo/settings
