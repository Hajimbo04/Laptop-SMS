import csv
import os
from datetime import datetime

# Data
SERVICES = {
    "1." : "Remove virus, malware or spyware" ,
    "2." : "Troubleshot and fix computer running slow" ,
    "3." : "Laptop screen replacement" ,
    "4." : "Laptop battery replacement" ,
    "5." : "Operating system format and installation" ,
    "6." : "Data backup and recovery"
}

_normal_prices = {
    "1." : "50.00" , "2." : "60.00" , "3." : "380.00" ,
    "4." : "180.00" , "5." : "100.00" , "6." : "80.00"
}
_urgent_prices = {
    "1." : "80.00" , "2." : "90.00" , "3." : "430.00" ,
    "4." : "210.00" , "5." : "150.00" , "6." : "130.00"
}

USERS_FILE = 'users.csv'
JOBS_FILE = 'jobs.csv'

# Functions
def get_price(service_key, urgency):
    """Returns the price string based on service and urgency."""
    if urgency == "Normal":
        return _normal_prices.get(service_key, "0.00")
    elif urgency == "Urgent":
        return _urgent_prices.get(service_key, "0.00")
    return "0.00"

def check_files():
    """
    Checks if required CSV files exist. If not, creates them with headers.
    Returns: (Boolean Success, String Message)
    """
    try:
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['username', 'password', 'name', 'phone', 'role'])
                # Default users
                writer.writerow(['admin', 'admin123', 'Default Admin', '0123456789', 'Admin'])
                writer.writerow(['recep', 'recep123', 'Receptionist Ali', '0122223333', 'Receptionist'])
                writer.writerow(['tech', 'tech123', 'Technician Abu', '0144445555', 'Technician'])
                writer.writerow(['cust', 'cust123', 'Customer Siti', '0166667777', 'Customer'])

        if not os.path.exists(JOBS_FILE):
            with open(JOBS_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['job_id', 'customer_username', 'service_id', 'urgency', 'price', 
                                 'status', 'date_requested', 'date_completed', 'technician_notes'])
        
        return True, "Files check complete."
    except IOError as e:
        return False, f"File System Error: {e}"

# User Management
def authenticate_user(username, password):
    """
    Checks credentials.
    Returns: (Role, Name) if success, or (None, None) if fail.
    """
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username and row['password'] == password:
                    return row['role'], row['name']
    except FileNotFoundError:
        return None, None
    return None, None

def get_user_details(username_to_find):
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username_to_find:
                    return row 
    except Exception:
        return None
    return None 

def register_user(username, password, name, phone, role):
    """
    Registers a new user.
    Returns: (Boolean Success, String Message)
    """
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username:
                    return False, f"Username '{username}' already exists."
    except FileNotFoundError:
        pass 

    try:
        with open(USERS_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([username, password, name, phone, role])
            return True, "User registered successfully."
    except IOError as e:
        return False, f"Write Error: {e}"

def update_user_profile(username_to_update, new_password, new_name, new_phone):
    users_data = []
    user_found = False
    
    try:
        with open(USERS_FILE, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames 
            if not fieldnames: return False, "Corrupt file"

            for row in reader:
                if row['username'] == username_to_update:
                    row['password'] = new_password
                    row['name'] = new_name
                    row['phone'] = new_phone
                    user_found = True
                users_data.append(row)
        
        if not user_found: return False, "User not found."

        with open(USERS_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames) 
            writer.writeheader()
            writer.writerows(users_data)
        return True, "Profile updated."
    except Exception as e:
        return False, str(e)

def get_all_customers():
    customers = []
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['role'] == 'Customer':
                    customers.append(row['username'])
    except Exception:
        pass
    return customers

# Job Management
def create_job(customer_username, service_id_key, urgency):
    price = get_price(service_id_key, urgency)
    job_id = 1
    header_present = False
    
    try:
        is_new_file = not os.path.exists(JOBS_FILE) or os.path.getsize(JOBS_FILE) == 0
        with open(JOBS_FILE, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)
            if len(rows) > 0: header_present = True 
            if len(rows) > 1: job_id = int(rows[-1][0]) + 1 
    except Exception:
        is_new_file = True 
    
    date_requested = datetime.now().strftime("%Y-%m-%d")
    status = "Pending"
    
    try:
        with open(JOBS_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if is_new_file or not header_present:
                 writer.writerow(['job_id', 'customer_username', 'service_id', 'urgency', 'price', 
                                 'status', 'date_requested', 'date_completed', 'technician_notes'])
            writer.writerow([job_id, customer_username, service_id_key, urgency, price, 
                             status, date_requested, "N/A", "N/A"])
        return True, "Job created successfully."
    except IOError as e:
        return False, str(e)

def get_all_jobs():
    jobs_list = []
    try:
        with open(JOBS_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                jobs_list.append(row)
    except Exception:
        pass
    return jobs_list

def get_jobs_for_customer(customer_username):
    all_jobs = get_all_jobs()
    return [job for job in all_jobs if job['customer_username'] == customer_username]

def update_job_completion(job_id_to_update, new_notes, collection_date):
    """
    Updates the job status to Completed and sets the manual collection date.
    """
    jobs_data = []
    job_found = False

    try:
        with open(JOBS_FILE, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['job_id'] == str(job_id_to_update):
                    row['technician_notes'] = new_notes
                    row['date_completed'] = collection_date 
                    row['status'] = 'Completed'
                    job_found = True
                jobs_data.append(row)

        if not job_found: return False, "Job ID not found"

        with open(JOBS_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames) 
            writer.writeheader()
            writer.writerows(jobs_data)
        return True, "Job completed."
    except Exception as e:
        return False, str(e)

def update_customer_service(job_id_to_update, new_service_id, new_urgency):
    jobs_data = []
    job_found = False
    update_success = False
    error_msg = ""

    try:
        with open(JOBS_FILE, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['job_id'] == str(job_id_to_update):
                    job_found = True
                    if row['status'] != 'Pending':
                        error_msg = f"Cannot change. Status is '{row['status']}'."
                    else:
                        row['service_id'] = new_service_id
                        row['urgency'] = new_urgency
                        row['price'] = get_price(new_service_id, new_urgency)
                        update_success = True
                jobs_data.append(row)

        if not job_found: return False, "Job ID not found."
        if not update_success: return False, error_msg

        with open(JOBS_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames) 
            writer.writeheader()
            writer.writerows(jobs_data)
        return True, "Service updated."
    except Exception as e:
        return False, str(e)

def process_payment(job_id_to_pay):
    jobs_data = []
    job_found = False
    payment_success = False
    error_msg = ""
    
    try:
        with open(JOBS_FILE, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['job_id'] == str(job_id_to_pay):
                    job_found = True
                    if row['status'] == 'Completed':
                        row['status'] = 'Paid' 
                        payment_success = True
                    elif row['status'] == 'Paid':
                        error_msg = "Job already paid."
                    elif row['status'] == 'Pending':
                        error_msg = "Job not completed yet."
                jobs_data.append(row) 

        if not job_found: return False, "Job ID not found"
        if not payment_success: return False, error_msg

        with open(JOBS_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames) 
            writer.writeheader()
            writer.writerows(jobs_data)
        return True, "Payment processed."
    except Exception as e:
        return False, str(e)

def calculate_total_income():
    total = 0.0
    for job in get_all_jobs():
        try:
            total += float(job.get('price', 0.0))
        except: pass
    return total

def get_monthly_report_data(selected_month):
    """
    Returns: (filtered_jobs_list, service_counts_dict, total_income)
    Now sorts jobs chronologically by date_requested.
    """
    all_jobs = get_all_jobs()
    filtered_jobs = []
    service_counts = {} 
    monthly_total_income = 0.0
    
    for job in all_jobs:
        try:
            date_str = job.get('date_requested', '')
            if date_str:
                job_month = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m')
                
                if job_month == selected_month:
                    filtered_jobs.append(job)
                    service_id = job.get('service_id')
                    service_counts[service_id] = service_counts.get(service_id, 0) + 1
                    monthly_total_income += float(job.get('price', 0.0))
        except: pass
    
    filtered_jobs.sort(key=lambda x: x['date_requested'])
    return filtered_jobs, service_counts, monthly_total_income

def get_available_months():
    months = set()
    for job in get_all_jobs():
        try:
            d = job.get('date_requested', '')
            if d: months.add(datetime.strptime(d, '%Y-%m-%d').strftime('%Y-%m'))
        except: pass
    return sorted(list(months), reverse=True) if months else ["No Data"]