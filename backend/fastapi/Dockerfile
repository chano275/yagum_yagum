# backend/fastapi/Dockerfile
FROM python:3.13

ARG BACKEND_PORT
ENV BACKEND_PORT=${BACKEND_PORT}

WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y netcat-openbsd && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# 애플리케이션 소스 복사 (bind mount을 사용할 경우 최신 소스는 호스트와 동기화)
COPY app/ ./

EXPOSE ${BACKEND_PORT}

RUN chmod +x ./wait-for-it.sh
CMD ["sh", "-c", "pwd && ./wait-for-it.sh mariadb:3306 -t 10 -- uvicorn main:app --host 0.0.0.0 --port ${BACKEND_PORT} --reload"]

