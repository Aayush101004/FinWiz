# Use an official Node runtime as a parent image
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package and config files first to leverage Docker layer caching
# Paths are now relative to the 'frontend' directory context
COPY package.json .
COPY tailwind.config.js .
COPY postcss.config.js .

# Install dependencies
RUN npm install

# Copy the rest of the application source code
COPY . .

# The command to run the app will be provided by docker-compose

