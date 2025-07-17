# 🌱 EcoFinds - Sustainable Marketplace

[![Flask](https://img.shields.io/badge/Flask-2.3.x-blue.svg)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://www.mysql.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.x-purple.svg)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Find Treasures, Save the Planet** - A sustainable marketplace for pre-loved items that promotes circular economy and reduces waste.

## 🌟 Overview

EcoFinds is a modern, eco-friendly marketplace web application built with Flask that allows users to buy and sell pre-loved items. The platform emphasizes sustainability by giving products a second life, reducing waste, and building a community of environmentally conscious consumers.

## ✨ Key Features

### 🔐 Authentication & User Management

- **Google OAuth Integration** - Secure login with Google accounts
- **User Profiles** - Personalized user experiences
- **Session Management** - Seamless cart persistence across sessions

### 🛍️ Marketplace Functionality

- **Product Listings** - Create, edit, and manage product listings
- **Advanced Search & Filtering** - Search by category, price range, and availability
- **Product Categories** - 10 different categories including Electronics, Fashion, Home & Garden
- **Image Support** - Product image uploads with fallback defaults

### 🛒 Shopping Experience

- **Shopping Cart** - Add/remove items with real-time updates
- **Wishlist** - Save favorite items for later
- **Quick Buy** - Instant checkout for single items
- **Cart Persistence** - Anonymous and authenticated user cart management

### 📱 User Interface

- **Responsive Design** - Mobile-first approach with Bootstrap 5
- **Modern UI/UX** - Clean, eco-friendly design with smooth animations
- **Interactive Elements** - AJAX-powered interactions for seamless experience
- **Accessibility** - ARIA labels and semantic HTML

### ⭐ Reviews & Ratings

- **Product Reviews** - Star-based rating system
- **User Feedback** - Comment and review purchased items
- **Review Management** - Edit and delete own reviews

### 📊 User Dashboard

- **My Listings** - Manage your selling products
- **My Orders** - Track purchase history
- **Sales Analytics** - View earnings and statistics

## 🏗️ Technical Architecture

### Backend Stack

- **Framework**: Flask (Python web framework)
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: Flask-Login + Google OAuth (Authlib)
- **Session Management**: Flask sessions with UUID

### Frontend Stack

- **CSS Framework**: Bootstrap 5.3.x
- **Icons**: Font Awesome 6.4.x + Bootstrap Icons
- **Fonts**: Google Fonts (Plus Jakarta Sans)
- **JavaScript**: Vanilla JS with AJAX for dynamic interactions

### Database Schema

```
Users → Products (One-to-Many: seller/buyer)
Products → Reviews (One-to-Many)
Users → Reviews (One-to-Many)
Users → CartItems (One-to-Many)
Users → Wishlist (One-to-Many)
Products → CartItems (One-to-Many)
Products → Wishlist (One-to-Many)
```

## 📁 Project Structure

```
EcoFinds/
├── app.py                 # Main Flask application
├── config.py             # Configuration and database setup
├── database.py           # Database initialization
├── auth.py               # Authentication and login management
├── requirements.txt      # Python dependencies
├── reset_db.py          # Database reset utility
├── models/              # Database models
│   ├── __init__.py
│   ├── user.py          # User model
│   ├── product.py       # Product model and categories
│   ├── review.py        # Review/rating model
│   ├── cart.py          # Cart and wishlist models
│   └── initData.py      # Sample data initialization
├── templates/           # Jinja2 HTML templates
│   ├── layouts/         # Base layouts and components
│   │   ├── layout.html  # Main layout template
│   │   ├── navbar.html  # Navigation component
│   │   └── footer.html  # Footer component
│   ├── index.html       # Product listing page
│   ├── show.html        # Product detail page
│   ├── new.html         # Create product form
│   ├── edit.html        # Edit product form
│   ├── cart.html        # Shopping cart page
│   ├── checkout.html    # Checkout page
│   ├── buy_now.html     # Quick purchase page
│   ├── wishlist.html    # Wishlist page
│   ├── my_orders.html   # User orders page
│   ├── my_listings.html # User listings page
│   ├── login.html       # Login page
│   ├── signup.html      # Signup page (placeholder)
│   └── root.html        # Landing page
└── static/              # Static assets
    ├── css/             # Stylesheets
    │   ├── style.css    # Global styles
    │   ├── navbar.css   # Navigation styles
    │   ├── footer.css   # Footer styles
    │   ├── index.css    # Product grid styles
    │   ├── show.css     # Product detail styles
    │   ├── form.css     # Form styling
    │   ├── rating.css   # Star rating styles
    │   └── root.css     # Landing page styles
    └── js/              # JavaScript files
        └── product-interactions.js # Cart and product interactions
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- MySQL 8.0 or higher
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ecofinds.git
cd ecofinds
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

```bash
# Make sure MySQL is running
# Update database credentials in config.py
python reset_db.py  # Creates and initializes database
```

### 5. Environment Configuration

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 6. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🔧 Configuration

### Database Configuration

Update `config.py` with your MySQL credentials:

```python
def setup_database():
    password = urllib.parse.quote_plus('your-mysql-password')
    return f'mysql+pymysql://root:{password}@localhost/ecofinds'
```

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs: `http://localhost:5000/auth/google/callback`
6. Update `.env` file with client ID and secret

## 🎯 Usage

### For Buyers

1. **Browse Products**: Visit `/products/` to see all available items
2. **Search & Filter**: Use advanced filters to find specific items
3. **Add to Cart**: Add items to cart for batch purchase
4. **Quick Buy**: Use "Buy Now" for instant single-item purchase
5. **Wishlist**: Save items for later consideration
6. **Reviews**: Rate and review purchased items

### For Sellers

1. **Login**: Authenticate with Google account
2. **Create Listing**: Navigate to "Sell Products" to add new items
3. **Manage Listings**: View and edit your products in "My Listings"
4. **Track Sales**: Monitor earnings and sold items

## 🌍 Sustainability Features

- **Circular Economy**: Promotes reuse and extends product lifecycles
- **Waste Reduction**: Diverts items from landfills
- **Community Building**: Connects environmentally conscious users
- **Educational**: Raises awareness about sustainable consumption

## 🔒 Security Features

- **OAuth Authentication**: Secure Google-based login
- **CSRF Protection**: Built-in Flask security
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **Session Security**: Secure session management
- **Input Validation**: Server-side form validation

## 📱 Mobile Responsiveness

The application is fully responsive and optimized for:

- 📱 Mobile devices (320px+)
- 📟 Tablets (768px+)
- 💻 Desktop (1024px+)
- 🖥️ Large screens (1200px+)

## 🎨 Design System

### Color Palette

- **Primary**: #f28d05 (Sustainable Orange)
- **Secondary**: #219ebc (Ocean Blue)
- **Accent**: #ffb703 (Warm Yellow)
- **Dark**: #023047 (Deep Navy)
- **Contrast**: #7c3c04 (Earth Brown)

### Typography

- **Font Family**: Plus Jakarta Sans
- **Weights**: 200-800
- **Responsive scaling**: rem-based sizing

## 🧪 Testing

### Manual Testing

- User authentication flows
- CRUD operations for products
- Cart and wishlist functionality
- Purchase workflows
- Responsive design testing

### Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Use production-grade secret keys
2. **Database**: Configure production MySQL instance
3. **SSL/HTTPS**: Enable SSL certificates
4. **Error Handling**: Implement comprehensive error logging
5. **Monitoring**: Add application monitoring
6. **Backup**: Regular database backups

### Deployment Platforms

- **Heroku**: Easy deployment with MySQL add-on
- **AWS**: EC2 with RDS MySQL
- **DigitalOcean**: App Platform or Droplets
- **Azure**: App Service with MySQL

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use semantic commit messages
- Add comments for complex logic
- Test changes thoroughly
- Update documentation as needed

## 📈 Roadmap

### Short Term (v1.1)

- [ ] Email notifications for sales
- [ ] Advanced search with filters
- [ ] Product image upload functionality
- [ ] User profile pages

### Medium Term (v1.2)

- [ ] Payment gateway integration
- [ ] Real-time chat between buyers/sellers
- [ ] Product recommendation engine
- [ ] Mobile app development

### Long Term (v2.0)

- [ ] Multi-vendor marketplace
- [ ] AI-powered product categorization
- [ ] Blockchain-based authenticity verification
- [ ] Carbon footprint tracking

## 📊 Analytics & Metrics

- **User Engagement**: Track active users and session duration
- **Environmental Impact**: Calculate waste reduction metrics
- **Sales Performance**: Monitor transaction volumes and values
- **User Satisfaction**: Collect feedback and ratings

## 🐛 Known Issues

- Cart persistence across browser sessions needs improvement
- Image upload functionality not yet implemented
- Email notifications are placeholder only

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Flask Community** for the excellent framework
- **Bootstrap Team** for the responsive design system
- **Font Awesome** for the beautiful icons
- **Google Fonts** for typography
- **Unsplash** for placeholder images

## 📞 Support

For support, please open an issue on GitHub or contact the development team.

---

**EcoFinds** - Building a sustainable future, one transaction at a time. 🌱

_Made with ❤️ for the environment_
