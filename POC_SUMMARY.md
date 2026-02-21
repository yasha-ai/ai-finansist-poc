# AI Finansist POC - Summary

## What was built

### 1. Backend API (Express + SQLite)
- `/api/health` - Health check
- `/api/certificates` - List certificates
- `/api/certificates/:id` - Certificate details
- `/api/purchases` - Create purchase
- `/api/ai/chat` - AI financial advisor chat
- `/api/users/:telegram_id/purchases` - User purchase history

### 2. Telegram Bot (Grammy)
- `/start` - Welcome + Mini App button
- `/catalog` - Certificate catalog
- Raffle participation callback
- Auto user registration

### 3. Mini App (Next.js)
- 📜 Catalog tab - Browse & buy certificates
- 🎲 Raffle tab - Free certificate giveaways with countdown
- 💬 AI Chat tab - Financial advisor chat interface
- Telegram theme integration (dark mode)
- Mobile-first responsive design

### 4. Database (SQLite)
- Users, Certificates, Purchases, Raffles tables
- 3 sample certificates seeded

## Tech Stack
- Node.js 22 + Express
- Grammy (Telegram Bot)
- Next.js 16 (App Router)
- SQLite3
- OpenAI API (optional)
- Dokploy (deployment)

## Running locally
```bash
npm install
node db-init.js
node server.js &    # API on :3001
npx next dev -p 4020  # Mini App on :4020
```

## Repository
https://github.com/yasha-ai/ai-finansist-poc
