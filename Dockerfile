FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p temp_sessions && chmod 777 temp_sessions

EXPOSE 7860

CMD ["chainlit", "run", "app_c.py", "--host", "0.0.0.0", "--port", "7860"]
