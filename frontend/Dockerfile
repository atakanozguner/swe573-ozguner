FROM node:16

# Set working directory for frontend
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the Svelte app code and build
COPY . .
RUN npm run build

# Expose the frontend port
EXPOSE 5000

# Serve the Svelte app
CMD ["npx", "serve", "-s", "public", "-l", "5000"]
