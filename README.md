# Credify - Setup Guide

## Quick Start (15 minutes)

### Step 1: Project Setup
```bash
# Create project directory
mkdir credit_approval_system
cd credit_approval_system

# Create all the required directories
mkdir -p credit_system apps/customers apps/loans apps/core data scripts
mkdir -p apps/customers/management/commands apps/loans/management/commands
```

### Step 2: Create All Files
Create all the files provided in the artifacts in their respective directories:

```
credit_approval_system/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── credit_system/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery.py
├── apps/
│   ├── __init__.py
│   ├── customers/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── management/
│   │       └── commands/
│   │           ├── __init__.py
│   │           ├── loaddata_async.py
│   │           └── loaddata_sync.py
│   ├── loans/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── admin.py
│   └── core/
│       ├── __init__.py
│       ├── tasks.py
│       ├── utils.py
│       └── credit_scoring.py
└── data/
    ├── customer_data.xlsx
    └── loan_data.xlsx
```

### Step 3: Copy Excel Files
Copy your `customer_data.xlsx` and `loan_data.xlsx` files to the `data/` directory.

### Step 4: Build and Run
```bash
# Build and start all services
docker-compose up --build

# The application will be available at http://localhost:8000
```

## Manual Setup (If Docker Issues)

### Prerequisites
- Python 3.11+
- PostgreSQL
- Redis

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Environment Setup
```bash
export DATABASE_URL=postgresql://user:password@localhost:5432/credit_db
export REDIS_URL=redis://localhost:6379/0
```

### Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### Load Data
```bash
# Load data synchronously (recommended for first time)
python manage.py loaddata_sync

# Or load data asynchronously with Celery
python manage.py loaddata_async
```

### Run Servers
```bash
# Terminal 1: Django
python manage.py runserver 8000

# Terminal 2: Celery (if using async data loading)
celery -A credit_system worker --loglevel=info
```

## API Endpoints

### 1. Register Customer
```bash
POST /api/register/
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "monthly_income": 50000,
    "phone_number": 9876543210
}
```

### 2. Check Loan Eligibility
```bash
POST /api/check-eligibility/
Content-Type: application/json

{
    "customer_id": 1,
    "loan_amount": 200000,
    "interest_rate": 10.5,
    "tenure": 24
}
```

### 3. Create Loan
```bash
POST /api/create-loan/
Content-Type: application/json

{
    "customer_id": 1,
    "loan_amount": 200000,
    "interest_rate": 10.5,
    "tenure": 24
}
```

### 4. View Loan Details
```bash
GET /api/view-loan/{loan_id}/
```

### 5. View Customer Loans
```bash
GET /api/view-loans/{customer_id}/
```

## Testing the System

### Test Sequence:
1. **Start the system**: `docker-compose up --build`
2. **Wait for data loading**: Check logs for "Data loading completed"
3. **Register new customer**: Test `/register` endpoint
4. **Check eligibility**: Test `/check-eligibility` endpoint
5. **Create loan**: Test `/create-loan` endpoint
6. **View details**: Test view endpoints

### Sample Test Commands:
```bash
# Register customer
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Test", "last_name": "User", "age": 25, "monthly_income": 60000, "phone_number": 1234567890}'

# Check eligibility for existing customer (ID: 1)
curl -X POST http://localhost:8000/api/check-eligibility/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "loan_amount": 100000, "interest_rate": 12, "tenure": 12}'
```

## Key Features Implemented

**Complete API Implementation**: All 5 required endpoints  
**Credit Scoring Algorithm**: Based on 5 components as specified  
**Interest Rate Correction**: Automatic adjustment based on credit score  
**Background Data Ingestion**: Celery-based async loading  
**Docker Containerization**: Single command deployment  
**PostgreSQL Integration**: Optimized database schema  
**Error Handling**: Comprehensive validation and error responses  
**Documentation**: Swagger/OpenAPI integration  

## Troubleshooting

### Common Issues:

1. **Port conflicts**: Change ports in docker-compose.yml
2. **Data not loading**: Check Excel files are in `data/` directory
3. **Database connection**: Ensure PostgreSQL is running
4. **Celery issues**: Make sure Redis is accessible

### Debug Commands:
```bash
# Check container logs
docker-compose logs web
docker-compose logs celery

# Access Django shell
docker-compose exec web python manage.py shell

# Check database
docker-compose exec db psql -U postgres -d credit_approval_db
```

## Performance Optimizations

- Database indexes on frequently queried fields
- Efficient credit scoring algorithm
- Optimized compound interest calculations
- Proper foreign key relationships
- Background task processing

## Security Features

- Input validation using DRF serializers
- SQL injection prevention with ORM
- CORS configuration
- Error handling without sensitive data exposure

Your system is now production-ready!