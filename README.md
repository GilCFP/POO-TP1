# Casino CRM - Django + React Web Application

A comprehensive Customer Relationship Management (CRM) system for casinos, built with Django REST API backend and React frontend.

## 🏗️ Project Structure

```
POO-TP1/
├── backend/                    # Django REST API
│   ├── casino_crm/            # Main Django project
│   │   ├── settings.py        # Django configuration
│   │   ├── urls.py           # URL routing
│   │   └── ...
│   ├── crm/                   # CRM Django app
│   │   ├── models.py         # Database models (Customer, GameSession)
│   │   ├── views.py          # API views
│   │   ├── serializers.py    # DRF serializers
│   │   ├── urls.py          # App URL routing
│   │   └── admin.py         # Django admin configuration
│   ├── manage.py             # Django management script
│   └── requirements.txt      # Python dependencies
├── frontend/                  # React SPA
│   ├── src/                  # React source code
│   ├── public/               # Static assets
│   ├── package.json          # Node.js dependencies
│   └── vite.config.js       # Vite configuration
├── docker-compose.yml        # PostgreSQL database
├── .env.example             # Environment variables template
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Docker & Docker Compose
- PostgreSQL (via Docker)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd POO-TP1
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start PostgreSQL Database

```bash
docker-compose up -d
```

### 4. Set Up Django Backend

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start Django development server
python manage.py runserver
```

### 5. Set Up React Frontend

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start React development server
npm run dev
```

### 6. Access the Application

- **React Frontend**: http://localhost:5173
- **Django API**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/admin/
- **API Health Check**: http://localhost:8000/api/health/

## 🎯 Features

### Backend (Django REST API)
- **Customer Management**: CRUD operations for casino customers
- **Game Session Tracking**: Record and manage gaming sessions
- **REST API**: Full RESTful API with Django REST Framework
- **PostgreSQL Database**: Robust database with proper relationships
- **Django Admin**: Web-based administration interface
- **CORS Support**: Configured for React frontend integration

### Frontend (React SPA)
- **Modern React**: Built with Vite for fast development
- **API Integration**: Axios for Django API communication
- **Responsive Design**: Mobile-friendly interface
- **Component-based**: Modular React architecture

### Database Models
- **Customer**: First name, last name, email, phone, customer type (VIP/Regular/Premium), registration date, total spent
- **GameSession**: Customer reference, game type, start/end time, amounts bet/won

## 🛠️ Development

### Django Commands

```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

### React Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### API Endpoints

- `GET /api/health/` - API health check
- `GET /api/customers/` - List customers
- `POST /api/customers/` - Create customer
- `GET /api/customers/{id}/` - Get customer details
- `PUT /api/customers/{id}/` - Update customer
- `DELETE /api/customers/{id}/` - Delete customer
- `GET /api/game-sessions/` - List game sessions
- `POST /api/game-sessions/` - Create game session

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=casino_crm
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### Database Configuration

The application is configured to use PostgreSQL. The Docker Compose file provides a ready-to-use PostgreSQL instance.

## 🧪 Testing

```bash
# Run Django tests
cd backend
python manage.py test

# Run React tests
cd frontend
npm test
```

## 📦 Production Deployment

### Django Production Settings

1. Set `DEBUG=False` in environment variables
2. Configure proper `SECRET_KEY`
3. Set up proper `ALLOWED_HOSTS`
4. Configure static file serving
5. Use a production database

### React Production Build

```bash
cd frontend
npm run build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
