# Tikr – Office-Centered Daily Time Record

Tickr is a simplified, office-focused Daily Time Record (DTR) and employee attendance system built with Flask. It provides a comprehensive suite for managing employee schedules, tracking time logs, and generating reports, with distinct portals for administrators and employees (GIAs).

## Key Features

### Admin Panel
*   **Dashboard:** An at-a-glance overview of key metrics, including total employees, currently present employees, late arrivals, and recent system activity.
*   **User Management:** Full CRUD (Create, Read, Update, Delete) functionality for managing user accounts (Admins and GIAs).
*   **Schedule Management:** Assign and manage work schedules for GIAs based on daily blocks (MW, TTh, Fri, Sat), with support for split shifts.
*   **Time Log Management:** View and edit daily attendance records. Manually add logs for corrections or special cases.
*   **DTR Reports:** Generate and export monthly Daily Time Records for all employees into a printable PDF format.
*   **Audit Logs:** A detailed trail of all significant actions performed within the system, filterable by date, user, and action type.
*   **System Settings:** Configure system-wide policies, including the unit head's name for reports, default working hours, and clock-in/out rules like "Strict Mode".

### Employee (GIA) Portal
*   **Attendance Dashboard:** A personalized view of rendered hours, remaining hours for the month, and a summary of recent activity.
*   **Clock-in / Clock-out:** Simple, real-time clock-in and clock-out functionality. The system validates actions against the user's assigned schedule.
*   **Schedule Viewing:** Employees can view their assigned work schedule for the week.
*   **IP-Based Restriction:** Access to the GIA portal can be restricted to specific IP addresses (e.g., office network only) for enhanced security.

## Tech Stack

*   **Backend:** Python, Flask, SQLAlchemy, Flask-Login, Flask-Migrate
*   **Database:** MySQL
*   **Frontend:** HTML, CSS, JavaScript, Bootstrap
*   **WSGI Server:** Waitress

## Project Structure

The repository is organized to separate concerns, making it easier to navigate and maintain.

```
/
├── app.py                  # Main Flask application entrypoint
├── config.py               # Configuration loader (from .env)
├── requirements.txt        # Project dependencies
├── models/
│   └── models.py           # SQLAlchemy database models
├── routes/
│   ├── admin.py            # Routes for the admin panel
│   ├── api.py              # RESTful API endpoints for the frontend
│   ├── auth.py             # Authentication routes (login/logout)
│   └── gia.py              # Routes for the GIA (employee) portal
├── static/
│   ├── css/                # Stylesheets
│   └── js/                 # JavaScript for frontend logic
└── templates/
    ├── admin/              # Admin-facing HTML templates
    ├── auth/               # Auth-related templates (login page)
    └── gia/                # GIA-facing HTML templates
```

## Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

*   Python 3.8+
*   MySQL Server
*   A virtual environment tool (e.g., `venv`)

### Configuration

1.  Create a `.env` file in the root directory of the project.
2.  Add the following environment variables, replacing the placeholder values with your own:

    ```env
    # Flask Configuration
    SECRET_KEY='your_strong_secret_key_here'

    # Database Configuration
    DB_HOST='localhost'
    DB_USER='your_mysql_user'
    DB_PASS='your_mysql_password'
    DB_NAME='tickr_db'
    ```

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/earlhsjks/tickr.git
    cd tickr
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set up the database:**
    *   Ensure your MySQL server is running and you have created a database named `tickr_db` (or the name you specified in `.env`).
    *   Initialize the database schema and create the default admin user by uncommenting `initialize_database()` in `app.py` and running the app once.

    ```python
    # In app.py, temporarily uncomment this line:
    # initialize_database()

    # The default superadmin credentials are:
    # Username: superadmin
    # Password: admin123
    ```

### Running the Application

Once the setup is complete, run the Flask application:

```sh
python app.py
```

The application will be available at `http://127.0.0.1:5001`.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
