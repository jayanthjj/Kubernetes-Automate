FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/build/deps -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /build/deps /usr/local/lib/python3.12/site-packages/
COPY main.py .
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]