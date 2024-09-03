# Social Networking API

This project is a Django-based API for a social networking application, built using Django Rest Framework (DRF) and PostgreSQL. It includes user authentication, friend request management, and various endpoints for querying friend requests and friends.

## Features

1. **User Authentication**
   - **Login**: Users can log in using their email and password.
   - **Signup**: Users can sign up with their email address.

2. **Friend Request Management**
   - **Send Friend Request**: Users can send friend requests.
   - **Accept/Reject Friend Request**: Only the receiver can accept or reject friend requests.
   - **List Friends**: List users who have accepted the friend request.
   - **List Pending Requests**: List friend requests that are pending (received but not yet accepted or rejected).

## Installation

1. **Clone the Repository:**
   git clone <repository-url>

2. **Navigate to the Project Directory:**
    cd social_network_drf

2.1 **For local setup, create .env file (reference: .env.example) and run following commands to start the server and access application to http://localhost:8000**
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver

3. **Create and Start Containers:**
    docker-compose up --build

4. **Apply Migrations:**
    docker-compose run web python manage.py migrate

5. **Create a Superuser:**
    docker-compose run web python manage.py createsuperuser

6. **Access the Application:**
    Open your browser and navigate to http://localhost:8000 to view your Django application.

***You can use postman collection by importing social_network.postman_collection file in postman:***
    Open postman
    Import social_network.postman_collection file using "import" button located on top left cornet
