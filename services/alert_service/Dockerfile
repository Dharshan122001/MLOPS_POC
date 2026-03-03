FROM python:3.10-slim

WORKDIR /app

COPY services/alert_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/alert_service/alert.py .

CMD ["python", "alert.py"]