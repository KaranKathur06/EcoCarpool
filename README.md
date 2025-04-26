# EcoCarpool - Sustainable Ride-Sharing Platform

EcoCarpool is a modern web application that facilitates sustainable transportation through ride-sharing. It connects drivers and passengers, promoting eco-friendly commuting while reducing costs and environmental impact.

## 🌟 Features

### For Drivers
- Create and manage ride offers
- Track earnings and ride history
- Vehicle management system
- Real-time ride status updates
- Rating and review system

### For Passengers
- Search and book available rides
- Track ride status and history
- Payment integration
- Favorite routes
- Environmental impact tracking

### For Administrators
- Comprehensive dashboard
- User management
- Ride monitoring
- Revenue tracking
- Platform analytics

## 🛠️ Technology Stack

- **Backend**: Django
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL
- **Charts**: Chart.js
- **UI Framework**: Bootstrap
- **Authentication**: Django Authentication System

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js and npm
- PostgreSQL

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/ecocarpool.git
cd ecocarpool
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
npm install
```

4. Set up environment variables
Create a `.env` file in the root directory with:
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
```

5. Run migrations
```bash
python manage.py migrate
```

6. Start the development server
```bash
python manage.py runserver
```

## 📁 Project Structure

```
ecocarpool/
├── api/            # API endpoints
├── bookings/       # Booking management
├── dashboard/      # Admin dashboard
├── payments/       # Payment processing
├── rides/          # Ride management
├── reviews/        # Review system
├── users/          # User management
├── vehicles/       # Vehicle management
├── wallet/         # Wallet functionality
├── static/         # Static files
├── templates/      # HTML templates
└── manage.py       # Django management script
```

## 🔒 Security Features

- Secure user authentication
- Payment encryption
- Data validation
- XSS protection
- CSRF protection
- Rate limiting

## 📊 Dashboard Features

- Real-time statistics
- User growth tracking
- Revenue analytics
- Ride status monitoring
- Environmental impact metrics

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- [Karan N Kathur](https://github.com/KaranKathur06) 

## 🙏 Acknowledgments

- Django community
- Bootstrap team
- Chart.js team
- All contributors and supporters 
