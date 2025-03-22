FROM python:3.12-slim

WORKDIR /app

COPY requirements_api.txt .
RUN pip install -r requirements_api.txt

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
