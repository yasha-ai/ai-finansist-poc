# Deployment Guide

## Prerequisites

1. **Telegram Bot Token**
   - Create bot via @BotFather
   - Get token
   - Save to `.env` file

2. **OpenAI API Key** (optional for POC)
   - Get from https://platform.openai.com/api-keys
   - Save to `.env` file

## Local Setup

```bash
# 1. Install dependencies
npm install
cd mini-app && npm install && cd ..

# 2. Create .env file
cp .env.example .env
# Edit .env with your credentials

# 3. Initialize database
npm run db:init

# 4. Start services
npm run server  # Start API server (port 3000)
npm run bot     # Start Telegram bot (separate terminal)
npm run dev     # Start Mini App dev server (port 3001)
```

## Dokploy Deployment

### Option 1: Via Dokploy UI

1. Go to Dokploy dashboard
2. Create new application
3. Select "Git" source
4. Point to this repository
5. Set build configuration:
   - Build command: `npm run build`
   - Start command: `npm start`
6. Add environment variables (BOT_TOKEN, OPENAI_API_KEY, etc.)
7. Deploy!

### Option 2: Via Dokploy CLI

```bash
# List available projects
dokploy project list

# Create application
dokploy app create \
  --name ai-finansist-poc \
  --project <project-id> \
  --repository https://github.com/your-repo/ai-finansist-poc \
  --branch main

# Get app ID from output, then deploy
dokploy app deploy <app-id>
```

### Option 3: Manual Dokploy CLI Setup

```bash
# 1. Initialize git repository
cd ~/clawd/ai-finansist-poc
git init
git add .
git commit -m "Initial commit: AI Finansist POC"

# 2. Push to GitHub/GitLab (if needed)
# git remote add origin <your-repo-url>
# git push -u origin main

# 3. Create Dokploy app
dokploy app create \\
  --name ai-finansist-poc \\
  --project yasha-projects \\
  --build-type nixpacks \\
  --port 3000

# 4. Set environment variables
dokploy app env set <app-id> BOT_TOKEN=<your-token>
dokploy app env set <app-id> OPENAI_API_KEY=<your-key>
dokploy app env set <app-id> PORT=3000

# 5. Deploy
dokploy app deploy <app-id>
```

## Environment Variables

Required:
- `BOT_TOKEN` - Telegram bot token from @BotFather
- `PORT` - API server port (default: 3000)

Optional:
- `OPENAI_API_KEY` - For AI chat feature
- `MINI_APP_URL` - URL where Mini App is deployed

## Testing POC

1. **Test API**: `curl http://localhost:3000/api/health`
2. **Test certificates**: `curl http://localhost:3000/api/certificates`
3. **Test bot**: Send `/start` to your bot in Telegram
4. **Test Mini App**: Open `http://localhost:3001` in browser

## Production Checklist

- [ ] Set up proper domain
- [ ] Configure SSL/HTTPS
- [ ] Set BOT_TOKEN in production environment
- [ ] Set OPENAI_API_KEY (if using AI features)
- [ ] Update MINI_APP_URL to production URL
- [ ] Test payment integration
- [ ] Set up monitoring/logs
- [ ] Configure database backups
