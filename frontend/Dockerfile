# Stage 1: Build the React application with Vite
FROM node:20-alpine AS builder

WORKDIR /app

# Optional build arguments to specify backend API URL during build
ARG VITE_API_BASE_URL
ARG VITE_API_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_API_URL=$VITE_API_URL

# Copy package manifests for layer caching
COPY package.json package-lock.json ./

# Install project dependencies
RUN npm ci

# Copy project source code
COPY . .

# Build production static bundle into /app/dist
RUN npm run build

# Stage 2: Serve production assets using lightweight Nginx
FROM nginx:alpine

# Remove default Nginx welcome assets
RUN rm -rf /usr/share/nginx/html/*

# Copy built static assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration for SPA routing and caching
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose HTTP port 80
EXPOSE 80

# Run Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
