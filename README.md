# Legal Application System ÌøõÔ∏è

A comprehensive web application that enables citizens to file legal applications using regional speech recognition technology, powered by BHASHINI API and Azure OpenAI.

## Ìºü Features

- **Ìæ§ Voice-Powered Forms**: Fill legal forms using regional speech recognition
- **Ìºê Multi-Language Support**: Supports 12+ Indian regional languages
- **Ì¥ñ AI-Assisted**: Intelligent form validation and document analysis
- **Ì≥± Responsive Design**: Works seamlessly on desktop and mobile
- **Ì≥Ñ Document Generation**: Automated PDF generation of legal documents
- **Ì≥ä Real-time Tracking**: Track application status and progress
- **Ì¥ê Secure**: JWT authentication and data encryption

## Ìª†Ô∏è Tech Stack

### Backend
- **Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Background Tasks**: Celery
- **AI/ML**: Azure OpenAI, BHASHINI API
- **File Storage**: Azure Blob Storage

### Frontend
- **Framework**: React 18 + TypeScript
- **State Management**: Redux Toolkit
- **UI Library**: Material-UI (MUI)
- **Styling**: Styled Components
- **Build Tool**: Create React App

## Ì∫Ä Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/legal-application-system.git
   cd legal-application-system
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   ```bash
   # Copy environment files
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env.local
   
   # Edit with your API keys and configuration
   ```

5. **Database Setup**
   ```bash
   cd backend
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py seed_templates
   ```

6. **Run Development Servers**
   ```bash
   # Terminal 1 - Backend
   cd backend
   python manage.py runserver
   
   # Terminal 2 - Frontend
   cd frontend
   npm start
   
   # Terminal 3 - Celery (optional)
   cd backend
   celery -A legal_app_backend worker --loglevel=info
   ```

## Ì≥ñ API Documentation

The API documentation is available at `/docs/api/` after starting the development server.

### Key Endpoints
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `GET /api/forms/templates/` - Get form templates
- `POST /api/speech/speech-to-text/` - Convert speech to text
- `POST /api/forms/applications/` - Create legal application

## Ìºç Supported Languages

- English
- ‡§π‡§ø‡§Ç‡§¶‡•Ä (Hindi)
- ‡∞§‡±Ü‡∞≤‡±Å‡∞ó‡±Å (Telugu)
- ‡Æ§‡ÆÆ‡Æø‡Æ¥‡Øç (Tamil)
- ‡¶¨‡¶æ‡¶Ç‡¶≤‡¶æ (Bengali)
- ‡™ó‡´Å‡™ú‡™∞‡™æ‡™§‡´Ä (Gujarati)
- ‡≤ï‡≤®‡≥ç‡≤®‡≤° (Kannada)
- ‡¥Æ‡¥≤‡¥Ø‡¥æ‡¥≥‡¥Ç (Malayalam)
- ‡§Æ‡§∞‡§æ‡§†‡•Ä (Marathi)
- ‡¨ì‡¨°‡¨º‡¨ø‡¨Ü (Odia)
- ‡®™‡©∞‡®ú‡®æ‡®¨‡©Ä (Punjabi)
- ÿßÿ±ÿØŸà (Urdu)

## Ì∑™ Testing

```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend
npm test
```

## Ì∫¢ Deployment

### Using Docker
```bash
docker-compose up --build
```

### Manual Deployment
See `/docs/deployment/` for detailed deployment instructions.

## Ì¥ù Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Ì≥Ñ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Ìπè Acknowledgements

- [BHASHINI](https://bhashini.gov.in/) for speech recognition APIs
- [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service) for AI capabilities
- [Material-UI](https://mui.com/) for UI components

## Ì≥û Support

For support, email support@legalappsystem.com or join our [Discord community](https://discord.gg/legalapp).

---

**Made with ‚ù§Ô∏è for empowering citizens through technology**
