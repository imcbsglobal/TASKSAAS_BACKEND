# TASKSAAS Backend

A comprehensive Django REST Framework backend for TaskPrime - a task and business management SaaS application. This backend provides APIs for user management, punch-in/out tracking with geolocation, debtor management, supplier management, and access control.

## 🚀 Features

### Core Modules

- **Authentication & Authorization** - JWT-based authentication with role-based access control
- **User Management** - Multi-client user system with role management
- **Punch-In System** - Employee attendance tracking with:
  - Photo capture and upload to Cloudflare R2
  - GPS location tracking
  - Shop location verification
  - Real-time status tracking
- **Debtors Management** - Track and manage customer debts and payments
- **Suppliers Management** - Manage supplier information and transactions
- **Access Control** - Fine-grained permission management across modules

## 🛠️ Tech Stack

- **Framework**: Django 5.0.2
- **API**: Django REST Framework 3.15.2
- **Authentication**: JWT (djangorestframework-simplejwt 5.5.1)
- **Database**: PostgreSQL (psycopg2-binary 2.9.10)
- **File Storage**: Cloudflare R2 (via django-storages & boto3)
- **Server**: Gunicorn with Uvicorn workers
- **Additional**: 
  - CORS handling (django-cors-headers)
  - QR Code generation
  - Payment integration (Razorpay)
  - Image processing (Pillow)

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)
- Virtual environment (recommended)
- Cloudflare R2 account (for file storage)

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/imcbsglobal/TASKSAAS_BACKEND.git
cd TASKSAAS_BACKEND
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432

# JWT Configuration
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=1

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Cloudflare R2 Storage
CLOUDFLARE_R2_BUCKET=your-bucket-name
CLOUDFLARE_R2_BUCKET_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
CLOUDFLARE_R2_ACCESS_KEY=your-r2-access-key
CLOUDFLARE_R2_SECRET_KEY=your-r2-secret-key
CLOUDFLARE_R2_PUBLIC_URL=https://your-custom-domain.com
```

### 5. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

## 🚀 Running the Application

### Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

### Production Server

```bash
gunicorn tasksaas_backend.wsgi:application --bind 0.0.0.0:8000
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Main Endpoints

#### Authentication
- `POST /api/login/` - User login
- `POST /api/logout/` - User logout
- `POST /api/token/refresh/` - Refresh JWT token

#### User Management
- `GET /api/users/` - List all users
- `POST /api/users/` - Create new user
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user

#### Punch-In System
- `POST /api/punchin/` - Create punch-in record
- `GET /api/punchin/` - List punch-in records
- `GET /api/shoplocation/` - Get shop locations
- `POST /api/shoplocation/` - Create shop location

#### Debtors Management
- `GET /api/debtors/` - List debtors
- `POST /api/debtors/` - Create debtor record
- `GET /api/debtors/{id}/` - Get debtor details

#### Suppliers Management
- `GET /api/suppiers_api/` - List suppliers
- `POST /api/suppiers_api/` - Create supplier record

#### Access Control
- `GET /api/permissions/` - List permissions
- `POST /api/permissions/` - Create permission

## 📁 Project Structure

```
TASKSAAS_BACKEND/
├── tasksaas_backend/       # Main project settings
│   ├── settings.py         # Django settings & configuration
│   ├── urls.py             # Main URL routing
│   ├── wsgi.py             # WSGI application
│   └── asgi.py             # ASGI application
├── app1/                   # Core user management module
│   ├── models.py           # User, AccMaster, Misel models
│   ├── views.py            # Authentication & user views
│   └── urls.py             # User management routes
├── PunchIn/                # Attendance tracking module
│   ├── models.py           # PunchIn, ShopLocation models
│   ├── views.py            # Punch-in/out views
│   └── urls.py             # Punch-in routes
├── DebtorsAPI/             # Debtor management module
│   ├── models.py           # Debtor models
│   ├── views.py            # Debtor views
│   └── urls.py             # Debtor routes
├── suppiers_api/           # Supplier management module
│   ├── models.py           # Supplier models
│   ├── views.py            # Supplier views
│   └── urls.py             # Supplier routes
├── accesscontroll/         # Access control module
│   ├── models.py           # Permission models
│   ├── views.py            # Access control views
│   └── urls.py             # Access control routes
├── logs/                   # Application logs directory
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore file
├── CLOUDFLARE_R2_SETUP.md  # Cloudflare R2 configuration guide
├── PRODUCTION_CHECKLIST.md # Production deployment checklist
└── README.md               # This file
```

## 🔐 Security

### Before Production Deployment

**CRITICAL**: Review the [Production Checklist](PRODUCTION_CHECKLIST.md) before deploying to production.

Key security considerations:
- Generate a new `SECRET_KEY` for production
- Set `DEBUG=False` in production
- Use strong database passwords
- Configure proper CORS origins
- Enable HTTPS/SSL
- Implement rate limiting
- Regular security audits

## 📦 Storage Configuration

This application uses **Cloudflare R2** for file storage (images, documents, etc.).

For detailed setup instructions, see [CLOUDFLARE_R2_SETUP.md](CLOUDFLARE_R2_SETUP.md)

Key features:
- Automatic file uploads via Django's ImageField
- CDN delivery for fast access
- Scalable and cost-effective storage
- Built-in file validation

## 🧪 Testing

Run tests with:

```bash
python manage.py test
```

Run specific app tests:

```bash
python manage.py test app1
python manage.py test PunchIn
python manage.py test DebtorsAPI
```

## 📊 Database

### Supported Databases
- PostgreSQL (recommended for production)
- MySQL
- SQLite (development only)

### Legacy Tables
This project connects to existing legacy database tables:
- `acc_users` - User authentication table
- `misel` - Firm/company information
- `acc_master` - Account master data

These tables are marked as `managed=False` in Django models.

## 🔄 API Response Format

### Success Response
```json
{
  "status": "success",
  "data": {
    // response data
  },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Error description",
  "errors": {
    // field-specific errors
  }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Coding Standards
- Follow PEP 8 style guide
- Write descriptive commit messages
- Add docstrings to functions and classes
- Update documentation for new features
- Write tests for new functionality

## 📝 Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Django secret key | Yes | - |
| `DEBUG` | Debug mode | No | True |
| `ALLOWED_HOSTS` | Allowed hosts list | Yes | localhost |
| `DB_NAME` | Database name | Yes | - |
| `DB_USER` | Database user | Yes | - |
| `DB_PASSWORD` | Database password | Yes | - |
| `DB_HOST` | Database host | No | localhost |
| `DB_PORT` | Database port | No | 5432 |
| `CLOUDFLARE_R2_BUCKET` | R2 bucket name | Yes | - |
| `CLOUDFLARE_R2_BUCKET_ENDPOINT` | R2 endpoint URL | Yes | - |
| `CLOUDFLARE_R2_ACCESS_KEY` | R2 access key | Yes | - |
| `CLOUDFLARE_R2_SECRET_KEY` | R2 secret key | Yes | - |
| `CLOUDFLARE_R2_PUBLIC_URL` | R2 public URL | Yes | - |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins | No | localhost |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | JWT access token lifetime | No | 60 |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | JWT refresh token lifetime | No | 1 |

## 📄 License

This project is proprietary software owned by IMCBS Global. All rights reserved.

## 📞 Support

For support, email: support@taskprime.app

## 🔗 Links

- **Production**: https://taskprime.app
- **API Documentation**: https://taskprime.app/api/docs
- **Frontend Repository**: [Link to frontend repo]

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Maintained by**: IMCBS Global Development Team
