# Sales Bot

SMS-based sales bot for nurturing leads in Go High Level (GHL).

## Project Structure
```
/sales-agent-bot/
│
├── main.py                  # FastAPI entry point (sets up routes)
├── quote_logic.py           # Handles /quote endpoint logic
├── sales_agent.py           # Handles /webhook endpoint logic
├── data_utils.py            # Shared logic (SOP lookups, customer data, Fieldd API calls)
├── config.py                # For API keys, environment variables
│
├── requirements.txt         # All project dependencies
├── .env                     # Environment variables (API keys, DB URLs)
├── README.md                # Project overview & setup instructions
│
├── /tests/                  # Unit tests for each module
│   ├── test_quote_logic.py
│   ├── test_sales_agent.py
│   └── test_data_utils.py
│
├── /db/                     # SQLite DB for SOPs, etc.
│   └── sops.db
│
└── /static/                 # Static files if needed
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with the following variables:
```
# API Keys
GHL_API_KEY=your_ghl_api_key_here
FIELDD_API_KEY=your_fieldd_api_key_here

# Webhook Settings
WEBHOOK_SECRET=your_webhook_secret_here

# Database
DATABASE_URL=sqlite:///db/sops.db

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
```

## Features

- Automated SMS responses
- Lead nurturing flows
- Conversation state tracking
- Integration with GHL API
- Webhook signature verification
- Quote creation in Fieldd
- SOP-based response generation

## Usage

1. Start the server:
```bash
python main.py
```

2. Configure GHL webhook to point to your server's `/webhook` endpoint

3. The bot will automatically:
   - Receive webhook events from GHL
   - Process incoming messages
   - Send appropriate responses
   - Update lead status in GHL
   - Create quotes in Fieldd when needed

## Development

1. Run tests:
```bash
pytest tests/
```

2. Database setup:
```bash
# The database will be created automatically when first used
# You can initialize it with sample data using:
python -c "from data_utils import init_db; init_db()"
```

## API Endpoints

- `POST /webhook` - Handle GHL webhook events
- `POST /quote` - Create quotes in Fieldd
- `GET /health` - Health check endpoint 