# backend/fastapi/Dockerfile
FROM python:3.13

ARG BACKEND_PORT
ARG SERVER_IP
ENV BACKEND_PORT=${BACKEND_PORT}
ENV SERVER_IP=${SERVER_IP}

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 애플리케이션 소스 복사 (bind mount을 사용할 경우 최신 소스는 호스트와 동기화)
COPY app/ ./
# app/

EXPOSE ${BACKEND_PORT}

# uvicorn을 통해 FastAPI 서버 실행 (app/main.py 파일이 존재한다고 가정)
CMD ["sh", "-c", "uvicorn main:app --host ${SERVER_IP} --port ${BACKEND_PORT} --reload"]
