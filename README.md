# ⏱️ Tickr
<!-- [![Ask DeepWiki](https://devin.ai/assets/askdeepwiki.png)](https://deepwiki.com/earlhsjks/tickr) -->

Tickr is a comprehensive, office-focused Daily Time Record (DTR) and employee attendance system built with Flask. As the successor to the Tachyon Log project, it's designed with a robust feature set for both administrators and employees (referred to as GIAs).

## Core Features

-   **Dual-Role Authentication**: Secure login for Admins and Employees (GIAs) with distinct permissions.
-   **Admin Dashboard**: Provides an at-a-glance overview of key attendance metrics like total employees, average work hours, and overtime.
-   **User Management**: Full CRUD (Create, Read, Update, Delete) functionality for managing employee accounts.
-   **Schedule Management**: Admins can assign daily and complex split-shift schedules to employees.
-   **Employee Dashboard**: A self-service portal for employees to clock in/out and view their attendance history.
-   **IP-Restricted Time Logging**: Clock-in/out functionality is restricted to whitelisted IP addresses, with configurable rules for strictness and early check-ins.
-   **Attendance Management**: Admins can view real-time daily logs and manually add or edit attendance records for corrections.
-   **DTR Report Generation**: Automatically generate and print DTR summaries in a formatted PDF-ready layout.
-   **Audit Logging**: Tracks and records all significant actions within the system for accountability and review.
-   **System Configuration**: A settings panel for administrators to configure system-wide attendance policies, default times, and unit head details.

## Tech Stack

-   **Backend**: Python (Flask, SQLAlchemy)
-   **Database**: MySQL
-   **Frontend**: HTML, CSS, JavaScript, Bootstrap
-   **Deployment**: Waitress

## Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

-   Python 3.x
-   MySQL Server

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/earlhsjks/tickr.git
    cd tickr
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    Create a `.env` file in the root directory and add your database credentials and a secret key:
    ```env
    SECRET_KEY=your_super_secret_key
    DB_HOST=localhost
    DB_USER=your_db_user
    DB_PASS=your_db_password
    DB_NAME=tickr_db
    ```

5.  **Set up the database:**
    a. In your MySQL server, create a database with the name you specified for `DB_NAME`.
    b. In `app.py`, uncomment the `initialize_database()` function call at the bottom of the file.
    c. Run the application once to create the database tables and the initial superadmin user:
    ```bash
    python app.py
    ```
    d. Once the server starts, stop it (`Ctrl+C`) and **re-comment** the `initialize_database()` line in `app.py` to prevent it from running again.

6.  **Run the application:**
    ```bash
    python app.py
    ```
    The application will be available at `http://127.0.0.1:5001`.

## Usage

### Admin Login

The system creates a default superadmin user during the initial database setup.
```sql
INSERT INTO user (user_id, first_name, last_name, password, role)
VALUES ('admin', 'Admin', 'User', <hashed_pw>, 'admin');
```

Log in using these credentials on the "Login as Admin" form to access the administrative dashboard.

### Employee (GIA) Login

Employees (GIAs) are created by an administrator. They can log in from the main page using only their assigned **User ID**. Clock-in and clock-out features are only available when accessing the system from a whitelisted IP address (e.g., the office network).

## Project Structure

```
├── app.py                  # Main Flask application, configuration, and startup
├── config.py               # Loads environment variables
├── requirements.txt        # Python dependencies
├── models/
│   └── models.py           # SQLAlchemy database models
├── routes/
│   ├── admin.py            # Routes for the admin panel
│   ├── api.py              # All API endpoints
│   ├── auth.py             # User authentication routes (login/logout)
│   └── gia.py              # Routes for the employee (GIA) dashboard
├── static/
│   ├── css/                # Stylesheets
│   └── js/                 # JavaScript files
└── templates/
    ├── admin/              # Admin-facing HTML templates
    ├── auth/               # Login page template
    └── gia/                # Employee-facing HTML templates
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.