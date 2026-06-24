# Stage 1: Build the React app
FROM node:20-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine
# Copy the built website from Stage 1 to Nginx
COPY --from=build /app/dist /usr/share/nginx/html
# Copy our custom config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Support running as non-root user (nginx UID is 101 in alpine)
RUN touch /var/run/nginx.pid && \
    chown -R 101:101 /var/run/nginx.pid /usr/share/nginx/html /var/cache/nginx /var/log/nginx /etc/nginx

USER 101
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]

# Trigger initial CI/CD build

# Retry initial CI/CD build after template fix
