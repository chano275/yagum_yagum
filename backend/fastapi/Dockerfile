# backend/fastapi/Dockerfile
FROM python:3.13

ARG BACKEND_PORT
ENV BACKEND_PORT=${BACKEND_PORT}

WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

ENV TZ=Asia/Seoul

# 애플리케이션 소스 복사 (bind mount을 사용할 경우 최신 소스는 호스트와 동기화)
COPY app/ ./
RUN cat ./wait-for-it.sh | tr -d '\r' > ./wait-for-it-fixed.sh && \
    mv ./wait-for-it-fixed.sh ./wait-for-it.sh && \
    chmod +x ./wait-for-it.sh
RUN chmod +x ./wait-for-it.sh

RUN apt-get update && apt-get install -y wget gnupg2
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
RUN apt-get update && apt-get install -y google-chrome-stable
RUN apt-get update && apt-get install -y libzbar0

EXPOSE ${BACKEND_PORT}
# CMD ["sh", "-c", "pwd && ./wait-for-it.sh mariadb:3306 -t 10 -- uvicorn main:app --host 0.0.0.0 --port ${BACKEND_PORT} --reload"]
CMD ["bash", "-c", "pwd && ./wait-for-it.sh mariadb:3306 -t 10 -- uvicorn main:app --host 0.0.0.0 --port ${BACKEND_PORT} --reload"]
