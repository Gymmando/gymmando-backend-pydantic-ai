FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gymmando/ ./gymmando/
COPY .env .

CMD ["uvicorn", "gymmando.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
