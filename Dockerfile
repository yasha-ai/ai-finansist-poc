FROM node:22-slim

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

RUN node db-init.js
RUN npx next build

ENV PORT=3000
EXPOSE 3000

CMD ["node", "server.js"]
