import customtkinter as ctk  
import tkinter.messagebox as tkmb  
from tkinter import ttk, filedialog 
from datetime import datetime
import backend  

# App
class RepairApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        app_width = int(screen_width * 0.6)  
        app_height = int(screen_height * 0.6)

        x_pos = int((screen_width / 2) - (app_width / 2))
        y_pos = int((screen_height / 2) - (app_height / 2))

        self.geometry(f"{app_width}x{app_height}+{x_pos}+{y_pos}")
        self.title("Abu Laptop Repair Service Management System")

        ctk.set_appearance_mode("dark")  
        ctk.set_default_color_theme("blue")
        
        self.current_user = {} 
        self.current_toast = None 
        self.setup_styles()
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        self.check_backend()
        self.show_view(LoginView)

    def setup_styles(self):
        """Configures standard tkinter widgets to match custom theme."""
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", 
                        fieldbackground="#2b2b2b", rowheight=30, font=("Arial", 12))
        style.configure("Treeview.Heading", background="#1f538d", foreground="white", 
                        font=("Arial", 12, "bold"), relief="flat")
        style.map("Treeview", background=[('selected', '#106A43')])

    def check_backend(self):
        backend.check_files()

    def show_view(self, view_class, *args, **kwargs):
        """
        The Scene Manager. Destroys current view and loads the new one.
        """
        for widget in self.container.winfo_children():
            widget.destroy()
            
        view = view_class(self.container, self, *args, **kwargs)
        view.pack(fill="both", expand=True)

    def show_toast(self, message, is_error=False):
        """
        Displays a floating 'Toast' notification at the bottom center.
        Replaces modal success popups to reduce click fatigue.
        """
        if self.current_toast:
            try: self.current_toast.destroy()
            except: pass

        color = "#C0392B" if is_error else "#27AE60"
        
        self.current_toast = ctk.CTkFrame(self, fg_color=color, corner_radius=20)
        self.current_toast.place(relx=0.5, rely=0.92, anchor="center")
        
        label = ctk.CTkLabel(self.current_toast, text=message, text_color="white", 
                             font=("Arial", 14, "bold"), padx=20, pady=10)
        label.pack()
        
        self.after(3000, self._destroy_toast)

    def _destroy_toast(self):
        if self.current_toast:
            self.current_toast.destroy()
            self.current_toast = None

    def show_error(self, title, msg):
        """Errors are critical, so we keep them as blocking Popups."""
        tkmb.showerror(title, msg)
        
    def show_info(self, title, msg):
        """Legacy method: redirects to toast."""
        self.show_toast(msg)

class BaseView(ctk.CTkFrame):
    """Parent class for all screens to share common logic."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

    def add_back_button(self):
        btn = ctk.CTkButton(self, text="← Back to Dashboard", width=150, fg_color="gray",
                            command=lambda: self.controller.show_view(DashboardView))
        btn.pack(anchor="w", padx=20, pady=(20, 0))

# Classes
class LoginView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.login_attempts = 0
        
        center_box = ctk.CTkFrame(self, width=500, height=400, corner_radius=15)
        center_box.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(center_box, text="ABU REPAIR SERVICE", font=("Arial", 28, "bold")).pack(pady=(50, 10), padx=40)
        ctk.CTkLabel(center_box, text="Management System", font=("Arial", 16)).pack(pady=(0, 30))

        self.user_entry = ctk.CTkEntry(center_box, placeholder_text="Username", width=300, height=45, font=("Arial", 14))
        self.user_entry.pack(pady=10)
        
        self.pass_entry = ctk.CTkEntry(center_box, placeholder_text="Password", show="*", width=300, height=45, font=("Arial", 14))
        self.pass_entry.pack(pady=10)

        ctk.CTkButton(center_box, text="Login", width=300, height=45, font=("Arial", 15, "bold"), 
                      command=self.attempt_login).pack(pady=30)

    def attempt_login(self):
        u = self.user_entry.get()
        p = self.pass_entry.get()
        role, name = backend.authenticate_user(u, p)
        
        if role:
            self.controller.current_user = {'username': u, 'role': role, 'name': name}
            self.controller.show_view(DashboardView)
        else:
            self.login_attempts += 1
            remaining = 3 - self.login_attempts
            
            if remaining <= 0:
                self.controller.show_error("Login Failed", "Max attempts reached. Exiting.")
                self.controller.destroy() # Close the app
            else:
                self.controller.show_error("Login Failed", f"Invalid Credentials. {remaining} attempts remaining.")

class DashboardView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        user = self.controller.current_user
        role = user['role']
        name = user['name']

        dash = ctk.CTkFrame(self, fg_color="transparent")
        dash.pack(fill='both', expand=True, padx=40, pady=40)
        
        header = ctk.CTkFrame(dash, height=100)
        header.pack(fill='x', pady=(0, 30))
        
        ctk.CTkLabel(header, text=f"Welcome, {name}", font=("Arial", 32, "bold")).pack(side="left", padx=30, pady=20)
        ctk.CTkLabel(header, text=f"Role: {role}", font=("Arial", 16), text_color="gray").pack(side="left", pady=20)
        
        ctk.CTkButton(header, text="Logout", fg_color="#C0392B", hover_color="#922B21", width=100, 
                      command=lambda: self.controller.show_view(LoginView)).pack(side="right", padx=30)

        content = ctk.CTkFrame(dash, fg_color="transparent")
        content.pack(fill='both', expand=True)

        menu_col = ctk.CTkFrame(content, width=400)
        menu_col.pack(side="left", fill="y", padx=(0, 20))
        ctk.CTkLabel(menu_col, text="MAIN MENU", font=("Arial", 14, "bold"), text_color="gray").pack(pady=20)

        if role == "Admin":
            self.add_menu_btn(menu_col, "Register Technician", lambda: controller.show_view(RegisterView, "Technician"))
            self.add_menu_btn(menu_col, "Register Receptionist", lambda: controller.show_view(RegisterView, "Receptionist"))
            self.add_menu_btn(menu_col, "View Monthly Report", lambda: controller.show_view(MonthlyReportView))
        
        elif role == "Receptionist":
            self.add_menu_btn(menu_col, "Register Customer", lambda: controller.show_view(RegisterView, "Customer"))
            self.add_menu_btn(menu_col, "New Job Ticket", lambda: controller.show_view(NewJobView))
            self.add_menu_btn(menu_col, "Process Payments", lambda: controller.show_view(PaymentListView))

        elif role == "Technician":
             self.add_menu_btn(menu_col, "View Job Board", lambda: controller.show_view(TechBoardView))

        elif role == "Customer":
            self.add_menu_btn(menu_col, "My Repairs", lambda: controller.show_view(CustomerRepairsView))

        ctk.CTkButton(menu_col, text="Update Profile", fg_color="transparent", border_width=2, 
                      text_color=("gray10", "gray90"), 
                      command=lambda: controller.show_view(UpdateProfileView)).pack(side="bottom", fill="x", padx=20, pady=20)

        self.setup_stats(content)

    def add_menu_btn(self, parent, text, command):
        ctk.CTkButton(parent, text=text, command=command, height=60, font=("Arial", 18)).pack(fill="x", padx=20, pady=10)

    def setup_stats(self, parent):
        info_col = ctk.CTkFrame(parent, fg_color="gray20")
        info_col.pack(side="right", fill="both", expand=True)
        
        role = self.controller.current_user['role']
        username = self.controller.current_user['username']
        
        stat1_val = "0"
        stat1_lbl = "Label 1"
        stat1_color = "orange"
        
        stat2_val = "0"
        stat2_lbl = "Label 2"
        stat2_color = "green"

        all_jobs = backend.get_all_jobs()

        if role == "Customer":
            my_jobs = backend.get_jobs_for_customer(username)
            stat1_val = len([j for j in my_jobs if j['status'] == "Pending"])
            stat1_lbl = "My Pending"
            stat2_val = len([j for j in my_jobs if j['status'] == "Completed"])
            stat2_lbl = "Ready for Pickup"

        elif role == "Technician":
            pending_count = len([j for j in all_jobs if j['status'] == "Pending"])
            urgent_count = len([j for j in all_jobs if j['status'] == "Pending" and j['urgency'] == "Urgent"])
            
            stat1_val = pending_count
            stat1_lbl = "Job Queue"
            
            stat2_val = urgent_count
            stat2_lbl = "Urgent & Pending"
            stat2_color = "#C0392B" 

        elif role == "Admin":
            revenue = backend.calculate_total_income()
            total_jobs = len(all_jobs)
            
            stat1_val = f"RM {revenue:.2f}" 
            stat1_lbl = "Total Revenue"
            
            stat2_val = total_jobs
            stat2_lbl = "Total Tickets"

        else: 
            stat1_val = len([j for j in all_jobs if j['status'] == "Pending"])
            stat1_lbl = "Total Pending"
            stat2_val = len([j for j in all_jobs if j['status'] == "Completed"])
            stat2_lbl = "Ready for Pickup"

        stats_box = ctk.CTkFrame(info_col, fg_color="transparent")
        stats_box.pack(pady=40)
        
        ctk.CTkLabel(stats_box, text=str(stat1_val), font=("Arial", 50, "bold"), text_color=stat1_color).pack()
        ctk.CTkLabel(stats_box, text=stat1_lbl, font=("Arial", 14)).pack(pady=(0, 20))
        ctk.CTkLabel(stats_box, text=str(stat2_val), font=("Arial", 50, "bold"), text_color=stat2_color).pack()
        ctk.CTkLabel(stats_box, text=stat2_lbl, font=("Arial", 14)).pack()

class RegisterView(BaseView):
    def __init__(self, parent, controller, role_to_register):
        super().__init__(parent, controller)
        self.add_back_button()
        self.role = role_to_register

        center = ctk.CTkFrame(self)
        center.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(center, text=f"Register New {self.role}", font=("Arial", 22, "bold")).pack(pady=20, padx=50)
        
        self.entries = {}
        for field in ["Full Name", "Phone", "Username", "Password"]:
            ctk.CTkLabel(center, text=field).pack(anchor="w", padx=30)
            entry = ctk.CTkEntry(center, width=300)
            entry.pack(pady=(0, 10), padx=30)
            if field == "Password": entry.configure(show="*")
            self.entries[field] = entry
            
        ctk.CTkButton(center, text="Complete Registration", command=self.submit, width=300, height=40).pack(pady=20, padx=30)

    def submit(self):
        args = [self.entries["Username"].get(), self.entries["Password"].get(), 
                self.entries["Full Name"].get(), self.entries["Phone"].get(), self.role]
        
        if not all(args):
            self.controller.show_error("Error", "All fields required")
            return

        success, msg = backend.register_user(*args)
        if success:
            self.controller.show_view(DashboardView)
            self.controller.show_toast(f"Success! {self.role} registered.")
        else:
            self.controller.show_error("Registration Failed", msg)

class PaymentListView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.add_back_button()
        
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=50, pady=10)

        ctk.CTkLabel(header_frame, text="Process Payments", font=("Arial", 24, "bold")).pack(side="left")
        
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(header_frame, width=300, placeholder_text="🔍 Search Customer Name...", 
                                         textvariable=self.search_var)
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", self.filter_table)
        
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=50, pady=(10, 20))

        columns = ("ID", "Customer", "Service", "Price", "Status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        headers = ["Job ID", "Customer", "Service Type", "Amount (RM)", "Status"]
        widths = [50, 150, 300, 100, 100]
        for col, h, w in zip(columns, headers, widths):
            self.tree.heading(col, text=h)
            self.tree.column(col, width=w, anchor="center" if col != "Customer" and col != "Service" else "w")

        scrollbar = ctk.CTkScrollbar(table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        self.all_jobs = backend.get_all_jobs()
        self.populate_table(self.all_jobs)

        self.pay_btn = ctk.CTkButton(self, text="Select a Job", fg_color="gray", state="disabled",
                                     height=50, font=("Arial", 16, "bold"), command=self.process_action)
        self.pay_btn.pack(pady=20)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def filter_table(self, event=None):
        query = self.search_var.get().lower()
        if not query:
            self.populate_table(self.all_jobs)
        else:
            filtered_data = [job for job in self.all_jobs if query in job['customer_username'].lower()]
            self.populate_table(filtered_data)

    def populate_table(self, jobs_list):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for job in jobs_list:
            s_name = backend.SERVICES.get(job['service_id'], "Unknown")
            self.tree.insert("", "end", values=(job['job_id'], job['customer_username'], s_name, job['price'], job['status']))

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected: 
            self.pay_btn.configure(state="disabled", fg_color="gray", text="Select a Job")
            return
        status = self.tree.item(selected)['values'][4]
        
        if status == 'Completed':
            self.pay_btn.configure(state="normal", fg_color="green", text="Process Payment")
        elif status == 'Paid':
            self.pay_btn.configure(state="disabled", fg_color="gray", text="Already Paid")
        else:
            self.pay_btn.configure(state="disabled", fg_color="gray", text="Job Not Finished")

    def process_action(self):
        selected = self.tree.selection()
        if not selected: return
        job_id = str(self.tree.item(selected)['values'][0])
        job_dict = next((j for j in self.all_jobs if str(j['job_id']) == job_id), None)
        self.controller.show_view(ReceiptView, job_data=job_dict)

class ReceiptView(BaseView):
    def __init__(self, parent, controller, job_data):
        super().__init__(parent, controller)
        self.add_back_button()
        self.job = job_data

        success, msg = backend.process_payment(self.job['job_id'])
        if not success and "already paid" not in msg.lower():
            self.controller.show_error("Error", msg)
        
        content = ctk.CTkFrame(self, width=500, fg_color="transparent")
        content.pack(pady=20, expand=True)

        ctk.CTkLabel(content, text="PAYMENT SUCCESSFUL", font=("Arial", 30, "bold"), text_color="#2CC985").pack(pady=10)
        
        c_data = backend.get_user_details(self.job['customer_username'])
        c_name = c_data.get('name', 'N/A') if c_data else 'N/A'
        s_name = backend.SERVICES.get(self.job['service_id'], 'N/A')
        
        self.receipt_text = (
            "========================================\n"
            "       ABU LAPTOP REPAIR SERVICE        \n"
            "========================================\n"
            f"DATE: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"JOB ID: {self.job['job_id']}\n"
            "----------------------------------------\n"
            f"CUSTOMER: {c_name}\n"
            f"SERVICE:  {s_name}\n"
            f"URGENCY:  {self.job['urgency']}\n"
            f"NOTES:    {self.job['technician_notes']}\n"
            "----------------------------------------\n"
            f"TOTAL PAID: RM {self.job['price']}\n"
            "========================================\n"
        )

        box = ctk.CTkTextbox(content, font=("Courier New", 14), width=500, height=400)
        box.pack(pady=20)
        box.insert("1.0", self.receipt_text)
        box.configure(state="disabled")

        ctk.CTkButton(content, text="💾 Save Receipt", fg_color="#2980B9", command=self.save_file).pack(pady=10)

    def save_file(self):
        fname = f"Receipt_Job_{self.job['job_id']}.txt"
        try:
            with open(fname, "w") as f: f.write(self.receipt_text)
            self.controller.show_toast(f"Receipt Saved: {fname}") # UX FIX: Toast instead of popup
        except Exception as e:
            self.controller.show_error("Error", str(e))

class TechBoardView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.add_back_button()
        
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=50, pady=10)
        ctk.CTkLabel(header_frame, text="Technician Job Board", font=("Arial", 24, "bold")).pack(side="left")
        
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(header_frame, width=300, placeholder_text="🔍 Search Customer Name...", 
                                         textvariable=self.search_var)
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", self.filter_table)
        
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=50, pady=(10, 20))

        columns = ("ID", "Customer", "Service", "Urgency", "Status", "Notes")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        headers = ["ID", "Customer", "Service", "Urgency", "Status", "Notes"]
        widths = [50, 150, 250, 100, 100, 200]
        for c, h, w in zip(columns, headers, widths):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor="center" if c!="Service" else "w")

        scrollbar = ctk.CTkScrollbar(table_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        self.all_jobs = backend.get_all_jobs()
        self.populate_table(self.all_jobs)

        self.btn = ctk.CTkButton(self, text="Select a Job", fg_color="gray", state="disabled", 
                                 height=50, font=("Arial", 16, "bold"), command=self.complete_selected)
        self.btn.pack(pady=20)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def filter_table(self, event=None):
        query = self.search_var.get().lower()
        if not query:
            self.populate_table(self.all_jobs)
        else:
            filtered_data = [job for job in self.all_jobs if query in job['customer_username'].lower()]
            self.populate_table(filtered_data)

    def populate_table(self, jobs_list):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for j in jobs_list:
            s = backend.SERVICES.get(j['service_id'], "Unknown")
            self.tree.insert("", "end", values=(j['job_id'], j['customer_username'], s, j['urgency'], j['status'], j['technician_notes']))

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel: 
            self.btn.configure(state="disabled", fg_color="gray", text="Select a Job")
            return
        status = self.tree.item(sel)['values'][4]
        if status == 'Pending':
            self.btn.configure(state="normal", fg_color="#F39C12", text="Complete Selected Job")
        else:
            self.btn.configure(state="disabled", fg_color="gray", text="Already Completed")

    def complete_selected(self):
        sel = self.tree.selection()
        job_id = str(self.tree.item(sel)['values'][0])
        job_dict = next((j for j in self.all_jobs if str(j['job_id']) == job_id), None)
        self.controller.show_view(CompleteJobView, job_dict=job_dict)

class CompleteJobView(BaseView):
    def __init__(self, parent, controller, job_dict):
        super().__init__(parent, controller)
        ctk.CTkButton(self, text="← Cancel", width=150, fg_color="gray", 
                      command=lambda: controller.show_view(TechBoardView)).pack(anchor="w", padx=20, pady=(20,0))
        
        self.job = job_dict
        center = ctk.CTkFrame(self)
        center.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(center, text=f"Completing Job #{self.job['job_id']}", font=("Arial", 22, "bold")).pack(pady=20, padx=50)
        ctk.CTkLabel(center, text="Collection Date (YYYY-MM-DD):").pack(anchor="w", padx=30)
        self.date_entry = ctk.CTkEntry(center, width=400)
        self.date_entry.pack(pady=(0, 10), padx=30)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ctk.CTkLabel(center, text="Technician Notes / Description:").pack(anchor="w", padx=30)
        self.txt = ctk.CTkTextbox(center, width=400, height=200)
        self.txt.pack(pady=10, padx=30)
        if self.job['technician_notes'] != "N/A": self.txt.insert("1.0", self.job['technician_notes'])
        
        ctk.CTkButton(center, text="Submit Completion", width=400, height=40, fg_color="green", command=self.submit).pack(pady=20)

    def submit(self):
        notes = self.txt.get("1.0", "end-1c").strip()
        date_val = self.date_entry.get().strip()

        if not notes:
            self.controller.show_error("Error", "Notes/Description required")
            return
        
        if not date_val:
            self.controller.show_error("Error", "Collection Date required")
            return

        success, msg = backend.update_job_completion(self.job['job_id'], notes, date_val)
        
        if success:
            self.controller.show_view(TechBoardView)
            self.controller.show_toast("Job marked as Completed!") 
        else:
            self.controller.show_error("Error", msg)

class CustomerRepairsView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.add_back_button()
        
        ctk.CTkLabel(self, text="My Repair Requests", font=("Arial", 24, "bold")).pack(pady=10)
        
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=50, pady=20)

        columns = ("ID", "Service", "Price", "Status", "Urgency")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        for c in columns: 
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")
        self.tree.column("Service", width=300, anchor="w") 
        
        self.tree.pack(side="left", fill="both", expand=True)

        self.jobs = backend.get_jobs_for_customer(self.controller.current_user['username'])
        for j in self.jobs:
            s = backend.SERVICES.get(j['service_id'], "Unknown")
            self.tree.insert("", "end", values=(j['job_id'], s, f"RM {j['price']}", j['status'], j['urgency']))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)

        self.change_btn = ctk.CTkButton(btn_frame, text="Change Service", fg_color="gray", state="disabled", 
                                        font=("Arial", 14, "bold"), command=self.change_service)
        self.change_btn.pack(side="left", padx=10)

        self.receipt_btn = ctk.CTkButton(btn_frame, text="💾 Download Receipt", fg_color="gray", state="disabled", 
                                         font=("Arial", 14, "bold"), command=self.download_receipt)
        self.receipt_btn.pack(side="left", padx=10)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        
        status = self.tree.item(sel)['values'][3]

        if status == 'Pending':
            self.change_btn.configure(state="normal", fg_color="orange")
            self.receipt_btn.configure(state="disabled", fg_color="gray")
            
        elif status == 'Paid':
            self.change_btn.configure(state="disabled", fg_color="gray")
            self.receipt_btn.configure(state="normal", fg_color="#2980B9") # Blue for info
            
        else: 
            self.change_btn.configure(state="disabled", fg_color="gray")
            self.receipt_btn.configure(state="disabled", fg_color="gray")

    def change_service(self):
        sel = self.tree.selection()
        job_id = str(self.tree.item(sel)['values'][0])
        job_dict = next((j for j in self.jobs if str(j['job_id']) == job_id), None)
        self.controller.show_view(ChangeServiceView, job_dict=job_dict)

    def download_receipt(self):
        sel = self.tree.selection()
        job_id = str(self.tree.item(sel)['values'][0])
        job = next((j for j in self.jobs if str(j['job_id']) == job_id), None)
        
        if not job: return

        c_name = self.controller.current_user['name']
        s_name = backend.SERVICES.get(job['service_id'], 'N/A')
        
        receipt_text = (
            "========================================\n"
            "       ABU LAPTOP REPAIR SERVICE        \n"
            "           CUSTOMER COPY                \n"
            "========================================\n"
            f"JOB ID:   {job['job_id']}\n"
            f"DATE:     {job['date_completed']}\n"
            "----------------------------------------\n"
            f"CUSTOMER: {c_name}\n"
            f"SERVICE:  {s_name}\n"
            f"URGENCY:  {job['urgency']}\n"
            "----------------------------------------\n"
            f"TOTAL PAID: RM {job['price']}\n"
            "========================================\n"
        )

        filename = f"Receipt_{job['job_id']}.txt"
        try:
            with open(filename, "w") as f: f.write(receipt_text)
            self.controller.show_toast(f"Saved to {filename}")
        except Exception as e:
            self.controller.show_error("Save Error", str(e))

class ChangeServiceView(BaseView):
    def __init__(self, parent, controller, job_dict):
        super().__init__(parent, controller)
        ctk.CTkButton(self, text="← Cancel", width=150, fg_color="gray", 
                      command=lambda: controller.show_view(CustomerRepairsView)).pack(anchor="w", padx=20, pady=(20,0))
        
        self.job = job_dict
        center = ctk.CTkFrame(self)
        center.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(center, text=f"Change Service #{self.job['job_id']}", font=("Arial", 22, "bold")).pack(pady=20)
        
        s_list = [f"{k} {v}" for k,v in backend.SERVICES.items()]
        self.combo = ctk.CTkComboBox(center, values=s_list, width=350)
        self.combo.pack(pady=20)
        self.combo.set(f"{self.job['service_id']} {backend.SERVICES.get(self.job['service_id'])}")
        
        self.urg_var = ctk.StringVar(value=self.job['urgency'])
        rads = ctk.CTkFrame(center, fg_color="transparent")
        rads.pack(pady=10)
        ctk.CTkRadioButton(rads, text="Normal", variable=self.urg_var, value="Normal").pack(side="left", padx=10)
        ctk.CTkRadioButton(rads, text="Urgent", variable=self.urg_var, value="Urgent").pack(side="left", padx=10)
        
        ctk.CTkButton(center, text="Confirm Update", command=self.save).pack(pady=20)

    def save(self):
        new_id = self.combo.get().split(" ")[0]
        success, msg = backend.update_customer_service(self.job['job_id'], new_id, self.urg_var.get())
        if success:
            self.controller.show_view(CustomerRepairsView)
            self.controller.show_toast(msg) 
        else:
            self.controller.show_error("Error", msg)

class NewJobView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.add_back_button()
        
        center = ctk.CTkFrame(self)
        center.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(center, text="New Job Ticket", font=("Arial", 22, "bold")).pack(pady=20, padx=50)

        customers = backend.get_all_customers() or ["No Customers"]
        
        ctk.CTkLabel(center, text="Customer").pack(anchor="w", padx=40)
        self.c_combo = ctk.CTkComboBox(center, values=customers, width=350)
        self.c_combo.pack(pady=(0, 15), padx=40)

        ctk.CTkLabel(center, text="Service").pack(anchor="w", padx=40)
        s_list = [f"{k} {v}" for k,v in backend.SERVICES.items()]
        self.s_combo = ctk.CTkComboBox(center, values=s_list, width=350, command=self.update_price)
        self.s_combo.pack(pady=(0, 15), padx=40)

        self.urg_var = ctk.StringVar(value="Normal")
        self.price_lbl = ctk.CTkLabel(center, text="Est. Price: RM --", font=("Arial", 20, "bold"), text_color="#2CC985")
        
        rads = ctk.CTkFrame(center, fg_color="transparent")
        rads.pack(pady=5)
        ctk.CTkRadioButton(rads, text="Normal", variable=self.urg_var, value="Normal", command=self.update_price).pack(side="left", padx=20)
        ctk.CTkRadioButton(rads, text="Urgent", variable=self.urg_var, value="Urgent", command=self.update_price).pack(side="left", padx=20)
        
        self.price_lbl.pack(pady=20)
        self.update_price()
        
        ctk.CTkButton(center, text="Create Ticket", command=self.submit).pack(pady=20)

    def update_price(self, *args):
        s_key = self.s_combo.get().split(" ")[0]
        p = backend.get_price(s_key, self.urg_var.get())
        self.price_lbl.configure(text=f"Est. Price: RM {p}")

    def submit(self):
        c = self.c_combo.get()
        if c == "No Customers": return
        success, msg = backend.create_job(c, self.s_combo.get().split(" ")[0], self.urg_var.get())
        if success:
            self.controller.show_view(DashboardView)
            self.controller.show_toast("Job Ticket Created!") # UX FIX: Redirect + Toast
        else:
            self.controller.show_error("Error", msg)

class MonthlyReportView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.add_back_button()
        ctk.CTkLabel(self, text="Monthly Report", font=("Arial", 24, "bold")).pack(pady=10)
        
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(pady=10)
        
        months = backend.get_available_months()
        self.combo = ctk.CTkComboBox(controls, values=months)
        self.combo.pack(side="left", padx=10)
        ctk.CTkButton(controls, text="Generate", command=self.generate).pack(side="left")
        
        self.area = ctk.CTkScrollableFrame(self, width=800)
        self.area.pack(fill='both', expand=True, padx=50, pady=20)

    def generate(self):
        for w in self.area.winfo_children(): w.destroy()
        m = self.combo.get()
        jobs, counts, total = backend.get_monthly_report_data(m)
        
        if not jobs:
            ctk.CTkLabel(self.area, text="No Data").pack(pady=20)
            return

        ctk.CTkLabel(self.area, text=f"REPORT: {m}", font=("Arial", 20, "bold")).pack(pady=20)
        ctk.CTkLabel(self.area, text=f"Revenue: RM {total:.2f}", font=("Arial", 26, "bold"), text_color="#2CC985").pack(pady=20)
        for s_id, count in counts.items():
            name = backend.SERVICES.get(s_id, "Unknown")
            ctk.CTkLabel(self.area, text=f"{count}x  {name}", anchor="w").pack(fill="x", padx=50)

class UpdateProfileView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.add_back_button()
        
        u_name = self.controller.current_user.get('username')
        data = backend.get_user_details(u_name)
        
        center = ctk.CTkFrame(self)
        center.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(center, text="Edit Profile", font=("Arial", 22, "bold")).pack(pady=20, padx=40)
        
        self.entries = {}
        for key, label, show in [('name', 'Name', ''), ('phone', 'Phone', ''), ('password', 'Password', '')]:
            ctk.CTkLabel(center, text=label).pack(anchor="w", padx=20)
            e = ctk.CTkEntry(center, width=300)
            if show: e.configure(show=show)
            e.insert(0, data.get(key, ''))
            e.pack(pady=(0,10), padx=20)
            self.entries[key] = e

        ctk.CTkButton(center, text="Save", command=self.save).pack(pady=20)

    def save(self):
        u = self.controller.current_user['username']
        success, msg = backend.update_user_profile(u, self.entries['password'].get(), self.entries['name'].get(), self.entries['phone'].get())
        if success:
            self.controller.current_user['name'] = self.entries['name'].get()
            self.controller.show_view(DashboardView)
            self.controller.show_toast("Profile Updated Successfully!") # UX FIX
        else:
            self.controller.show_error("Error", msg)

if __name__ == "__main__":
    app = RepairApp()
    app.mainloop()