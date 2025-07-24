<<<<<<< HEAD
# WAXD Car Detailing Sales Agent

An intelligent AI-powered sales agent for WAXD Car Detailing Austin that handles customer conversations through SMS, manages sales pipelines, and helps book detailing services.

## 🚀 Features

- **AI-Powered Conversations**: Uses OpenAI GPT-3.5-turbo for natural, context-aware customer interactions
- **Sales Pipeline Management**: Tracks customers through different pipeline stages (New Lead → Sales → Booking)
- **GoHighLevel Integration**: Webhook support for seamless SMS integration with GoHighLevel CRM
- **Conversation State Management**: Persistent conversation history and context tracking
- **Intelligent Routing**: LangGraph-based workflow that routes conversations based on customer intent
- **Database Persistence**: SQLite database for storing conversations, messages, and customer data
- **RESTful API**: Flask webhook server for handling incoming SMS messages

## 🏗️ Architecture

The sales agent uses a state machine approach with three main nodes:

1. **SMS Handler Node**: Processes incoming messages and initializes conversation state
2. **Sales Node**: Handles sales conversations, gathers car condition information, and qualifies leads
3. **Booking Node**: Manages the booking process once customers are qualified

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- GoHighLevel account (for SMS integration)
- Flask (for webhook server)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd sales-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## 🚀 Usage

### Running the Interactive Agent

For testing and development, you can run the agent interactively:

```bash
python src/agent.py
```

This starts a command-line interface where you can simulate customer conversations.

### Running the Webhook Server

For production use with GoHighLevel integration:

```bash
python src/webhook_server.py
```

The server will start on `http://localhost:5000` with the following endpoints:

- `POST /webhook` - Main webhook endpoint for GoHighLevel SMS
- `GET /webhook/test` - Health check endpoint
- `GET /conversations/<customer_id>` - Get conversation history
- `GET /stats` - Get conversation statistics

## 🔧 Configuration

### GoHighLevel Webhook Setup

1. In your GoHighLevel account, configure a webhook to point to your server's `/webhook` endpoint
2. The webhook should send POST requests with customer data and SMS content
3. Expected webhook payload format:
   ```json
   {
     "customerId": "customer_id_here",
     "message": {
       "content": "Customer message content"
     },
     "pipeline_stage": "New Lead",
     "customer": {
       "firstName": "John",
       "lastName": "Doe"
     }
   }
   ```

### Database Configuration

The application uses SQLite by default. The database file (`sales_agent.db`) will be created automatically on first run.

## 📊 Database Schema

### Conversations Table
- `id` - Primary key
- `ghl_customer_id` - GoHighLevel customer ID
- `pipeline_stage` - Current pipeline stage
- `current_node` - Current workflow node
- `context` - JSON string with conversation context
- `created_date` - Conversation creation timestamp
- `last_updated` - Last activity timestamp
- `is_active` - Whether conversation is active

### Messages Table
- `id` - Primary key
- `conversation_id` - Foreign key to conversations
- `role` - 'user' or 'assistant'
- `content` - Message content
- `timestamp` - Message timestamp

## 🤖 AI Agent Behavior

The sales agent is designed to:

1. **Gather Information**: Ask about car condition and service needs
2. **Qualify Leads**: Determine customer interest and readiness to book
3. **Provide Information**: Share service details, pricing, and availability
4. **Facilitate Booking**: Guide customers through the booking process

The agent maintains conversation context and adapts responses based on:
- Current pipeline stage
- Previous conversation history
- Customer responses and intent
- Car condition information gathered

## 🧪 Testing

### Test Files Included

- `test_conversation_flow.py` - Test conversation workflow
- `test_database.py` - Test database operations
- `test_webhook.py` - Test webhook functionality

Run tests with:
```bash
python -m pytest test_*.py
```

### Database Viewer

Use `view_database.py` to inspect the database contents:
```bash
python view_database.py
```

## 📁 Project Structure

```
sales-agent/
├── src/
│   ├── agent.py              # Main AI agent with conversation logic
│   ├── database.py           # Database operations and models
│   ├── webhook_server.py     # Flask webhook server
│   └── send_ghl_sms.py      # GoHighLevel SMS integration
├── ghl_tokens/
│   ├── token_handler.py      # Token management
│   └── tokens.json           # Stored tokens
├── requirements.txt          # Python dependencies
├── setup.py                 # Package setup
├── test_*.py                # Test files
└── README.md               # This file
```

## 🔒 Security Considerations

- Store API keys in environment variables, never in code
- Use HTTPS in production for webhook endpoints
- Implement proper authentication for webhook endpoints
- Regularly rotate API keys
- Monitor API usage and costs

## 🚀 Deployment

### Local Development
```bash
python src/webhook_server.py
```

### Production Deployment
1. Use a production WSGI server (e.g., Gunicorn)
2. Set up reverse proxy (e.g., Nginx)
3. Use environment variables for configuration
4. Set up SSL/TLS certificates
5. Configure firewall rules

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.webhook_server:app
```

## 📈 Monitoring and Analytics

The application provides several endpoints for monitoring:

- `/stats` - Overall conversation statistics
- `/conversations/<customer_id>` - Individual customer history
- Database queries for detailed analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the test files for usage examples
- Review the database schema for data structure
- Examine the webhook server for integration details

## 🔄 Version History

- **v1.0.0** - Initial release with basic conversation flow
- Added GoHighLevel webhook integration
- Implemented database persistence
- Added LangGraph workflow management 
=======
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
>>>>>>> 6aab433614ef0c1be8d3455f6bda263b07e7b974
