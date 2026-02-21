# AI Finansist POC

Telegram Mini App + Bot for selling financial literacy certificates with AI integration.

## Features

- 🤖 Telegram Bot (registration, notifications)
- 📱 Mini App (certificate catalog, purchase)
- 💳 Payment integration (Telegram Stars)
- 🎲 Raffle system (free giveaways)
- 🤖 AI financial advisor (OpenAI/GigaChat)

## Tech Stack

- Backend: Node.js + Express + SQLite
- Bot: Grammy (Telegram Bot Framework)
- Mini App: Next.js + React + Telegram SDK
- AI: OpenAI API
- Deploy: Dokploy

## Setup

1. Copy `.env.example` to `.env` and fill in your credentials
2. Install dependencies: `npm install`
3. Initialize database: `npm run db:init`
4. Start bot: `npm run bot`
5. Start Mini App: `npm run dev`

## Deployment

Deploy via Dokploy CLI:
```bash
dokploy app deploy <app-id>
```
