FROM nginx:alpine

COPY ./LoadBalancer/SchedulerLoadBalancer/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
