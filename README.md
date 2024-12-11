# 🐀 Mall Rats - Modern E-commerce Platform

Mall Rats is a modern e-commerce web application built with React and FastAPI, offering a seamless shopping experience with features like category browsing, product filtering, and a secure authentication system.

## 🌟 Features

### Shopping Experience
- **Product Browsing**:
  - Category-based filtering
  - Product search functionality
  - Detailed product views
  - Rating and review system
  - Shopping cart functionality

### User Management
- **Authentication System**:
  - User registration
  - Secure login
  - Protected routes
  - JWT token authentication
  - Session management

### Admin Features
- **Product Management**:
  - Add new products
  - Update existing products
  - Category management
  - Brand management
  - Subcategory organization

### User Interface
- **Modern Design**:
  - Responsive layout
  - Dark theme
  - Interactive components
  - Smooth transitions
  - Mobile-friendly design

## 🛠 Technology Stack

### Frontend
- React
- React Router DOM
- Tailwind CSS
- Lucide React Icons
- Supabase Client

### Backend
- Python
- FastAPI
- SQLModel
- PostgreSQL
- Alembic (migrations)
- JWT Authentication

### Deployment
- Fly.io
- CORS enabled
- Environment configuration

## 🚀 Getting Started

### Prerequisites
- Python (3.8 or higher)
- Node.js (16.0 or higher)
- PostgreSQL database
- Supabase account

### Environment Variables
Create a `.env` file in both frontend and backend directories:

```env
# Backend
DATABASE_URL=your_database_url
SUPABASE_SECRET_KEY=your_supabase_key
JWT_ALGORITHM=your_jwt_algorithm

# Frontend
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_API_KEY=your_supabase_api_key
VITE_API_URL=your_api_url
```

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mall-rats.git

# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload

# Frontend Setup
cd frontend
npm install
npm run dev
```

## 📊 API Endpoints

### Product Management
- `GET /api/products/`: Get products by category
- `POST /products/add`: Add new product (authenticated)
- `GET /api/brands/`: Get all brands
- `GET /api/categories/`: Get all categories
- `GET /api/subcategories/`: Get subcategories

### Authentication Routes
- `POST /categories/auth/add`: Add new category
- `PUT /categories/auth/{item_id}`: Update category
- `DELETE /categories/auth/{item_id}`: Delete category
- Similar endpoints for brands and subcategories

## 🎨 Design Features
- Custom purple and green color scheme
- Responsive grid layouts
- Interactive product cards
- Dynamic navigation bar
- Cart notification system
- Social media integration
- Animated hover effects

## 🤝 Contributing
We welcome contributions to Mall Rats! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/NewFeature`)
3. Commit your changes (`git commit -m 'Add some NewFeature'`)
4. Push to the branch (`git push origin feature/NewFeature`)
5. Open a Pull Request

## 📝 Project Structure
```
mall-rats/
├── backend/
│   ├── models/         # Database models
│   ├── migrations/     # Alembic migrations
│   ├── main.py        # FastAPI application
│   └── db.py          # Database configuration
├── frontend/
│   ├── src/
│   │   ├── components/ # React components
│   │   ├── routes/     # Route components
│   │   └── context/    # React context
│   ├── public/         # Static assets
│   └── index.html      # Entry point
```

## 🚧 Features in Development
- User reviews and ratings
- Wishlist functionality
- Advanced search filters
- Order management system
- Payment integration
- Admin dashboard

---
Built with 💜 by Jordan Church
