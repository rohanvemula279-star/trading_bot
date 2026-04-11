FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables will be injected by the evaluator
ENV PORT=7860

EXPOSE 7860

CMD ["python", "server.py"]
