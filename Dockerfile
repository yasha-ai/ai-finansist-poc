FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm install --production

# Copy application files
COPY . .

# Initialize database
RUN npm run db:init

# Build Mini App
WORKDIR /app/mini-app
RUN npm install && npm run build

WORKDIR /app

EXPOSE 3000

# Start both bot and server
CMD ["npm", "start"]
