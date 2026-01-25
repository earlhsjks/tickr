<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">

<img src="readmeai/assets/logos/purple.svg" width="30%" style="position: relative; top: 0; right: 0;" alt="Project Logo"/>

# <code>❯ REPLACE-ME</code>

<em>Transforming Time Management with Intelligent Automation Solutions</em>

<!-- BADGES -->
<!-- local repository, no metadata badges. -->

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/Python-3776AB.svg?style=default&logo=Python&logoColor=white" alt="Python">

</div>
<br>

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
    - [Project Index](#project-index)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

Introducing Tickr, a comprehensive developer tool for building robust, scalable, and secure web applications.

**Why Tickr?**

This project provides a modular design, robust security features, and comprehensive user management capabilities. The core features include:

- **🔒 Secure Authentication:** Ensures secure authentication and password management using Flask-Login and Werkzeug libraries.
- **💻 Comprehensive User Management:** Provides a user-friendly interface for managing employee schedules, attendance records, and system settings.
- **📊 Automated Reporting:** Generates daily time records (DTR) reports and exports them as PDFs, saving time and effort in generating reports manually.
- **⚙️ Customizable System Settings:** Allows administrators to configure unit head information, system policies, default time settings, and additional settings for adaptability.
- **🔧 Modular Design:** Reduces complexity and makes it easier to maintain the codebase with a modular design.

---

## Features

|      | Component       | Details                              |
| :--- | :-------------- | :----------------------------------- |
| ⚙️  | **Architecture**  | <ul><li>Monolithic architecture</li></ul> |
| 🔩 | **Code Quality**  | <ul><li>Python code with PEP8 compliance</li><li>No linters or formatters detected in the codebase</li></ul> |
| 📄 | **Documentation** | <ul><li>No documentation found in the project</li></ul> |
| 🔌 | **Integrations**  | <ul><li>Uses pip for package management</li><li>Depends on 'html', 'license', and 'requirements.txt'</li></ul> |
| 🧩 | **Modularity**    | <ul><li>No clear modularity or separation of concerns in the codebase</li></ul> |
| 🧪 | **Testing**       | <ul><li>No unit tests or integration tests detected in the codebase</li></ul> |
| ⚡️  | **Performance**   | <ul><li>No performance optimizations or caching mechanisms detected in the codebase</li></ul> |
| 🛡️ | **Security**      | <ul><li>No security-related dependencies or libraries detected in the codebase</li></ul> |
| 📦 | **Dependencies**  | <ul><li>'html', 'license', and 'requirements.txt' are project dependencies</li></ul> |
| 🚀 | **Scalability**   | <ul><li>No clear scalability features or mechanisms detected in the codebase</li></ul> |

Note that this analysis is based on the provided context, which includes:

* Programming language: Python
* Project dependencies: 'html', 'license', and 'requirements.txt'
* CICD tools: pip, html, license, python, requirements.txt, html, py, txt (note: some of these seem to be duplicates or unrelated)
* Containerization: None
* Documentation: None
* Package manager: pip

---

## Project Structure

```sh
└── /
    ├── app.py
    ├── config.py
    ├── LICENSE
    ├── models
    │   └── models.py
    ├── requirements.txt
    ├── routes
    │   ├── admin.py
    │   ├── api.py
    │   ├── auth.py
    │   └── gia.py
    ├── static
    │   ├── css
    │   ├── js
    │   └── media
    └── templates
        ├── admin
        ├── auth
        ├── gia
        ├── maintenance.html
        └── template.html
```

### Project Index

<details open>
	<summary><b><code>/</code></b></summary>
	<!-- __root__ Submodule -->
	<details>
		<summary><b>__root__</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ __root__</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/app.py'>app.py</a></b></td>
					<td style='padding: 8px;'>- Configures the Flask application, initializing database connections, session management, and login functionality<br>- It sets up routes for authentication, administration, API access, and error handling, ensuring a secure and functional web application<br>- The code also defines user loader and maintenance mode handlers to support robust system operation.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/config.py'>config.py</a></b></td>
					<td style='padding: 8px;'>- Configures database connection settings and application secrets.The Config class retrieves environment variables to establish a MySQL database connection and sets the applications secret key<br>- This enables secure authentication and data storage within the application, ensuring proper functionality and integrity of user data.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/LICENSE'>LICENSE</a></b></td>
					<td style='padding: 8px;'>- Licenses the project under the MIT License, allowing free use, modification, and distribution of the software<br>- Grants permission to deal with the Software without restriction, subject to including copyright and permission notices in all copies or substantial portions<br>- Provides no warranty and disclaims liability for any claims, damages, or other liability arising from the Software or its use.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/requirements.txt'>requirements.txt</a></b></td>
					<td style='padding: 8px;'>- Specifies dependencies for the project, including Flask and its extensions, as well as other libraries such as MySQL connector, Waitress, and Pandas<br>- The file outlines the required versions of each dependency to ensure consistent functionality across the codebase.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- models Submodule -->
	<details>
		<summary><b>models</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ models</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/models/models.py'>models.py</a></b></td>
					<td style='padding: 8px;'>- The User model defines the structure of user data within the application, encompassing attributes such as user ID, name, role, and attendance records<br>- It establishes relationships with Attendance, Schedule, and Logs models, facilitating data synchronization across these entities<br>- The model also includes methods for password hashing and retrieval<br>- This module serves as a foundation for user management within the system.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- routes Submodule -->
	<details>
		<summary><b>routes</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ routes</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/routes/admin.py'>admin.py</a></b></td>
					<td style='padding: 8px;'>- Admin Dashboard Routes ConfigurationThis module defines routes for the admin dashboard, providing access to various features such as user management, schedule viewing, and log analysis<br>- It also includes settings and account management pages, ensuring administrators have a comprehensive view of system operations<br>- The configuration enables role-based access control, restricting certain actions to superadmins or admins only.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/routes/api.py'>api.py</a></b></td>
					<td style='padding: 8px;'>- Project Name]<strong>==========================</strong>Summary:<strong>The <code>routes/api.py</code> file is a core component of the project's API architecture, responsible for handling administrative routes and system logging<br>- This module provides a centralized point for managing user data, scheduling, and global settings.</strong>Key Functionality:<strong><em> Provides secure access to user data through the <code>/users-data</code> endpoint, restricted to superadmin and admin roles.</em> Enables system logging with detailed entries, including user actions, timestamps, and client IP addresses.<em> Integrates with other project components, such as models and scheduling (commented out).</strong>Purpose:<strong>This code file serves as a critical building block for the project's API infrastructure, ensuring secure data access and robust logging mechanisms<br>- It is essential for maintaining the integrity and security of user data and system operations.</strong>Additional Context:</em><em>* The project structure suggests a modular design with separate components for routes, models, and scheduling.</em> The use of Flask-Login and Werkzeug libraries indicates a focus on authentication and password management.* The commented-out APScheduler import implies a potential future integration for automated task scheduling.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/routes/auth.py'>auth.py</a></b></td>
					<td style='padding: 8px;'>- Handles user authentication for the application, providing routes for login and logout functionality<br>- The /login route verifies user credentials and logs users into their respective portals (GIA or Admin), while the /logout route securely logs out authenticated users<br>- This module integrates with the systems logging mechanism to record user activity.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/routes/gia.py'>gia.py</a></b></td>
					<td style='padding: 8px;'>- Attendance Flag Checker=====================Enforces attendance rules by detecting late arrivals, early departures, and overtime based on user schedules and global settings.This module integrates with the main application to provide a robust attendance tracking system<br>- It ensures compliance with strict schedule policies while excluding weekends and allowing for buffer times.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- templates Submodule -->
	<details>
		<summary><b>templates</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ templates</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/templates/maintenance.html'>maintenance.html</a></b></td>
					<td style='padding: 8px;'>- Defines the maintenance page layout and content for the admin dashboard, extending from a base template with customized title, page title, and breadcrumb settings<br>- It includes links to external CSS files, Bootstrap JavaScript libraries, and a custom CSS file, rendering a visually appealing maintenance message with an icon and text.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='/templates/template.html'>template.html</a></b></td>
					<td style='padding: 8px;'>- Defines the layout and structure of the admin dashboard page, extending from a base template and setting up breadcrumb navigation<br>- Establishes the page title, content block, and breadcrumb labels, providing a foundation for adding dynamic content to the dashboard view<br>- Essential component in the projects overall architecture, enabling consistent design and user experience across admin pages.</td>
				</tr>
			</table>
			<!-- admin Submodule -->
			<details>
				<summary><b>admin</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ templates.admin</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/templates/admin/audit_logs.html'>audit_logs.html</a></b></td>
							<td style='padding: 8px;'>- Displays audit logs for system activities, allowing users to filter by date range, user, action type, and search within the logs<br>- Provides a table view of log entries with details on date, time, user, action, IP address, and allows pagination through multiple pages of results.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/templates/admin/base.html'>base.html</a></b></td>
							<td style='padding: 8px;'>- Tickr<strong><em>*File:</strong> <code>templates/admin/base.html</code><strong>Summary:</strong>This code defines the base HTML template for the admin section of the Tickr application<br>- It serves as a foundation for all admin pages, providing a consistent layout and styling.<strong>Purpose:</strong>The purpose of this file is to establish a common structure and design elements for the admin interface, ensuring a cohesive user experience across various admin pages.<strong>Key Features:</strong></em> Defines the basic HTML structure with a title block that can be overridden by child templates<em> Includes essential metadata (viewport, favicon, etc.)</em> Links to external CSS libraries (Bootstrap Icons) and internal static assets* Sets up a consistent layout for the admin interfaceThis template is a crucial component of the Tickr applications architecture, providing a solid foundation for building and maintaining the admin section.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/templates/admin/daily_logs.html'>daily_logs.html</a></b></td>
							<td style='padding: 8px;'>A customizable page title and breadcrumb navigation<em> Real-time search functionality for employees</em> An Add Log button for manual log entry* Integration with external CSS libraries (Bootstrap, Font Awesome) and internal stylesheetsThis template is an essential component of the Tickr admin dashboard, providing a critical interface for managing employee time tracking data.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/templates/admin/dashboard.html'>dashboard.html</a></b></td>
							<td style='padding: 8px;'>- Dashboard Template**This template defines the layout and content of the admin dashboard, providing a centralized view of key metrics and activities<br>- It extends the base HTML template and includes various blocks to display user information, statistics, recent activity logs, and summary metrics<br>- The template is designed to be dynamic, fetching data from the applications database and displaying it in an organized manner.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/templates/admin/dtr_report.html'>dtr_report.html</a></b></td>
							<td style='padding: 8px;'>- Generates daily time records (DTR) reports for users, displaying attendance data in a tabular format with calculated total hours worked<br>- The report includes user information, shift details, and certification sections<br>- It is designed to be printed and used as a record-keeping tool.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/templates/admin/export_dtr.html'>export_dtr.html</a></b></td>
							<td style='padding: 8px;'>- Generates and exports DTR reports as PDFs, allowing administrators to select a month and download attendance summaries<br>- This template extends the base admin layout, providing a user-friendly interface with a date picker and generate/download button<br>- The script behind it enables generating and downloading reports upon button click.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/templates/admin/manual_logs.html'>manual_logs.html</a></b></td>
							<td style='padding: 8px;'>- Summary**This code file, <code>manual_logs.html</code>, is a template responsible for rendering the manual logs page within the Tickr admin dashboard<br>- Its primary function is to provide a user interface for adding or editing attendance logs manually, catering to corrections and special cases.The template extends the base admin layout, incorporating necessary CSS stylesheets and fonts from external sources<br>- It includes a search bar and an Add Manual Log button, allowing users to efficiently navigate and manage manual logs within the system.This file is a crucial component of the Tickr projects administrative interface, enabling administrators to accurately track and record attendance logs for employees.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/templates/admin/profile.html'>profile.html</a></b></td>
							<td style='padding: 8px;'>- Provides User Profile Management Interface**This template enables administrators to manage their profiles by updating personal information and account settings<br>- It includes sections for basic information, password change, and account details, with input fields and buttons for saving changes and changing passwords<br>- The interface is designed to be user-friendly and secure.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/templates/admin/schedule.html'>schedule.html</a></b></td>
							<td style='padding: 8px;'>- Manages Employee Schedules and Broken Time Assignments**This template provides a comprehensive interface for managing employee schedules and broken time assignments within the GIA system<br>- It includes features such as schedule editing, adding broken schedules, and clearing all schedules with confirmation<br>- The design is responsive and user-friendly, ensuring efficient management of employee work hours.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/templates/admin/settings.html'>settings.html</a></b></td>
							<td style='padding: 8px;'>Configures system-wide settings for the Daily Time Record (DTR) system, allowing administrators to customize unit head information, system policies, default time settings, and additional settings.This template enables administrators to manage various aspects of the DTR system, including strict mode, early in and out allowances, overtime permissions, and default working hours.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/templates/admin/users.html'>users.html</a></b></td>
							<td style='padding: 8px;'>- User Management Dashboard**This template provides a comprehensive user management dashboard, allowing administrators to view, add, edit, and delete users with various roles and permissions<br>- The dashboard includes features such as user search, export, refresh, and pagination, ensuring efficient user management<br>- It also includes modals for adding, editing, and deleting users, providing a seamless user experience.</td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- auth Submodule -->
			<details>
				<summary><b>auth</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ templates.auth</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/templates/auth/login.html'>login.html</a></b></td>
							<td style='padding: 8px;'>- One for employees and another for administrators<br>- The login page allows users to input their credentials and submit them for verification<br>- It also includes a toggle link to switch between employee and admin login modes.</td>
						</tr>
					</table>
				</blockquote>
			</details>
			<!-- gia Submodule -->
			<details>
				<summary><b>gia</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ templates.gia</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/templates/gia/access_denied.html'>access_denied.html</a></b></td>
							<td style='padding: 8px;'>- Displays an Access Denied" page when users attempt to access restricted dashboard content from unauthorized networks.This HTML template is used to render a visually appealing and informative error message, providing users with clear instructions on why they are being denied access and how to resolve the issue<br>- It includes links to relevant network information and contact details for system administrators.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/templates/gia/dashboard.html'>dashboard.html</a></b></td>
							<td style='padding: 8px;'>- Dashboard Template Provides User Interface for Time Tracking and Attendance**This HTML template serves as the user interface for the GIA Dashboard, displaying essential information such as total hours worked, on-time days, late days, and absences<br>- It also includes a clock-in feature, recent activity log, and modals for success and error notifications<br>- The template is designed to be responsive and visually appealing, providing users with an intuitive experience for tracking their time and attendance.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='/templates/gia/manual.html'>manual.html</a></b></td>
							<td style='padding: 8px;'>- Generates user manual content for the GIA system, providing an introduction to the platforms features and functionality, as well as guides for employees and administrators on how to use the system effectively<br>- The manual covers attendance management, employee records, and administrative tasks, ensuring users understand their roles and responsibilities within the system.</td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
</details>

---

## Getting Started

### Prerequisites

This project requires the following dependencies:

- **Programming Language:** HTML
- **Package Manager:** Pip

### Installation

Build  from the source and intsall dependencies:

1. **Clone the repository:**

    ```sh
    ❯ git clone ../
    ```

2. **Navigate to the project directory:**

    ```sh
    ❯ cd 
    ```

3. **Install the dependencies:**

<!-- SHIELDS BADGE CURRENTLY DISABLED -->
	<!-- [![pip][pip-shield]][pip-link] -->
	<!-- REFERENCE LINKS -->
	<!-- [pip-shield]: None -->
	<!-- [pip-link]: None -->

	**Using [pip](None):**

	```sh
	❯ echo 'INSERT-INSTALL-COMMAND-HERE'
	```

### Usage

Run the project with:

**Using [pip](None):**
```sh
echo 'INSERT-RUN-COMMAND-HERE'
```

### Testing

 uses the {__test_framework__} test framework. Run the test suite with:

**Using [pip](None):**
```sh
echo 'INSERT-TEST-COMMAND-HERE'
```

---

## Contributing

- **💬 [Join the Discussions](https://LOCAL///discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://LOCAL///issues)**: Submit bugs found or log feature requests for the `` project.
- **💡 [Submit Pull Requests](https://LOCAL///blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your LOCAL account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone .
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to LOCAL**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://LOCAL{///}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=/">
   </a>
</p>
</details>

---

## License

 is protected under the [LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

## Acknowledgments

- Credit `contributors`, `inspiration`, `references`, etc.

<div align="right">

[![][back-to-top]](#top)

</div>


[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square


---
