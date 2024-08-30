#Build the React app using Node.js
FROM node:18-alpine AS build

WORKDIR /app

COPY ./commonRessources ./commonRessources

COPY ./Frontend/package.json ./Frontend/package-lock.json ./

RUN npm install

COPY ./Frontend ./

RUN npm run build

#Serve the React app using Nginx
FROM nginx:stable-alpine

# Copy built files from the previous stage to the Nginx html directory
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY ./Frontend/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]