FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p sources/pdf sources/prolog sources/txt chroma_db

EXPOSE 7860

CMD ["python", "app.py"]
