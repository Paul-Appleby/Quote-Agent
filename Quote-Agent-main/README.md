# Auto Book

Automation suite for Go High Level (GHL) integration.

## Components

### Quote Bot
Automated quote creation in Fieldd CRM using GHL webhooks.
- [View Quote Bot Documentation](quote_bot/README.md)

### Sales Bot
SMS-based sales bot for nurturing leads in GHL.
- [View Sales Bot Documentation](sales_bot/README.md)

## Project Structure
```
auto_book/
├── quote_bot/          # Fieldd quote automation
├── sales_bot/          # GHL SMS sales bot
└── README.md          # This file
```

## Getting Started

1. Choose which bot you want to set up:
   - [Quote Bot Setup](quote_bot/README.md)
   - [Sales Bot Setup](sales_bot/README.md)

2. Follow the setup instructions in the respective bot's README

## Development

Each bot is self-contained in its own directory with its own:
- Dependencies
- Configuration
- Documentation
- Environment variables 

# Railway Deployment Instructions

## 1. Prepare Your Repo
- Ensure all code is committed to GitHub
- Add your environment variables in Railway dashboard (see .env.example)

## 2. Deploy
- Go to https://railway.app/
- Create a new project and link your GitHub repo
- Set environment variables in Railway settings
- Deploy!

## 3. Webhook Setup
- Copy your Railway app URL (e.g., https://your-app.up.railway.app/webhook)
- Set this as your webhook endpoint in GHL 