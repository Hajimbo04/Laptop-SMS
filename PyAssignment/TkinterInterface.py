import customtkinter as ctk  
import tkinter.messagebox as tkmb  
import csv
import os
from datetime import datetime

# 1. GUI Setup 
ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")  
app = ctk.CTk()  
app.geometry("1280x720")  
app.title("Abu Laptop Repair Service Management System")  

# 2. DATA 
SERVICES = {
    "1." : "Remove virus, malware or spyware" ,
    "2." : "Troubleshot and fix computer running slow" ,
    "3." : "Laptop screen replacement" ,
    "4." : "Laptop battery replacement" ,
    "5." : "Operating system format and installation" ,
    "6." : "Data backup and recovery"
}
normal = {
    "1." : "50.00" ,
    "2." : "60.00" ,
    "3." : "380.00" ,
    "4." : "180.00" ,
    "5." : "100.00" ,
    "6." : "80.00"
}
urgent = {
    "1." : "80.00" ,
    "2." : "90.00" ,
    "3." : "430.00" ,
    "4." : "210.00" ,
    "5." : "150.00" ,
    "6." : "130.00"
}

USERS_FILE = 'users.csv'
JOBS_FILE = 'jobs.csv'
LOGIN_ATTEMPTS = 0

#  3. BACKEND / DATA LOGIC FUNCTIONS 
def check_files():
    """
    Checks if required CSV files exist. If not, creates them with headers.
    """
    if not os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['username', 'password', 'name', 'phone', 'role'])
                writer.writerow(['admin', 'admin123', 'Default Admin', '0123456789', 'Admin'])
                writer.writerow(['recep', 'recep123', 'Receptionist Ali', '0122223333', 'Receptionist'])
                writer.writerow(['tech', 'tech123', 'Technician Abu', '0144445555', 'Technician'])
                writer.writerow(['cust', 'cust123', 'Customer Siti', '0166667777', 'Customer'])
                writer.writerow(['cust2', 'cust456', 'Customer Bala', '0198765432', 'Customer'])
        except IOError as e:
            show_error_message("File Error", f"Failed to create users.csv: {e}")

    if not os.path.exists(JOBS_FILE):
        try:
            with open(JOBS_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['job_id', 'customer_username', 'service_id', 'urgency', 'price', 
                                 'status', 'date_requested', 'date_completed', 'technician_notes'])
        except IOError as e:
            show_error_message("File Error", f"Failed to create jobs.csv: {e}")

def authenticate_user(username, password):
    """
    Checks user credentials against the users.csv file.
    Returns: User's role and name as a tuple (role, name) if successful, else (None, None).
    """
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username and row['password'] == password:
                    return row['role'], row['name']
    except FileNotFoundError:
        show_error_message("Login Error", f"{USERS_FILE} not found. Please run check_files.")
        return None, None
    except Exception as e:
        show_error_message("Login Error", f"An error occurred: {e}")
        return None, None
    return None, None

def get_user_details(username_to_find):
    """
    Fetches the details for a specific user from users.csv.
    Returns a dictionary of user data, or None if not found.
    """
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username_to_find:
                    return row 
    except FileNotFoundError:
        show_error_message("Error", f"{USERS_FILE} not found.")
        return None
    except Exception as e:
        show_error_message("Error", f"An error occurred while reading user details: {e}")
        return None
    return None 

def update_user_profile(username_to_update, new_password, new_name, new_phone):
    """
    Finds a user by username and updates their details.
    This function REWRITES the entire users.csv file.
    """
    users_data = []
    user_found = False
    
    try:
        with open(USERS_FILE, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames 
            if not fieldnames:
                show_error_message("Error", "Users file is empty or corrupt.")
                return False

            for row in reader:
                if row['username'] == username_to_update:
                    row['password'] = new_password
                    row['name'] = new_name
                    row['phone'] = new_phone
                    user_found = True
                users_data.append(row)
    except FileNotFoundError:
        show_error_message("Error", f"{USERS_FILE} not found.")
        return False
    except Exception as e:
        show_error_message("Error", f"Error reading users file: {e}")
        return False

    if not user_found:
        show_error_message("Error", f"User {username_to_update} not found.")
        return False

    try:
        with open(USERS_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames) 
            writer.writeheader()
            writer.writerows(users_data)
        return True 
    except IOError as e:
        show_error_message("Error", f"Failed to write updated users file: {e}")
        return False

def register_user_to_file(username, password, name, phone, role):
    """
    Registers a new user to the users.csv file.
    Checks for duplicate usernames.
    Returns: True if registration is successful, False otherwise.
    """
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username:
                    show_error_message("Registration Failed", f"The username '{username}' already exists. Please choose another one.")
                    return False
    except FileNotFoundError:
        show_error_message("Error", f"{USERS_FILE} not found.")
        return False
    except Exception as e:
        show_error_message("Error", f"An error occurred while reading users: {e}")
        return False

    try:
        with open(USERS_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([username, password, name, phone, role])
            return True
    except IOError as e:
        show_error_message("Registration Failed", f"An error occurred while writing to file: {e}")
        return False

def get_all_customers():
    """
    Reads users.csv and returns a list of all customer usernames.
    """
    customer_list = []

    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['role'] == 'Customer':
                    customer_list.append(row['username']) # Add username to the list
    except FileNotFoundError:
        show_error_message("Error", f"{USERS_FILE} not found.")
    except Exception as e:
        show_error_message("Error", f"Failed to read customers: {e}")
    return customer_list

def create_job_in_file(customer_username, service_id_key, urgency):
    """
    Appends a new job to the jobs.csv file.
    Calculates price and generates a new job_id.
    """
    price = "0.00"
    if urgency == "Normal":
        price = normal.get(service_id_key, "0.00")
    elif urgency == "Urgent":
        price = urgent.get(service_id_key, "0.00")
    
    job_id = 1
    header_present = False

    try:
        is_new_file = not os.path.exists(JOBS_FILE) or os.path.getsize(JOBS_FILE) == 0
        with open(JOBS_FILE, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)
            if len(rows) > 0:
                header_present = True 
            if len(rows) > 1: 
                job_id = int(rows[-1][0]) + 1 
    except FileNotFoundError:
        is_new_file = True
    except Exception as e:
        if "invalid literal" not in str(e): 
             show_error_message("Error", f"Error reading jobs file to get ID: {e}")
             return False
    
    date_requested = datetime.now().strftime("%Y-%m-%d")
    status = "Pending"
    date_completed = "N/A"
    technician_notes = "N/A"
    
    try:
        with open(JOBS_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if is_new_file or not header_present:
                 writer.writerow(['job_id', 'customer_username', 'service_id', 'urgency', 'price', 
                                 'status', 'date_requested', 'date_completed', 'technician_notes'])
            writer.writerow([job_id, customer_username, service_id_key, urgency, price, 
                             status, date_requested, date_completed, technician_notes])
        return True
    except IOError as e:
        show_error_message("Job Creation Failed", f"Error writing to jobs file: {e}")
        return False

def get_all_jobs():
    """
    Reads jobs.csv and returns a list of all jobs (as dictionaries).
    """
    jobs_list = []

    try:
        with open(JOBS_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                jobs_list.append(row)
    except FileNotFoundError:
        show_error_message("Error", f"{JOBS_FILE} not found.")
    except Exception as e:
        show_error_message("Error", f"Failed to read jobs: {e}")
    return jobs_list

def get_jobs_for_customer(customer_username):
    """
    Reads jobs.csv and returns a list of jobs matching the customer_username.
    """
    customer_jobs_list = []

    try:
        with open(JOBS_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['customer_username'] == customer_username:
                    customer_jobs_list.append(row)
    except FileNotFoundError:
        show_error_message("Error", f"{JOBS_FILE} not found.")
    except Exception as e:
        show_error_message("Error", f"Failed to read your jobs: {e}")
    return customer_jobs_list

def update_job_in_file(job_id_to_update, new_notes):
    """
    Finds a job by its ID and updates notes, completion date, and status.
    This function REWRITES the entire jobs.csv file.
    """
    jobs_data = []
    job_found = False

    try:
        with open(JOBS_FILE, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames 
            if not fieldnames:
                show_error_message("Error", "Jobs file is empty or corrupt.")
                return False
                
            for row in reader:
                if row['job_id'] == job_id_to_update:
                    row['technician_notes'] = new_notes
                    row['date_completed'] = datetime.now().strftime("%Y-%m-%d")
                    row['status'] = 'Completed'
                    job_found = True
                jobs_data.append(row)
    except FileNotFoundError:
        show_error_message("Error", f"{JOBS_FILE} not found.")
        return False
    except Exception as e:
        show_error_message("Error", f"Error reading jobs file: {e}")
        return False

    if not job_found:
        show_error_message("Error", f"Job ID {job_id_to_update} not found.")
        return False

    try:
        with open(JOBS_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames) 
            writer.writeheader()
            writer.writerows(jobs_data)
        return True
    except IOError as e:
        show_error_message("Error", f"Failed to write updated jobs file: {e}")
        return False

def update_customer_service(job_id_to_update, new_service_id, new_urgency):
    """
    Finds a job by its ID and updates the service, urgency, and price.
    ONLY works if the job status is 'Pending'.
    This function REWRITES the entire jobs.csv file.
    """
    jobs_data = []
    job_found = False
    update_success = False
    
    try:
        with open(JOBS_FILE, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames 
            if not fieldnames: 
                show_error_message("Error", "Jobs file is empty or corrupt.")
                return False
                
            for row in reader:
                if row['job_id'] == job_id_to_update:
                    job_found = True
                    if row['status'] != 'Pending':
                        show_error_message("Change Failed", f"This job is already '{row['status']}'.\nOnly 'Pending' jobs can be changed.")
                        jobs_data.append(row) 
                        continue 

                    new_price = "0.00"
                    if new_urgency == "Normal":
                        new_price = normal.get(new_service_id, "0.00")
                    elif new_urgency == "Urgent":
                        new_price = urgent.get(new_service_id, "0.00")
                    
                    row['service_id'] = new_service_id
                    row['urgency'] = new_urgency
                    row['price'] = new_price
                    update_success = True

                jobs_data.append(row) 

    except FileNotFoundError:
        show_error_message("Error", f"{JOBS_FILE} not found.")
        return False
    except Exception as e:
        show_error_message("Error", f"Error reading jobs file: {e}")
        return False

    if not job_found:
        show_error_message("Error", f"Job ID {job_id_to_update} not found.")
        return False

    if not update_success:
        return False 

    try:
        with open(JOBS_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames) 
            writer.writeheader()
            writer.writerows(jobs_data)
        return True 
    except IOError as e:
        show_error_message("Error", f"Failed to write updated jobs file: {e}")
        return False

def process_payment_in_file(job_id_to_pay):
    """
    Finds a job by its ID and updates the status to 'Paid'.
    ONLY works if the job status is 'Completed'.
    This function REWRITES the entire jobs.csv file.
    """
    jobs_data = []
    job_found = False
    payment_success = False
    
    try:
        with open(JOBS_FILE, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            if not fieldnames: 
                show_error_message("Error", "Jobs file is empty or corrupt.")
                return False
                
            for row in reader:
                if row['job_id'] == job_id_to_pay:
                    job_found = True
                    if row['status'] == 'Completed':
                        row['status'] = 'Paid' 
                        payment_success = True
                    elif row['status'] == 'Paid':
                        show_error_message("Payment Failed", "This job has already been paid.")
                    elif row['status'] == 'Pending':
                        show_error_message("Payment Failed", "This job is not yet completed by the technician.")
                    
                jobs_data.append(row) 

    except FileNotFoundError:
        show_error_message("Error", f"{JOBS_FILE} not found.")
        return False
    except Exception as e:
        show_error_message("Error", f"Error reading jobs file: {e}")
        return False

    if not job_found:
        show_error_message("Error", f"Job ID {job_id_to_pay} not found.")
        return False

    if payment_success:
        try:
            with open(JOBS_FILE, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames) 
                writer.writeheader()
                writer.writerows(jobs_data)
            return True 
        except IOError as e:
            show_error_message("Error", f"Failed to write updated jobs file: {e}")
            return False
    
    return False 

def calculate_total_income():
    """
    Reads jobs.csv and calculates the sum of all 'price' columns.
    Returns the total income as a float.
    """
    total_income = 0.0
    try:
        with open(JOBS_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    price = float(row['price'])
                    total_income += price
                except (ValueError, TypeError):
                    print(f"Warning: Skipping invalid price '{row['price']}' for job ID {row['job_id']}")
    except FileNotFoundError:
        show_error_message("Error", f"{JOBS_FILE} not found.")
        return 0.0
    except Exception as e:
        show_error_message("Error", f"Failed to calculate income: {e}")
        return 0.0
    
    return total_income

def get_available_months():
    """
    Reads all jobs and returns a sorted list of unique months (YYYY-MM)
    that have at least one job.
    """
    available_months = set()
    try:
        with open(JOBS_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    date_str = row.get('date_requested', '')
                    if date_str:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        available_months.add(date_obj.strftime('%Y-%m'))
                except ValueError:
                    print(f"Warning: Skipping invalid date format for job ID {row.get('job_id')}")
                    
    except FileNotFoundError:
        return []
    except Exception as e:
        show_error_message("Error", f"Failed to read job dates: {e}")
        return []

    if not available_months:
        return ["No job data found"]
        
    return sorted(list(available_months), reverse=True)


#  4. FRONTEND / UI FUNCTIONS 
def show_error_message(title, message):
    """A helper function to show an error message box."""
    tkmb.showerror(title, message)

def show_info_message(title, message):
    """A helper function to show an info message box."""
    tkmb.showinfo(title, message)

def logout():
    """
    Logs out the current user and returns to the login screen.
    """
    global CURRENT_USER, global_welcome_label, dashboard_frame, LOGIN_ATTEMPTS
    
    for widget in dashboard_frame.winfo_children():
        widget.destroy()
        
    dashboard_frame.pack_forget()
    
    CURRENT_USER = {}
    global_welcome_label = None
    
    LOGIN_ATTEMPTS = 0
    
    app.geometry("1280x720")
    app.title("Abu Laptop Repair Service Management System")

    user_entry.delete(0, 'end')
    pass_entry.delete(0, 'end')

    login_frame.pack(fill='both', expand=True) 

# --- Pop-up Window Functions ---
def show_receipt_window(job_to_pay, refresh_callback):
    """
    Processes payment and displays a receipt.
    This window is modal and calls the refresh_callback on close.
    """
    payment_success = process_payment_in_file(job_to_pay['job_id'])
    
    if not payment_success:
        refresh_callback()
        return

    receipt_window = ctk.CTkToplevel(app)
    receipt_window.title(f"Receipt for Job ID: {job_to_pay['job_id']}")
    receipt_window.geometry("450x550")
    receipt_window.transient(app)
    receipt_window.grab_set()

    frame = ctk.CTkFrame(master=receipt_window)
    frame.pack(pady=20, padx=20, fill='both', expand=True)
    
    title_label = ctk.CTkLabel(master=frame, text="Payment Successful", font=("Arial", 18, "bold"), text_color="green")
    title_label.pack(pady=10)
    
    customer_data = get_user_details(job_to_pay['customer_username'])
    customer_name = customer_data.get('name', 'N/A') if customer_data else 'N/A'
    customer_phone = customer_data.get('phone', 'N/A') if customer_data else 'N/A'
    
    receipt_text = (
        "--------------------------------------------------\n"
        f" RECEIPT OF PAYMENT\n"
        "--------------------------------------------------\n\n"
        f"Job ID:\t\t{job_to_pay['job_id']}\n"
        f"Payment Status:\tPAID\n"
        f"Payment Date:\t{datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        "--- Customer Details ---\n"
        f"Customer Name:\t{customer_name}\n"
        f"Username:\t\t{job_to_pay['customer_username']}\n"
        f"Phone:\t\t{customer_phone}\n\n"

        "--- Service Details ---\n"
        f"Date Requested:\t{job_to_pay['date_requested']}\n"
        f"Date Completed:\t{job_to_pay['date_completed']}\n"
        f"Service:\t\t{SERVICES.get(job_to_pay['service_id'], 'N/A')}\n"
        f"Urgency:\t\t{job_to_pay['urgency']}\n"
        f"Tech Notes:\t{job_to_pay['technician_notes']}\n\n"
        
        "--------------------------------------------------\n"
        f"TOTAL AMOUNT PAID: \tRM {job_to_pay['price']}\n"
        "--------------------------------------------------\n\n"
        "Thank you for your business!\n"
    )

    receipt_textbox = ctk.CTkTextbox(master=frame, height=350, width=400, font=("Courier", 12))
    receipt_textbox.pack(pady=5, padx=10, fill="both", expand=True)
    receipt_textbox.insert("1.0", receipt_text)
    receipt_textbox.configure(state="disabled") 
    
    def on_close_receipt():
        """Handle closing the receipt."""
        refresh_callback() 
        receipt_window.destroy() 
        
    close_button = ctk.CTkButton(master=frame, text="Close", command=on_close_receipt)
    close_button.pack(pady=10)

    receipt_window.protocol("WM_DELETE_WINDOW", on_close_receipt)


def show_payment_list_window():
    """
    Creates a pop-up for the Receptionist to view jobs and accept payment.
    """
    payment_list_window = ctk.CTkToplevel(app)
    payment_list_window.title("Accept Customer Payment")
    payment_list_window.geometry("1100x700") 
    payment_list_window.transient(app)
    payment_list_window.grab_set()

    title_label = ctk.CTkLabel(master=payment_list_window, text="Process Customer Payments", font=("Arial", 18, "bold"))
    title_label.pack(pady=10)

    scroll_frame = ctk.CTkScrollableFrame(master=payment_list_window)
    scroll_frame.pack(pady=10, padx=20, fill='both', expand=True)

    def refresh_payment_list():
        """Inner function to reload all job cards."""
        for widget in scroll_frame.winfo_children():
            widget.destroy()

        jobs = get_all_jobs()

        if not jobs:
            ctk.CTkLabel(master=scroll_frame, text="No jobs found in the system.", font=("Arial", 14)).pack(pady=20)
            return

        for job in jobs:
            job_frame = ctk.CTkFrame(master=scroll_frame, border_width=2)
            job_frame.pack(fill='x', expand=True, padx=10, pady=10)
            
            # Job Details 
            left_frame = ctk.CTkFrame(master=job_frame, fg_color="transparent")
            left_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)
            
            right_frame = ctk.CTkFrame(master=job_frame, fg_color="transparent", width=200)
            right_frame.pack(side="right", fill="none", padx=15, pady=10)

            id_label = ctk.CTkLabel(master=left_frame, text=f"Job ID: {job['job_id']}", font=("Arial", 16, "bold"))
            id_label.pack(anchor="w")
            
            customer_label = ctk.CTkLabel(master=left_frame, text=f"Customer: {job['customer_username']}")
            customer_label.pack(anchor="w", pady=2)
            
            price_label = ctk.CTkLabel(master=left_frame, text=f"Amount: RM {job['price']}", font=("Arial", 14))
            price_label.pack(anchor="w", pady=2)
            
            status_label = ctk.CTkLabel(master=left_frame, text=f"Status: {job['status']}", font=("Arial", 14, "bold"))
            status_label.pack(anchor="w", pady=2)
            
            if job['status'] == 'Completed':
                pay_button = ctk.CTkButton(
                    master=right_frame, 
                    text="Process Payment",
                    fg_color="green",
                    hover_color="dark green",
                    command=lambda current_job=job: show_receipt_window(current_job, refresh_payment_list)
                )
                pay_button.pack(fill="x")
            elif job['status'] == 'Paid':
                paid_label = ctk.CTkButton(
                    master=right_frame, 
                    text="Already Paid",
                    state="disabled",
                    fg_color="gray50"
                )
                paid_label.pack(fill="x")
            elif job['status'] == 'Pending':
                pending_label = ctk.CTkButton(
                    master=right_frame, 
                    text="Not Completed",
                    state="disabled"
                )
                pending_label.pack(fill="x")

    refresh_payment_list()


def show_monthly_report_window():
    """
    Creates a pop-up for the Admin to view a monthly service report.
    """
    report_window = ctk.CTkToplevel(app)
    report_window.title("Monthly Service Report")
    report_window.geometry("600x700") 
    report_window.transient(app)
    report_window.grab_set()

    frame = ctk.CTkFrame(master=report_window)
    frame.pack(pady=20, padx=20, fill='both', expand=True)
    title_label = ctk.CTkLabel(master=frame, text="Service Report Generator", font=("Arial", 18, "bold"))
    title_label.pack(pady=10)
    month_label = ctk.CTkLabel(master=frame, text="Select Month to Report:")
    month_label.pack()

    all_jobs = get_all_jobs() 
    available_months = get_available_months()
    
    month_combobox = ctk.CTkComboBox(master=frame, values=available_months, width=200)
    month_combobox.set(available_months[0]) 
    month_combobox.pack(pady=5, padx=10)
    report_frame = ctk.CTkScrollableFrame(master=frame, height=350, fg_color="gray20")
    report_frame.pack(pady=10, padx=10, fill='x', expand=True)
    initial_report_label = ctk.CTkLabel(master=report_frame, text="Select a month and click 'Generate'.")
    initial_report_label.pack(pady=20)

    def on_generate_report_click():
        """
        Inner function to filter jobs and display the report.
        """
        for widget in report_frame.winfo_children():
            widget.destroy()

        selected_month = month_combobox.get()
        if not selected_month or selected_month == "No job data found":
            ctk.CTkLabel(master=report_frame, text="No data to report.").pack()
            return

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
            except Exception as e:
                print(f"Warning: Error processing job {job.get('job_id')}: {e}")

        if not filtered_jobs:
            ctk.CTkLabel(master=report_frame, text="No jobs found for this month.").pack()
            return
            
        summary_frame = ctk.CTkFrame(master=report_frame, fg_color="gray25")
        summary_frame.pack(fill="x", pady=5, padx=5)

        ctk.CTkLabel(master=summary_frame, text=f"Report for: {selected_month}", font=("Arial", 16, "bold")).pack(pady=5)
        ctk.CTkLabel(master=summary_frame, text=f"Total Jobs: {len(filtered_jobs)}", font=("Arial", 14)).pack(pady=2, anchor="w", padx=10)
        ctk.CTkLabel(master=summary_frame, text=f"Total Income: RM {monthly_total_income:.2f}", font=("Arial", 14)).pack(pady=2, anchor="w", padx=10)

        breakdown_frame = ctk.CTkFrame(master=report_frame)
        breakdown_frame.pack(fill="x", pady=5, padx=5)
        
        ctk.CTkLabel(master=breakdown_frame, text="Service Breakdown:", font=("Arial", 14, "bold")).pack(pady=5, anchor="w", padx=10)
        
        if not service_counts:
             ctk.CTkLabel(master=breakdown_frame, text="- No services found -", anchor="w", padx=10).pack()
        
        sorted_service_keys = sorted(service_counts.keys(), key=lambda x: int(x.strip('.')))

        for service_id in sorted_service_keys:
            count = service_counts[service_id]
            service_desc = SERVICES.get(service_id, "Unknown Service")
            report_line = f"- ({service_id}) {service_desc}: {count} job(s)"
            ctk.CTkLabel(master=breakdown_frame, text=report_line).pack(anchor="w", padx=20, pady=2)

    generate_button = ctk.CTkButton(master=frame, text="Generate Report", command=on_generate_report_click)
    generate_button.pack(pady=10, padx=10)


def show_total_income_window():
    """
    Creates a pop-up window to display the total calculated income.
    """
    income_window = ctk.CTkToplevel(app)
    income_window.title("Total Income Report")
    income_window.geometry("300x150")
    income_window.transient(app)
    income_window.grab_set()
    
    frame = ctk.CTkFrame(master=income_window)
    frame.pack(pady=20, padx=20, fill='both', expand=True)
    total = calculate_total_income()
    label = ctk.CTkLabel(master=frame, text="Total System Income", font=("Arial", 16))
    label.pack(pady=(10, 5), padx=10)
    income_label = ctk.CTkLabel(master=frame, text=f"RM {total:.2f}", font=("Arial", 20, "bold"), text_color="green")
    income_label.pack(pady=(5, 15), padx=10)


def show_update_profile_window():
    """
    Creates a pop-up for the logged-in user to update their profile.
    Reads from CURRENT_USER global to know who is logged in.
    """
    username = CURRENT_USER.get('username')
    if not username:
        show_error_message("Error", "Could not find current user. Please log in again.")
        return

    user_data = get_user_details(username)
    if not user_data:
        show_error_message("Error", f"Could not fetch details for {username}.")
        return
        
    profile_window = ctk.CTkToplevel(app)
    profile_window.title(f"Update Profile ({username})")
    profile_window.geometry("350x400") 
    profile_window.transient(app)
    profile_window.grab_set()
    
    frame = ctk.CTkFrame(master=profile_window)
    frame.pack(pady=20, padx=20, fill='both', expand=True)

    label = ctk.CTkLabel(master=frame, text="Update Your Details", font=("Arial", 16))
    label.pack(pady=12, padx=10)

    # --- Entry Fields ---
    name_label = ctk.CTkLabel(master=frame, text="Full Name:")
    name_label.pack(pady=(5,0), padx=10, anchor="w")
    name_entry = ctk.CTkEntry(master=frame, width=250)
    name_entry.insert(0, user_data.get('name', '')) 
    name_entry.pack(pady=5, padx=10)
    
    phone_label = ctk.CTkLabel(master=frame, text="Phone Number:")
    phone_label.pack(pady=(5,0), padx=10, anchor="w")
    phone_entry = ctk.CTkEntry(master=frame, width=250)
    phone_entry.insert(0, user_data.get('phone', '')) 
    phone_entry.pack(pady=12, padx=10)
    
    password_label = ctk.CTkLabel(master=frame, text="Password:")
    password_label.pack(pady=(5,0), padx=10, anchor="w")
    password_entry = ctk.CTkEntry(master=frame, width=250, show="*")
    password_entry.insert(0, user_data.get('password', '')) 
    password_entry.pack(pady=12, padx=10)

    def on_save_click():
        """
        Inner function to handle the save button click.
        """
        new_name = name_entry.get()
        new_phone = phone_entry.get()
        new_password = password_entry.get()

        if not new_name or not new_phone or not new_password:
            show_error_message("Empty Fields", "Please fill in all fields.")
            return

        if update_user_profile(username, new_password, new_name, new_phone):
            show_info_message("Success", "Your profile has been updated successfully.")
            
            if global_welcome_label:
                global_welcome_label.configure(text=f"Welcome, {new_name}!")
            
            CURRENT_USER['name'] = new_name
            
            profile_window.destroy() # Close the pop-up

    save_button = ctk.CTkButton(master=frame, text="Save Changes", command=on_save_click)
    save_button.pack(pady=20, padx=10)


def show_register_user_window(role_to_register):
    """
    Creates a new pop-up window (Toplevel) for registering a new user.
    """
    reg_window = ctk.CTkToplevel(app)
    reg_window.title(f"Register New {role_to_register}")
    reg_window.geometry("350x400") 
    reg_window.transient(app)  
    reg_window.grab_set()     
    
    frame = ctk.CTkFrame(master=reg_window)
    frame.pack(pady=20, padx=20, fill='both', expand=True)
    label = ctk.CTkLabel(master=frame, text=f"New {role_to_register} Details", font=("Arial", 16))
    label.pack(pady=12, padx=10)

    name_entry = ctk.CTkEntry(master=frame, placeholder_text="Full Name")
    name_entry.pack(pady=12, padx=10)
    phone_entry = ctk.CTkEntry(master=frame, placeholder_text="Phone Number")
    phone_entry.pack(pady=12, padx=10)
    username_entry = ctk.CTkEntry(master=frame, placeholder_text="New Username")
    username_entry.pack(pady=12, padx=10)
    password_entry = ctk.CTkEntry(master=frame, placeholder_text="New Password", show="*")
    password_entry.pack(pady=12, padx=10)

    def on_register_click():
        """
        Inner function to handle the register button click.
        Gathers data from entries and calls the backend function.
        """
        name = name_entry.get()
        phone = phone_entry.get()
        username = username_entry.get()
        password = password_entry.get()

        if not name or not phone or not username or not password:
            show_error_message("Empty Fields", "Please fill in all fields.")
            return

        if register_user_to_file(username, password, name, phone, role_to_register):
            show_info_message("Success", f"{role_to_register} '{name}' has been registered successfully.")
            reg_window.destroy() 

    register_button = ctk.CTkButton(master=frame, text="Register User", command=on_register_click)
    register_button.pack(pady=20, padx=10)


def show_new_job_window():
    """
    Creates a pop-up window for the Receptionist to assign a new job.
    """
    job_window = ctk.CTkToplevel(app)
    job_window.title("Create New Repair Job")
    job_window.geometry("450x500") 
    job_window.transient(app)
    job_window.grab_set()

    frame = ctk.CTkFrame(master=job_window)
    frame.pack(pady=20, padx=20, fill='both', expand=True)
    
    label = ctk.CTkLabel(master=frame, text="New Repair Job", font=("Arial", 16))
    label.pack(pady=12, padx=10)

    customer_label = ctk.CTkLabel(master=frame, text="Select Customer:")
    customer_label.pack(pady=(10, 0))
    
    customer_list = get_all_customers() 
    if not customer_list:
        customer_list = ["No customers found"]
        
    customer_combobox = ctk.CTkComboBox(master=frame, values=customer_list, width=250)
    customer_combobox.set(customer_list[0])
    customer_combobox.pack(pady=5, padx=10)

    service_label = ctk.CTkLabel(master=frame, text="Select Service:")
    service_label.pack(pady=(10, 0))
    service_display_list = [f"{key} {desc}" for key, desc in SERVICES.items()]
    service_combobox = ctk.CTkComboBox(master=frame, values=service_display_list, width=350)
    service_combobox.set(service_display_list[0]) 
    service_combobox.pack(pady=5, padx=10)

    urgency_label = ctk.CTkLabel(master=frame, text="Select Urgency:")
    urgency_label.pack(pady=(10, 0))
    urgency_var = ctk.StringVar(value="Normal")  
    urgency_frame = ctk.CTkFrame(master=frame, fg_color="transparent")
    urgency_frame.pack(fill="x", padx=40, pady=5)
    normal_radio = ctk.CTkRadioButton(master=urgency_frame, text="Normal", variable=urgency_var, value="Normal")
    normal_radio.pack(side="left", expand=True, padx=10)
    urgent_radio = ctk.CTkRadioButton(master=urgency_frame, text="Urgent", variable=urgency_var, value="Urgent")
    urgent_radio.pack(side="right", expand=True, padx=10)

    price_label = ctk.CTkLabel(master=frame, text="Price: RM 0.00", font=("Arial", 14, "bold"))
    price_label.pack(pady=(20, 10))

    def update_price_display(*args):
        """Inner function to update the price label."""
        selected_service_str = service_combobox.get()
        if not selected_service_str:
            return
        
        service_key = selected_service_str.split(" ")[0] 
        urgency = urgency_var.get()
        
        price = "N/A"
        if urgency == "Normal":
            price = normal.get(service_key, "N/A")
        elif urgency == "Urgent":
            price = urgent.get(service_key, "N/A")
        
        price_label.configure(text=f"Price: RM {price}")

    normal_radio.configure(command=update_price_display)
    urgent_radio.configure(command=update_price_display)
    service_combobox.configure(command=update_price_display)
    
    update_price_display()

    def on_create_job_click():
        customer = customer_combobox.get()
        selected_service_str = service_combobox.get()
        urgency = urgency_var.get()

        if not customer or customer == "No customers found":
            show_error_message("Validation Error", "Please register a customer first.")
            return
        if not selected_service_str or not urgency:
            show_error_message("Validation Error", "Please select a service and urgency.")
            return

        # Get service key from "1. Remove virus..."
        service_key = selected_service_str.split(" ")[0] 
        
        if create_job_in_file(customer, service_key, urgency):
            show_info_message("Success", f"New job created successfully for {customer}.")
            job_window.destroy()

    submit_button = ctk.CTkButton(master=frame, text="Create Job", command=on_create_job_click)
    submit_button.pack(pady=20, padx=10)


def show_view_all_jobs_window():
    """
    Creates a pop-up window for the Technician to view all service requests.
    """
    view_window = ctk.CTkToplevel(app)
    view_window.title("All Service Requests")
    view_window.geometry("1100x700")
    view_window.transient(app)
    view_window.grab_set()
    
    def refresh_jobs_list():
        for widget in scroll_frame.winfo_children():
            widget.destroy()
            
        jobs = get_all_jobs()

        if not jobs:
            no_jobs_label = ctk.CTkLabel(master=scroll_frame, text="No jobs found.", font=("Arial", 14))
            no_jobs_label.pack(pady=20, padx=10)
            return

        for job in jobs:
            job_frame = ctk.CTkFrame(master=scroll_frame, border_width=2)
            job_frame.pack(fill='x', expand=True, padx=10, pady=10)
            
            service_desc = SERVICES.get(job['service_id'], "Unknown Service")
        
            left_frame = ctk.CTkFrame(master=job_frame, fg_color="transparent")
            left_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)
            right_frame = ctk.CTkFrame(master=job_frame, fg_color="transparent")
            right_frame.pack(side="right", fill="x", expand=True, padx=15, pady=10)

            id_label = ctk.CTkLabel(master=left_frame, text=f"Job ID: {job['job_id']}", font=("Arial", 16, "bold"))
            id_label.pack(anchor="w")
            customer_label = ctk.CTkLabel(master=left_frame, text=f"Customer: {job['customer_username']}")
            customer_label.pack(anchor="w", pady=2)
            service_label = ctk.CTkLabel(master=left_frame, text=f"Service: ({job['service_id']}) {service_desc}")
            service_label.pack(anchor="w", pady=2)
            notes_label = ctk.CTkLabel(master=left_frame, text=f"Tech Notes: {job['technician_notes']}")
            notes_label.pack(anchor="w", pady=2)

            status_label = ctk.CTkLabel(master=right_frame, text=f"Status: {job['status']}", font=("Arial", 14, "bold"))
            status_label.pack(anchor="w")
            price_label = ctk.CTkLabel(master=right_frame, text=f"Price: RM {job['price']}")
            price_label.pack(anchor="w", pady=2)
            urgency_label = ctk.CTkLabel(master=right_frame, text=f"Urgency: {job['urgency']}")
            urgency_label.pack(anchor="w", pady=2)
            date_req_label = ctk.CTkLabel(master=right_frame, text=f"Requested: {job['date_requested']}")
            date_req_label.pack(anchor="w", pady=2)
            date_comp_label = ctk.CTkLabel(master=right_frame, text=f"Completed: {job['date_completed']}")
            date_comp_label.pack(anchor="w", pady=2)
            
            if job['status'] != 'Completed' and job['status'] != 'Paid':
                update_button = ctk.CTkButton(
                    master=job_frame, 
                    text="Complete Job", 
                    fg_color="green",
                    hover_color="dark green",
                    command=lambda current_job=job: show_update_job_window(current_job, refresh_jobs_list)
                )
                update_button.pack(side="bottom", fill="x", padx=15, pady=10)

    title_label = ctk.CTkLabel(master=view_window, text="All Repair Jobs", font=("Arial", 18, "bold"))
    title_label.pack(pady=10)
    scroll_frame = ctk.CTkScrollableFrame(master=view_window)
    scroll_frame.pack(pady=10, padx=20, fill='both', expand=True)

    refresh_jobs_list()


def show_update_job_window(job_to_update, refresh_callback):
    """
    Pop-up for Technician to add notes and complete a job.
    'job_to_update' is the job dictionary.
    'refresh_callback' is the function to reload the jobs list.
    """
    update_window = ctk.CTkToplevel(app)
    update_window.title(f"Complete Job ID: {job_to_update['job_id']}")
    update_window.geometry("450x400") 
    update_window.transient(app)
    update_window.grab_set()
    
    frame = ctk.CTkFrame(master=update_window)
    frame.pack(pady=20, padx=20, fill='both', expand=True)
    title_label = ctk.CTkLabel(master=frame, text=f"Complete Job: {job_to_update['job_id']}", font=("Arial", 16, "bold"))
    title_label.pack(pady=10)
    customer_label = ctk.CTkLabel(master=frame, text=f"Customer: {job_to_update['customer_username']}")
    customer_label.pack(pady=2)
    notes_label = ctk.CTkLabel(master=frame, text="Add Technician Notes:")
    notes_label.pack(pady=(10, 5))
    notes_textbox = ctk.CTkTextbox(master=frame, height=150, width=400)
    if job_to_update['technician_notes'] != "N/A":
        notes_textbox.insert("1.0", job_to_update['technician_notes'])
    notes_textbox.pack(pady=5, padx=10)

    def on_submit_completion():
        """
        Gathers notes, calls backend, and refreshes the list.
        """
        new_notes = notes_textbox.get("1.0", "end-1c") # Get all text
        
        if not new_notes:
            show_error_message("Missing Notes", "Please add technician notes to complete the job.")
            return

        if update_job_in_file(job_to_update['job_id'], new_notes):
            show_info_message("Success", "Job has been updated successfully.")
            refresh_callback() 
            update_window.destroy() # Close this pop-up

    submit_button = ctk.CTkButton(master=frame, text="Submit & Complete Job", command=on_submit_completion)
    submit_button.pack(pady=20, padx=10)


def show_customer_jobs_window(customer_username):
    """
    Creates a pop-up window for the Customer to view THEIR service requests.
    (This is the "View Details" button)
    """
    view_window = ctk.CTkToplevel(app)
    view_window.title(f"My Service Requests ({customer_username})")
    view_window.geometry("1100x700") 
    view_window.transient(app)
    view_window.grab_set()

    title_label = ctk.CTkLabel(master=view_window, text="My Repair Jobs", font=("Arial", 18, "bold"))
    title_label.pack(pady=10)

    scroll_frame = ctk.CTkScrollableFrame(master=view_window)
    scroll_frame.pack(pady=10, padx=20, fill='both', expand=True)

    jobs = get_jobs_for_customer(customer_username)

    if not jobs:
        no_jobs_label = ctk.CTkLabel(master=scroll_frame, text="You have not requested any services.", font=("Arial", 14))
        no_jobs_label.pack(pady=20, padx=10)
        return

    for job in jobs:
        job_frame = ctk.CTkFrame(master=scroll_frame, border_width=2)
        job_frame.pack(fill='x', expand=True, padx=10, pady=10)
        service_desc = SERVICES.get(job['service_id'], "Unknown Service")
        left_frame = ctk.CTkFrame(master=job_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)
        right_frame = ctk.CTkFrame(master=job_frame, fg_color="transparent")
        right_frame.pack(side="right", fill="x", expand=True, padx=15, pady=10)
        id_label = ctk.CTkLabel(master=left_frame, text=f"Job ID: {job['job_id']}", font=("Arial", 16, "bold"))
        id_label.pack(anchor="w")
        service_label = ctk.CTkLabel(master=left_frame, text=f"Service: ({job['service_id']}) {service_desc}")
        service_label.pack(anchor="w", pady=2)
        notes_label = ctk.CTkLabel(master=left_frame, text=f"Technician Notes: {job['technician_notes']}")
        notes_label.pack(anchor="w", pady=2)
        status_label = ctk.CTkLabel(master=right_frame, text=f"Status: {job['status']}", font=("Arial", 14, "bold"))
        status_label.pack(anchor="w")
        price_label = ctk.CTkLabel(master=right_frame, text=f"Total Amount: RM {job['price']}")
        price_label.pack(anchor="w", pady=2)
        urgency_label = ctk.CTkLabel(master=right_frame, text=f"Urgency: {job['urgency']}")
        urgency_label.pack(anchor="w", pady=2)
        date_req_label = ctk.CTkLabel(master=right_frame, text=f"Requested: {job['date_requested']}")
        date_req_label.pack(anchor="w", pady=2)
        date_comp_label = ctk.CTkLabel(master=right_frame, text=f"Collection Date: {job['date_completed']}")
        date_comp_label.pack(anchor="w", pady=2)

def show_change_service_list_window(customer_username):
    """
    Creates a pop-up for the Customer to see their jobs and change PENDING ones.
    (This is for the "Change Requested Service" button)
    """
    change_list_window = ctk.CTkToplevel(app)
    change_list_window.title(f"Change My Service ({customer_username})")
    change_list_window.geometry("1100x700") 
    change_list_window.transient(app)
    change_list_window.grab_set()

    title_label = ctk.CTkLabel(master=change_list_window, text="Change My Repair Service", font=("Arial", 18, "bold"))
    title_label.pack(pady=10)

    scroll_frame = ctk.CTkScrollableFrame(master=change_list_window)
    scroll_frame.pack(pady=10, padx=20, fill='both', expand=True)

    def refresh_job_list():
        """Inner function to reload all job cards."""
        for widget in scroll_frame.winfo_children():
            widget.destroy()

        jobs = get_jobs_for_customer(customer_username)

        if not jobs:
            ctk.CTkLabel(master=scroll_frame, text="You have no services to change.", font=("Arial", 14)).pack(pady=20)
            return

        jobs_found = False
        for job in jobs:
            jobs_found = True
            job_frame = ctk.CTkFrame(master=scroll_frame, border_width=2)
            job_frame.pack(fill='x', expand=True, padx=10, pady=10)
            
            service_desc = SERVICES.get(job['service_id'], "Unknown Service")
            
            info_frame = ctk.CTkFrame(master=job_frame, fg_color="transparent")
            info_frame.pack(fill="x", expand=True, padx=15, pady=10)

            id_label = ctk.CTkLabel(master=info_frame, text=f"Job ID: {job['job_id']}", font=("Arial", 16, "bold"))
            id_label.pack(anchor="w")
            
            service_label = ctk.CTkLabel(master=info_frame, text=f"Service: {service_desc}")
            service_label.pack(anchor="w", pady=2)

            status_label = ctk.CTkLabel(master=info_frame, text=f"Status: {job['status']}", font=("Arial", 14, "bold"))
            status_label.pack(anchor="w", pady=2)
            
            price_label = ctk.CTkLabel(master=info_frame, text=f"Price: RM {job['price']}")
            price_label.pack(anchor="w", pady=2)
            
            if job['status'] == 'Pending':
                change_button = ctk.CTkButton(
                    master=job_frame, 
                    text="Change This Service",
                    command=lambda current_job=job: show_perform_service_change_window(current_job, refresh_job_list)
                )
                change_button.pack(side="bottom", fill="x", padx=15, pady=10)
        
        if not jobs_found:
            ctk.CTkLabel(master=scroll_frame, text="You have no services to change.", font=("Arial", 14)).pack(pady=20)

    refresh_job_list()

def show_perform_service_change_window(job_to_change, refresh_callback):
    """
    The SECOND pop-up, where the customer actually makes the change.
    """
    change_window = ctk.CTkToplevel(app)
    change_window.title(f"Changing Job ID: {job_to_change['job_id']}")
    change_window.geometry("450x500")
    change_window.transient(app)
    change_window.grab_set() 

    frame = ctk.CTkFrame(master=change_window)
    frame.pack(pady=20, padx=20, fill='both', expand=True)
    
    label = ctk.CTkLabel(master=frame, text="Select New Service", font=("Arial", 16))
    label.pack(pady=12, padx=10)

    service_label = ctk.CTkLabel(master=frame, text="Select New Service:")
    service_label.pack(pady=(10, 0))
    service_display_list = [f"{key} {desc}" for key, desc in SERVICES.items()]
    service_combobox = ctk.CTkComboBox(master=frame, values=service_display_list, width=350)
    service_combobox.set(f"{job_to_change['service_id']} {SERVICES.get(job_to_change['service_id'])}") 
    service_combobox.pack(pady=5, padx=10)

    urgency_label = ctk.CTkLabel(master=frame, text="Select New Urgency:")
    urgency_label.pack(pady=(10, 0))
    urgency_var = ctk.StringVar(value=job_to_change['urgency'])
    urgency_frame = ctk.CTkFrame(master=frame, fg_color="transparent")
    urgency_frame.pack(fill="x", padx=40, pady=5)
    normal_radio = ctk.CTkRadioButton(master=urgency_frame, text="Normal", variable=urgency_var, value="Normal")
    normal_radio.pack(side="left", expand=True, padx=10)
    urgent_radio = ctk.CTkRadioButton(master=urgency_frame, text="Urgent", variable=urgency_var, value="Urgent")
    urgent_radio.pack(side="right", expand=True, padx=10)

    price_label = ctk.CTkLabel(master=frame, text="Price: RM 0.00", font=("Arial", 14, "bold"))
    price_label.pack(pady=(20, 10))

    def update_price_display(*args):
        selected_service_str = service_combobox.get()
        if not selected_service_str: return
        
        service_key = selected_service_str.split(" ")[0] 
        urgency = urgency_var.get()
        
        price = "N/A"
        if urgency == "Normal":
            price = normal.get(service_key, "N/A")
        elif urgency == "Urgent":
            price = urgent.get(service_key, "N/A")
        
        price_label.configure(text=f"New Price: RM {price}")

    normal_radio.configure(command=update_price_display)
    urgent_radio.configure(command=update_price_display)
    service_combobox.configure(command=update_price_display)
    update_price_display() 

    def on_confirm_change_click():
        selected_service_str = service_combobox.get()
        new_urgency = urgency_var.get()
        new_service_key = selected_service_str.split(" ")[0] 
        
        if update_customer_service(job_to_change['job_id'], new_service_key, new_urgency):
            show_info_message("Success", f"Job {job_to_change['job_id']} has been updated.")
            refresh_callback() 
            change_window.destroy() 

    submit_button = ctk.CTkButton(master=frame, text="Confirm Change", command=on_confirm_change_click)
    submit_button.pack(pady=20, padx=10)


#  Main Dashboard Functions 
def show_dashboard(user_role, user_name):
    """
    Destroys the login frame and shows the appropriate dashboard
    based on the user's role.
    """
    login_frame.pack_forget()
    
    app.geometry("1280x720")
    app.title(f"{user_role} Dashboard - Abu Laptop Repair Service Management System")
    
    global CURRENT_USER
    CURRENT_USER = {"role": user_role, "name": user_name, "username": user_entry.get()}

    dashboard_frame.pack(pady=20, padx=40, fill='both', expand=True)

    global global_welcome_label
    global_welcome_label = ctk.CTkLabel(master=dashboard_frame, text=f"Welcome, {user_name}!", font=("Arial", 24, "bold"))
    global_welcome_label.pack(pady=10, padx=10)
    role_label = ctk.CTkLabel(master=dashboard_frame, text=f"Role: {user_role}", font=("Arial", 14))
    role_label.pack(pady=0, padx=10)

    button_frame = ctk.CTkFrame(master=dashboard_frame, fg_color="transparent")
    button_frame.pack(pady=20, padx=20, fill="y", expand=True)

    if user_role == 'Admin':
        admin_interface(button_frame)
    elif user_role == 'Receptionist':
        receptionist_interface(button_frame)
    elif user_role == 'Technician':
        technician_interface(button_frame)
    elif user_role == 'Customer':
        customer_interface(button_frame)
    else:
        show_error_message("Role Error", "Unknown user role. Logging out.")
        logout() 

    logout_button = ctk.CTkButton(master=dashboard_frame, text='Logout', command=logout,
                                  fg_color="red", hover_color="dark red")  
    logout_button.pack(pady=20, padx=10, side="bottom")

def admin_interface(admin_frame):  
    register_technician_button = ctk.CTkButton(master=admin_frame,text='Register New Technician',
                                               command=lambda: show_register_user_window("Technician"))  
    register_technician_button.pack(pady=12,padx=10)
    
    register_receptionist_button = ctk.CTkButton(master=admin_frame,text='Register New Receptionist',
                                                 command=lambda: show_register_user_window("Receptionist"))  
    register_receptionist_button.pack(pady=12,padx=10)
    
    view_report_button = ctk.CTkButton(master=admin_frame,text='View Report', command=show_monthly_report_window) 
    view_report_button.pack(pady=12,padx=10)

    view_income_button = ctk.CTkButton(master=admin_frame,text='View Income', command=show_total_income_window) 
    view_income_button.pack(pady=12,padx=10)

    update_pass_button = ctk.CTkButton(master=admin_frame,text='Update Own Profile', command=show_update_profile_window)  
    update_pass_button.pack(pady=12,padx=10)
    
def receptionist_interface(receptionist_frame):  
    register_customer_button = ctk.CTkButton(master=receptionist_frame,text='Register New Customer',
                                             command=lambda: show_register_user_window("Customer"))
    register_customer_button.pack(pady=12,padx=10)
    
    assign_service_button = ctk.CTkButton(master=receptionist_frame,text='Assign Service to Customer', 
                                          command=show_new_job_window)
    assign_service_button.pack(pady=12,padx=10)
    
    payment_button = ctk.CTkButton(master=receptionist_frame,text='Accept Payment & Generate Receipt',
                                   command=show_payment_list_window) 
    payment_button.pack(pady=12,padx=10)

    update_pass_button = ctk.CTkButton(master=receptionist_frame,text='Update Own Profile', command=show_update_profile_window)  
    update_pass_button.pack(pady=12,padx=10)

def technician_interface(technician_frame):  
    view_service_button = ctk.CTkButton(master=technician_frame,text='View Service Requested', 
                                        command=show_view_all_jobs_window) 
    view_service_button.pack(pady=12,padx=10)
    
    update_pass_button = ctk.CTkButton(master=technician_frame,text='Update Own Profile', command=show_update_profile_window)  
    update_pass_button.pack(pady=12,padx=10)

def customer_interface(customer_frame):  
    change_service_button = ctk.CTkButton(master=customer_frame,text='Change Requested Service',
                                          command=lambda: show_change_service_list_window(CURRENT_USER['username'])) 
    change_service_button.pack(pady=12,padx=10)
    
    view_details_button = ctk.CTkButton(master=customer_frame,text='View Service Details & Total Amount',
                                        command=lambda: show_customer_jobs_window(CURRENT_USER['username']))
    view_details_button.pack(pady=12,padx=10)

    update_pass_button = ctk.CTkButton(master=customer_frame,text='Update Own Profile', command=show_update_profile_window)  
    update_pass_button.pack(pady=12,padx=10)

#  5. MAIN LOGIN LOGIC & APP STARTUP 
def login_process():
    """
    Handles the login process, including attempt tracking.
    This function is called by the login button.
    """
    global LOGIN_ATTEMPTS
    
    username = user_entry.get()
    password = pass_entry.get()

    if not username or not password:
        show_error_message('Login Error', 'Please enter both username and password.')
        return

    user_role, user_name = authenticate_user(username, password)

    if user_role and user_name:
        show_info_message('Login Success', f'Welcome, {user_name}!')
        
        LOGIN_ATTEMPTS = 0
        show_dashboard(user_role, user_name)
    else:
        LOGIN_ATTEMPTS += 1
        remaining_attempts = 3 - LOGIN_ATTEMPTS
        
        if remaining_attempts > 0:
            show_error_message('Login Failed', f'Invalid username or password.\nYou have {remaining_attempts} attempts left.')
        else:
            show_error_message('Login Locked', 'You have exceeded the maximum login attempts. The application will now close.')
            app.quit() 

# --- Main Application Setup ---
if __name__ == "__main__":
    
    check_files()
    
    CURRENT_USER = {}
    global_welcome_label = None
    
    global login_frame, dashboard_frame
    global user_entry, pass_entry 
    
    login_frame = ctk.CTkFrame(master=app, fg_color=app.cget("bg"))  
    login_frame.pack(fill='both', expand=True)  
    inner_login_frame = ctk.CTkFrame(master=login_frame, width=400, corner_radius=10) 
    inner_login_frame.place(relx=0.5, rely=0.5, anchor="center") 
    
    label = ctk.CTkLabel(master=inner_login_frame, text='Abu Laptop Repair Service', font=("Arial", 28, "bold"))  
    label.pack(pady=(40, 20), padx=50) 
    label_sub = ctk.CTkLabel(master=inner_login_frame, text='Management System Login', font=("Arial", 16))
    label_sub.pack(pady=(0, 30), padx=50) 

    user_entry = ctk.CTkEntry(master=inner_login_frame, placeholder_text="Username", width=300, height=40, font=("Arial", 14))  
    user_entry.pack(pady=12, padx=50)  
    
    pass_entry = ctk.CTkEntry(master=inner_login_frame, placeholder_text="Password", show="*", width=300, height=40, font=("Arial", 14))  
    pass_entry.pack(pady=12, padx=50)  
    
    login_button = ctk.CTkButton(master=inner_login_frame, text='Login', command=login_process, width=300, height=40, font=("Arial", 14, "bold"))  
    login_button.pack(pady=(20, 40), padx=50) 
    
    dashboard_frame = ctk.CTkFrame(master=app)
    
    app.mainloop()