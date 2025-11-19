# Abu Laptop Repair Service Management System 

A simple, modern desktop app to help manage a laptop repair shop. Built with Python and CustomTkinter, this system comes with a full role-based workflow for Admins, Technicians, Receptionists, and Customers.

## Features:
- **Role-Based Dashboards**: Each role gets its own interface and permissions.
- **Clean Dark Mode UI**: Powered by CustomTkinter for a fresh, modern look.
- **Job Tracking**: Manage repairs from Pending → Completed → Paid.
- **No Database Hassle**: Everything is stored in local CSV files (users.csv, jobs.csv).
- **Receipt Generation**: Customers can download simple text receipts.
- **Reports**: Admins can check monthly revenue and popular services.

## Installation & Setup
1. Clone the Repository

```bash
git clone https://github.com/Hajimbo04/Laptop-SMS.git
cd abu-repair-system
```

3. Install Dependencies
Only one external library is needed:

```python
pip install customtkinter
```

3. Run the App
python main.py

## Default Login Credentials
If users.csv isn’t found, the system will auto-create these accounts:

| Role | Username | Password | Description |
| :--- | :--- | :--- | :--- |
| Admin | admin | admin123 |  Manages staff and views financial reports. |
| Technician | tech | tech123 | Works on repairs and updates job status. |
| Receptionist | recep | recep123 | Handles customers, job intake, payments. |
| Customer | cust | cust123 | Can track repair progress & download receipts. |

## Project Structure
- main.py      → GUI & view logic
- backend.py   → Data logic, CSV handling, authentication
- users.csv    → User accounts
- jobs.csv     → Repair tickets / job data
