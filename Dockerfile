FROM python:3.11-slim
WORKDIR /app
COPY requirments.txt
COPY . .
CMD ["python", "bot.py"]