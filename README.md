# Syro Flow - README.md and LICENSE

## `README.md`

```markdown
# Syro Flow

## Web-Based Content Management and Donation Platform

[![Django Version](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![Python Version](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-orange.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Table of Contents

- [About](#about)
- [Features](#features)
- [Computer Science Concepts](#computer-science-concepts)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Deployment](#deployment)
- [Security](#security)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## 📌 About

**Syro Flow** is a database-driven Content Management System (CMS) built with Django. It allows authorized administrators to create, manage, publish, and organize digital content through a web-based interface while providing visitors with accessible articles, images, informational pages, and transparent donation information.

The system demonstrates key Computer Science concepts including web application architecture, database management, object-relational mapping, CRUD operations, authentication, authorization, and cloud deployment.

### Project Objective

> To design and implement a database-driven content management system that allows authorized users to create, manage, publish, and organize digital content through a web-based interface while providing visitors with accessible articles, images, informational pages, and transparent donation information.

---

## ✨ Features

### Content Management
- ✅ Create, edit, publish, and delete posts
- ✅ Organize posts by categories (Teaching, Repentance, Rebuke, Warnings, Testimonies, Scripture)
- ✅ Draft and publish workflow
- ✅ Rich text editing via CKEditor
- ✅ SEO-friendly slugs

### Media Library
- ✅ Upload images with titles and alt text
- ✅ Image gallery with thumbnails
- ✅ File validation (types, size, dimensions)
- ✅ Associate images with posts

### Pages
- ✅ Create and manage permanent pages (About, Contact, Mission, etc.)
- ✅ Dynamic page content
- ✅ Page status (draft/published)

### Donations
- ✅ Configurable donation information
- ✅ Bank details management
- ✅ Fund usage explanation
- ✅ All editable through admin interface

### Security
- ✅ Django authentication and authorization
- ✅ CSRF protection
- ✅ Input validation
- ✅ File upload security
- ✅ Secure environment variables
- ✅ HTTPS enforcement

### Additional Features
- ✅ Category filtering
- ✅ Search functionality
- ✅ Pagination
- ✅ Responsive design
- ✅ Custom error pages (404, 500)
- ✅ REST API ready (DRF)

---

## 🖥️ Computer Science Concepts Demonstrated

| Concept | Implementation |
|---------|---------------|
| **Web Application Architecture** | Client-server model with Django |
| **Relational Databases** | PostgreSQL with normalized schema |
| **Object-Relational Mapping** | Django ORM |
| **CRUD Operations** | Complete CRUD for all models |
| **Authentication & Authorization** | Django's built-in auth system |
| **REST APIs** | Django REST Framework |
| **Separation of Concerns** | MVC/MVT pattern |
| **Modular Design** | Django apps for each domain |
| **Input Validation** | Form validation and model validation |
| **File Management** | Media library with validation |
| **Testing** | Comprehensive test suite |
| **Software Security** | Multiple security layers |
| **Cloud Deployment** | Vercel deployment |

---

## 🛠️ Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.12+ | Programming language |
| Django | 4.2 | Web framework |
| Django REST Framework | 3.14 | API development |
| PostgreSQL | 15+ | Database |
| Gunicorn | 21.2 | WSGI server |

### Frontend
| Technology | Purpose |
|------------|---------|
| HTML5 | Structure |
| CSS3 | Styling |
| JavaScript | Interactivity |
| Django Templates | Templating |
| CKEditor | Rich text editing |

### Tools & Services
| Tool | Purpose |
|------|---------|
| Vercel | Hosting and deployment |
| Git | Version control |
| GitHub | Repository hosting |
| psycopg2 | PostgreSQL adapter |
| django-environ | Environment management |
| Pillow | Image processing |
| Whitenoise | Static file serving |

---

## 🏗️ System Architecture

```
                        SYRO FLOW
                             │
                             ▼
                       Web Browser
                             │
                             ▼
                          Vercel
                             │
                             ▼
                          Django
                             │
             ┌───────────────┼───────────────┐
             │               │               │
             ▼               ▼               ▼
           Posts           Pages         Donations
             │               │               │
             └───────────────┼───────────────┘
                             │
                             ▼
                       Django ORM
                             │
                             ▼
                        PostgreSQL
                             │
                             ▼
                      Persistent Data
```

### Data Flow

```mermaid
flowchart LR
    Admin[Django Admin] --> Post[Create/Edit Post]
    Post --> DB[(PostgreSQL)]
    Visitor[Website Visitor] --> Django
    Django --> DB
    DB --> HTML[HTML Response]
```

## 🚀 Installation

### Prerequisites

- Python 3.12 or higher
- PostgreSQL 15 or higher
- Git
- Virtual environment (recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/syro-flow.git
cd syro-flow
```

### Step 2: Create and Activate Virtual Environment

```bash
# Linux/Mac
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your actual values
```

### Step 5: Set Up Database

```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE syro_flow;
CREATE USER syro_user WITH PASSWORD 'your_password';
ALTER ROLE syro_user SET client_encoding TO 'utf8';
ALTER ROLE syro_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE syro_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE syro_flow TO syro_user;
\q
```

### Step 6: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 7: Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

### Step 8: Collect Static Files

```bash
python manage.py collectstatic
```

### Step 9: Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to view the site and `http://localhost:8000/admin` for the admin interface.

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `DEBUG` | Debug mode (True/False) | Yes |
| `ALLOWED_HOSTS` | Comma-separated hostnames | Yes |
| `SITE_NAME` | Site name for display | No |
| `SITE_DESCRIPTION` | Site description | No |
| `ADMIN_URL` | Admin URL path | No |
| `STATIC_URL` | Static files URL | No |
| `MEDIA_URL` | Media files URL | No |
| `MAX_UPLOAD_SIZE` | Max file upload size (bytes) | No |

### Database URL Format

```
postgresql://username:password@host:5432/database_name
```

---

## 📝 Usage

### Creating Content

1. **Login to Admin**: Visit `/admin` and login with superuser credentials
2. **Create a Post**: Click "Posts" → "Add Post"
3. **Add Content**: Enter title, content, select category, upload image
4. **Publish**: Set status to "Published" and save
5. **Manage Pages**: Use the Pages section for static content
6. **Upload Images**: Use Media Library for images
7. **Update Donations**: Edit Donation Settings

### Public Views

| URL | Description |
|-----|-------------|
| `/` | Homepage with recent posts |
| `/posts/` | All published posts |
| `/posts/<slug>/` | Individual post |
| `/category/<slug>/` | Posts by category |
| `/gallery/` | Image gallery |
| `/gallery/<id>/` | Individual image |
| `/about/` | About page |
| `/contact/` | Contact page |
| `/donations/` | Donation information |
| `/search/` | Search results |

---

## 🧪 Testing

### Run All Tests

```bash
python manage.py test
```

### Run Specific Test File

```bash
python manage.py test tests.test_posts
```

### Run Specific Test Case

```bash
python manage.py test tests.test_posts.PostModelTests.test_post_creation
```

### Test Coverage

```bash
# Install coverage
pip install coverage

# Run with coverage
coverage run manage.py test
coverage report
coverage html  # Generate HTML report
```
