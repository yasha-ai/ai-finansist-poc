FROM node:22-slim

WORKDIR /app

# Install deps
COPY package*.json ./
RUN npm ci --only=production

# Copy source
COPY . .

# Init DB and build
RUN node db-init.js
RUN npx next build

EXPOSE 3001 4020

# Run API + Next.js
CMD ["sh", "-c", "node server.js & npx next start -p 4020"]
