# First Project

A Django-based web application that provides user authentication and profile management features. This project demonstrates the fundamentals of Django, including authentication, model relationships, form handling, and CRUD operations.

---

## Features

- User Registration
- User Login
- User Logout
- Forgot Password
- Change Password
- Profile Management
- Contact Form
- Form Validation
- Logging Support

---

## Tech Stack

### Backend
- Python 
- Django

### Frontend
- HTML
- CSS

### Database
- SQLite3

### Version Control
- Git
- GitHub

---

## Project Structure

```text
first-project/
│── app/
│── first_project/
│── templates/
│── static/
│── media/
│── db.sqlite3
│── manage.py
│── requirements.txt
└── README.md
```

---

## Prerequisites

Before running the project, make sure the following are installed:

- Python 3.x
- pip
- Git

---

## Project Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
```

### 2. Navigate to the Project Directory

```bash
cd <project-folder>
```

### 3. Create a Virtual Environment

**Windows**

```bash
python -m venv venv
```

**Linux/macOS**

```bash
python3 -m venv venv
```

---

### 4. Activate the Virtual Environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

---

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 6. Apply Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 7. Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

---

### 8. Run the Development Server

```bash
python manage.py runserver
```

---

### 9. Open the Application

Visit:

```
http://127.0.0.1:8000/
```

Admin Panel:

```
http://127.0.0.1:8000/admin/
```

---

## Available Pages

- Home
- Register
- Login
- Dashboard
- Profile
- Change Password
- Forgot Password
- Contact

---

## Database

This project uses **SQLite3** as the default database.

---

## Logging

Logging has been configured to record application events such as:

- User registration
- Login attempts
- Successful login
- Logout
- Password reset
- Profile updates
- Validation warnings

---

## Learning Objectives

This project was built to learn and practice:

- Django Authentication
- Django ORM
- Models
- Views
- URL Routing
- Templates
- Forms
- Model Relationships
- Validation
- Logging
- Static Files
- Git & GitHub Workflow

---

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a new branch

```bash
git checkout -b feature-name
```

3. Commit your changes

```bash
git commit -m "Add new feature"
```

4. Push the branch

```bash
git push origin feature-name
```

5. Open a Pull Request

---

## License

This project is created for learning purposes.