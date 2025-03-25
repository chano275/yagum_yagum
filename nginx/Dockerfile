FROM nginx:latest

# 기존 default.conf 제거 (필요 없다면)
# RUN rm /etc/nginx/conf.d/default.conf

# 커스텀 설정 복사
COPY nginx.conf /etc/nginx/conf.d/custom.conf

# Nginx 포그라운드 실행
CMD ["nginx", "-g", "daemon off;"]
