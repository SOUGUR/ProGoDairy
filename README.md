# ProGoDairy - Dairy Management System

A comprehensive Django-based web application for managing dairy operations, from milk collection to distribution. This system streamlines the entire dairy supply chain including supplier management, milk quality testing, collection centers, processing plants, and distribution networks.

## 📚 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Database Models](#database-models)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### Supplier Management
- Complete supplier profile management with personal and banking details
- Track daily milk capacity and annual output projections
- Maintain supplier location and route assignments
- Aadhar and bank account verification

### Milk Quality Testing
- Detailed quality parameter tracking:
  - Fat percentage
  - Protein content
  - Lactose levels
  - Total solids and SNF (Solids-Not-Fat)
  - Urea nitrogen (MUN)
  - Bacterial count
- Automated quality-based pricing system
- Milk lot approval/rejection workflow

### Collection Center Operations
- Bulk cooler management and assignment
- Track milk lots by collection center
- Real-time inventory monitoring

### Plant Management
- Tester role assignment for quality checks
- Process milk lots from multiple suppliers
- Integration with distribution system

### Distribution Network
- Route management for milk collection and delivery
- Milk transfer tracking between facilities
- Distribution optimization

### Payment & Billing
- Automated bill generation based on approved milk lots
- Quality-based pricing with bonus system
- Payment tracking and reconciliation
- PDF bill generation support

### User Management
- Django built-in authentication system
- Role-based access control
- Admin dashboard for system management

## 🛠️ Technology Stack

- **Backend Framework**: Django 5.2.4
- **Database**: SQLite (default, can be configured for PostgreSQL/MySQL)
- **GraphQL**: Strawberry Django for API
- **Frontend**: Django Templates with HTML/CSS
- **Authentication**: Django Auth
- **Python Version**: Python 3.x

## 📁 Project Structure

```
ProGoDairy/
├── accounts/              # User authentication and account management
├── collection_center/     # Collection center operations and bulk coolers
├── dairy_project/         # Main project configuration
│   ├── settings.py        # Project settings
│   ├── urls.py            # URL routing
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
├── distribution/          # Distribution routes and milk transfer
├── milk/                  # Milk-related operations (currently being restructured)
├── plants/                # Processing plant management
├── suppliers/             # Supplier management and milk lot tracking
│   ├── models.py          # Supplier, MilkLot, PaymentBill models
│   ├── views.py           # Business logic
│   └── admin.py           # Admin interface customization
├── static/                # Static files (CSS, JavaScript, images)
│   └── images/            # Application images and assets
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── homePage.html      # Homepage
│   ├── accounts/          # Account-related templates
│   ├── suppliers/         # Supplier templates
│   ├── collection_center/ # Collection center templates
│   └── distribution/      # Distribution templates
├── .gitignore
└── manage.py              # Django management script
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/SOUGUR/ProGoDairy.git
   cd ProGoDairy
   ```

2. **Create and activate virtual environment**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install django==5.2.4
   pip install strawberry-graphql-django
   ```

4. **Apply database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (admin account)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Homepage: `http://127.0.0.1:8000/`
   - Admin Panel: `http://127.0.0.1:8000/admin/`
   - GraphQL Endpoint: `http://127.0.0.1:8000/graphql`

## ⚙️ Configuration

### Database Configuration

By default, the project uses SQLite. To use PostgreSQL or MySQL:

1. Install the appropriate database driver:
   ```bash
   pip install psycopg2-binary  # For PostgreSQL
   # OR
   pip install mysqlclient      # For MySQL
   ```

2. Update `dairy_project/settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'your_database_name',
           'USER': 'your_database_user',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

### Secret Key

**Important**: Change the `SECRET_KEY` in `settings.py` before deploying to production:

```python
SECRET_KEY = 'your-secure-secret-key-here'
```

### Debug Mode

For production deployment, set `DEBUG = False` in `settings.py` and configure `ALLOWED_HOSTS`:

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

## 💻 Usage

### Admin Panel

1. Access the admin panel at `/admin/`
2. Log in with superuser credentials
3. Manage all aspects of the dairy system:
   - Add/edit suppliers
   - Review milk lots and quality parameters
   - Assign testers and routes
   - Generate payment bills
   - Monitor collection centers

### Workflow

1. **Supplier Registration**
   - Register new suppliers with complete details
   - Assign collection routes

2. **Milk Collection**
   - Suppliers deliver milk lots
   - Record volume and initial details

3. **Quality Testing**
   - Testers perform quality checks
   - System records all quality parameters

4. **Evaluation & Pricing**
   - System automatically evaluates quality
   - Calculates price based on quality thresholds
   - Assigns bonus for premium quality

5. **Approval Process**
   - Approve or reject milk lots
   - Assign to bulk coolers/storage

6. **Billing**
   - Generate bills for approved lots
   - Track payments
   - Export to PDF

## 💾 Database Models

### Supplier Model
- User profile with contact details
- Daily capacity and production metrics
- Banking information for payments
- Aadhar number for identification
- Route assignment

### MilkLot Model
- Individual milk delivery tracking
- Quality parameters (fat, protein, SNF, etc.)
- Volume and date tracking
- Status (pending/approved/rejected)
- Price calculation
- Tester assignment
- Collection center/bulk cooler assignment

### PaymentBill Model
- Aggregated billing for suppliers
- Total volume and value calculation
- Payment status tracking
- PDF generation support

## 📝 Quality-Based Pricing System

The system implements an automated quality-based pricing mechanism:

**Base Price**: ₹26.00 per litre

**Quality Bonuses**:
- Fat ≥ 3.5%: +₹1.50/L
- SNF ≥ 8.5%: +₹1.00/L
- Protein ≥ 3.0%: +₹0.50/L
- Urea nitrogen ≤ 70 mg/dL: +₹0.50/L
- Bacterial count ≤ 50,000/mL: +₹0.50/L

**Maximum Price**: ₹30.00 per litre (with all bonuses)

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write clear commit messages
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 🔒 Security Considerations

- Change the default `SECRET_KEY` before production deployment
- Use environment variables for sensitive configuration
- Keep `DEBUG = False` in production
- Implement proper user authentication and authorization
- Regularly update dependencies for security patches
- Use HTTPS in production

## 🛣️ Roadmap

- [ ] Add REST API endpoints
- [ ] Implement real-time notifications
- [ ] Mobile app integration
- [ ] Advanced analytics and reporting dashboard
- [ ] Multi-language support
- [ ] Automated SMS/Email notifications
- [ ] Integration with payment gateways
- [ ] Inventory management for dairy products

## 📝 License

This project is open source and available for educational and commercial use.

## 📧 Contact

**Project Maintainer**: SOUGUR

**GitHub**: [https://github.com/SOUGUR/ProGoDairy](https://github.com/SOUGUR/ProGoDairy)

---

**Built with ❤️ using Django**
