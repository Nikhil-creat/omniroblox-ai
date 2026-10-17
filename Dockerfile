FROM python:3.11-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY data ./data
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
