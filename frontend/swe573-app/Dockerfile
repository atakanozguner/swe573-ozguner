FROM node:18-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm config set legacy-peer-deps true 
RUN npm i
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npx", "serve", "-s", "build"]
