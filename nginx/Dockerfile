FROM nginx:latest

RUN mkdir /conf
COPY ./nginx.conf /conf/nginx.conf

EXPOSE 80
EXPOSE 443

CMD ["nginx", "-c", "/conf/nginx.conf", "-g", "daemon off;"]