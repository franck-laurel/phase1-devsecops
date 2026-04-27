FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --upgrade "jaraco.context>=6.1.0" "wheel>=0.46.2"
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
