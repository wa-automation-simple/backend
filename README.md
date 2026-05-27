# WhatsApp SaaS Microservices Backend

## Project Overview
A Python-based microservices architecture for a WhatsApp Business SaaS platform with the following features:
- WhatsApp warming (panasin WA)
- Bulk messaging (blast) with image support
- Auto-reply with AI integration
- Token-based AI usage with markup pricing
- Member follow-up system
- Multi-account support (multiple WhatsApp accounts in one app)
- Auto-click links for banned/unbanned recovery

## Architecture

### Services

1. **API Gateway** (`gateway/`)
   - Central entry point for all requests
   - Request routing and load balancing
   - Authentication validation
   - Rate limiting

2. **Auth Service** (`auth-service/`)
   - User authentication and authorization
   - JWT token management
   - Session handling
   - Multi-account management

3. **WhatsApp Service** (`whatsapp-service/`)
   - WhatsApp connection management
   - Multi-account support
   - Message sending/receiving
   - Auto-click link functionality
   - Warming schedule management

4. **Blast Service** (`blast-service/`)
   - Bulk message scheduling
   - Image/media attachment support
   - Campaign management
   - Delivery tracking

5. **AI Service** (`ai-service/`)
   - AI-powered auto-replies
   - Token management
   - Integration with LLM providers
   - Token balance checking

6. **Payment Service** (`payment-service/`)
   - Token top-up processing
   - Payment gateway integration
   - Pricing markup management ($3 → $10)
   - Transaction history

7. **Follow-up Service** (`followup-service/`)
   - Member follow-up scheduling
   - Reminder management
   - Engagement tracking

8. **Scheduler Service** (`scheduler-service/`)
   - Task scheduling and queuing
   - Cron job management
   - Warm-up schedule coordination

9. **Shared Library** (`shared/`)
   - Common utilities
   - Database models
   - Message schemas
   - Configuration management

## Tech Stack

- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Message Queue**: Redis/RabbitMQ
- **Database**: PostgreSQL + Redis
- **Container**: Docker & Docker Compose
- **Orchestration**: Kubernetes (optional)

## Directory Structure

```
microservices/
├── gateway/
│   ├── main.py
│   ├── routes.py
│   └── config.py
├── auth-service/
│   ├── main.py
│   ├── auth.py
│   ├── models.py
│   └── config.py
├── whatsapp-service/
│   ├── main.py
│   ├── whatsapp_manager.py
│   ├── multi_account.py
│   └── config.py
├── blast-service/
│   ├── main.py
│   ├── campaign.py
│   ├── media_handler.py
│   └── config.py
├── ai-service/
│   ├── main.py
│   ├── ai_engine.py
│   ├── token_manager.py
│   └── config.py
├── payment-service/
│   ├── main.py
│   ├── payment_processor.py
│   ├── pricing.py
│   └── config.py
├── followup-service/
│   ├── main.py
│   ├── followup_scheduler.py
│   └── config.py
├── scheduler-service/
│   ├── main.py
│   ├── task_queue.py
│   └── config.py
├── shared/
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── utils.py
│   └── config.py
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- PostgreSQL
- Redis

### Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables
4. Run with Docker Compose: `docker-compose up -d`

### Environment Variables

Each service requires specific environment variables. See individual service `config.py` files for details.

## API Documentation

Once running, access Swagger UI at:
- Gateway: `http://localhost:8000/docs`
- Individual services: `http://localhost:{port}/docs`

## Features Detail

### 1. WhatsApp Warming
Automated warm-up schedules to prevent bans:
- Gradual increase in message volume
- Random delays between messages
- Natural interaction patterns

### 2. Blast Messaging
Bulk messaging with advanced features:
- Text and image support
- Scheduled campaigns
- Personalization tokens
- Delivery reports

### 3. AI Auto-Reply
Intelligent response system:
- Context-aware responses
- Customizable AI personality
- Token-based usage
- Fallback to predefined responses

### 4. Token System
Monetization through AI tokens:
- Base cost: $3 per 1000 tokens
- Markup price: $10 per 1000 tokens
- Balance tracking
- Auto-recharge options

### 5. Follow-up System
Member engagement automation:
- Scheduled follow-ups
- Conditional triggers
- Engagement scoring

### 6. Multi-Account Support
Manage multiple WhatsApp accounts:
- Single dashboard
- Account switching
- Isolated sessions
- Per-account analytics

### 7. Auto-Click Recovery
Automatic link clicking for recovery:
- Detect ban/unban status
- Click verification links
- Retry mechanisms

## License

MIT License
