# frontend/react-native/Dockerfile
FROM node:18-alpine

ARG FRONTEND_METRO_PORT
ARG FRONTEND_EXPO_PORT
ENV FRONTEND_METRO_PORT=${FRONTEND_METRO_PORT}
ENV FRONTEND_EXPO_PORT=${FRONTEND_EXPO_PORT}

WORKDIR /app

# package.json과 package-lock.json을 먼저 복사하여 의존성 설치
COPY package.json package-lock.json ./
RUN npm install

# 전체 소스 복사
COPY . .

EXPOSE ${FRONTEND_METRO_PORT} ${FRONTEND_EXPO_PORT}
# CMD ["npx", "expo", "start", "--web"]
