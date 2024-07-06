FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir distutils
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "run.py"]
