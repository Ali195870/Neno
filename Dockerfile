FROM python:3.9-slim

WORKDIR /app
RUN pip install --no-cache-dir distutils
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "run.py"]
