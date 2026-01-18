FROM python:3.9

WORKDIR /app

ARG HF_TOKEN

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p temp_sessions && chmod 777 temp_sessions

ENV HUGGINGFACEHUB_API_TOKEN=${HF_TOKEN}

EXPOSE 7860

CMD ["chainlit", "run", "app_c.py", "--host", "0.0.0.0", "--port", "7860", "-w"]
