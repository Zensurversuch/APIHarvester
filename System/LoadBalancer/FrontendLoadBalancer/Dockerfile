FROM nginx:alpine

COPY ./LoadBalancer/FrontendLoadBalancer/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
