# First Project

## Project Overview

This is a Django-based web application developed to learn user authentication, profile management, and REST API development. The project allows users to register, log in, manage their profile, reset their password, submit contact messages, and securely log out.

## Features

- User Registration
- User Login
- User Logout
- Dashboard
- Profile Management
- Update Username
- Update Mobile Number
- Update Alternate Mobile Number
- Update Date of Birth
- Update Address
- Upload Profile Image
- Change Password
- Forgot Password
- Contact Form
- Logging
- REST API using Django REST Framework

## Tech Stack

### Backend

- Python
- Django
- Django REST Framework

### Frontend

- HTML
- CSS

### Database

- SQLite3

### Version Control

- Git
- GitHub

## Project Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
```

### 2. Navigate to the Project Directory

```bash
cd first_project
```

### 3. Create a Virtual Environment

**Windows**

```bash
python -m venv wrold
```

### 4. Activate the Virtual Environment

**Windows**

```bash
wrold\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Apply Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 8. Run the Development Server

```bash
python manage.py runserver
```

### 9. Open the Application

Application

```
http://127.0.0.1:8000/
```

Admin Panel

```
http://127.0.0.1:8000/admin/
```


## Project Workflow

### 1. User Registration

- Open the Registration page.
- Enter the required user details.
- The application validates the input.
- A new Django User and User Profile are created.
- The user is redirected to the Login page.

### 2. User Login

- Enter the registered username and password.
- Django authenticates the user.
- If the credentials are valid, the user is redirected to the Dashboard.
- If the credentials are invalid, an error message is displayed.

### 3. Dashboard

After successful login, the Dashboard provides access to:

- service
- Profile
- Contact
- Logout

### 4. Profile Management

From the Profile page, the user can:

- Update Username
- Update Mobile Number
- Update Alternate Mobile Number
- Update Date of Birth
- Update Address
- Upload Profile Image
- Change Password

The application validates the updated information before saving it.

### 5. Forgot Password

- Open the Forgot Password page.
- Enter the registered email address.
- Enter a new password and confirm it.
- If validation is successful, the password is updated.
- The user can log in using the new password.

### 6. Contact Form

- Open the Contact page.
- Enter Name, Email, and Message.
- Submit the form.
- The message is stored in the database.

### 7. REST API

The project provides REST APIs for:

- User Profile CRUD Operations
- Contact Message CRUD Operations

API access is protected using authentication and custom permissions.

### 8. User Logout

- Click the Logout button.
- The current user session is terminated securely.
- The user is redirected to the Login page.

### 9. Admin Panel

The Django Admin Panel allows administrators to:

- View registered users
- Manage user profiles
- View contact messages


## Logging

The application records important events such as:

- User Registration
- Login Attempts
- Successful Login
- Logout
- Password Reset
- Profile Updates
- Contact Form Submission
- Validation Warnings
