# Quote Bot

Automated quote creation bot for Fieldd CRM using GHL webhooks.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with the following variables:
```
FIELDD_USERNAME=your_username
FIELDD_PASSWORD=your_password
COMPANY_CITY=your_city
```

## Usage

1. Start the local agent:
```bash
python local_agent.py
```

2. The agent will:
   - Poll the Railway webhook server for new leads
   - Automatically create quotes in Fieldd CRM
   - Handle address validation and service selection

## Components

- `local_agent.py`: Main automation script
- `server.py`: Railway webhook server
- `requirements.txt`: Project dependencies 