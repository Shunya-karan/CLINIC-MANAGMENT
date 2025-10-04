import customtkinter as ctk
from tkinter import ttk, messagebox
import pymysql
from tkinter import messagebox, Toplevel
from PIL import Image, ImageTk
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from tkinter import filedialog
import threading
import tkinter as tk
from tkinter import Button

# Set appearance mode and color theme
ctk.set_appearance_mode("light")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

#COLORS 
dbc = "#07002B"
mbc = "#294B82"
lbc = "#4EBEFA"
hbc = "#1A2750"

# Database connection
conn1 = pymysql.connect(
    host="localhost", 
    user="root", 
    password="root",
    database="clinic_management"
)
cursor1 = conn1.cursor()

def databaseconnectivity():
    try:
        conn = pymysql.connect(
            host="localhost", 
            user="root", 
            password="root",
            database="clinic_management"
        )
        print("Connected to database")
        return conn
    except pymysql.MySQLError as e:
        print("Error connecting to database:", e)
        messagebox.showerror("Database Error", f"Error connecting to database:\n{e}")
        return None

# Fetch patients based on search query
def search_patient():
    query = search_entry.get().strip()
    if not query or query == "SEARCH PATIENT":
        messagebox.showwarning("Input Error", "Please enter a valid patient name to search!")
        return

    try:
        db = databaseconnectivity()
        cursor = db.cursor()

        sql = """
            SELECT 
                b.bill_id,
                CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
                a.appointment_id,
                a.appointment_date,
                b.total_amount,
                b.payment_status
            FROM billing b
            JOIN appointments a ON b.appointment_id = a.appointment_id
            JOIN patients p ON a.patient_id = p.patient_id
            WHERE p.first_name LIKE %s
            ORDER BY b.bill_id;
        """

        cursor.execute(sql, ("%" + query + "%",))
        rows = cursor.fetchall()
        db.close()

        tree.delete(*tree.get_children())  # Clear old results
        for row in rows:
            tree.insert("", "end", values=row)

    except pymysql.Error as e:
        messagebox.showerror("Database Error", f"Error fetching data: {e}")

def show_paid_patients_window():
    """
    Opens a window displaying all paid patients with their payment screenshots.
    This function can be called from any button click event.
    """
    
    # Database configuration
    DB_CONFIG = {
        "host": "localhost",
        "user": "root",
        "password": "root",
        "database": "clinic_management"
    }
    
    # Colors
    DBC = "#001739"  # Dark Blue
    LBC = "#424242"  # Light Blue
    TEXT_COLOR = "#FFFFFF"
    ACCENT_COLOR = "#00D4FF"
    INFO_COLOR = "#4A90E2"
    INFO_HOVER = "#357ABD"
    REJECT_COLOR = "#FF4444"
    REJECT_HOVER = "#CC0000"
    
    def get_connection():
        """Establishes database connection."""
        try:
            return pymysql.connect(**DB_CONFIG)
        except pymysql.Error as e:
            messagebox.showerror("Database Error", f"Failed to connect:\n{e}")
            return None
    
    def show_payment_screenshot(screenshot_blob, patient_name):
        """Display the payment screenshot in a new window."""
        if not screenshot_blob:
            messagebox.showwarning("No Image", "No payment screenshot available.")
            return
        
        try:
            # Convert blob to PIL Image
            image_data = io.BytesIO(screenshot_blob)
            pil_image = Image.open(image_data)
            
            # Create image window
            img_window = Toplevel()
            img_window.title(f"Payment Screenshot - {patient_name}")
            img_window.configure(bg=DBC)
            
            # Scale image if too large
            img_width, img_height = pil_image.size
            max_width, max_height = 800, 600
            
            if img_width > max_width or img_height > max_height:
                ratio = min(max_width/img_width, max_height/img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(pil_image)
            
            # Set window size
            window_width = pil_image.width + 40
            window_height = pil_image.height + 100
            img_window.geometry(f"{window_width}x{window_height}")
            
            # Center and make modal
            img_window.transient()
            img_window.grab_set()
            
            # Title
            title_label = ctk.CTkLabel(img_window, 
                                     text=f"💳 {patient_name}'s Payment Screenshot", 
                                     font=("Arial", 16, "bold"), 
                                     text_color=ACCENT_COLOR)
            title_label.pack(pady=10)
            
            # Image display
            img_label = ctk.CTkLabel(img_window, image=photo, text="")
            img_label.pack(pady=10)
            img_label.image = photo  # Keep reference
            
            # Close button
            close_btn = ctk.CTkButton(img_window, text="Close", 
                                    font=("Arial", 12, "bold"),
                                    fg_color=REJECT_COLOR, 
                                    hover_color=REJECT_HOVER,
                                    width=80, height=30,
                                    command=img_window.destroy)
            close_btn.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Image Error", f"Failed to display screenshot:\n{e}")
    
    # Get database connection
    conn = get_connection()
    if not conn:
        return
    
    try:
        with conn.cursor() as cursor:
            # Query to get paid patients with their full names and screenshots
            # Join billing -> appointments -> patients to get patient names
            query = """
            SELECT b.bill_id, 
                   CONCAT(p.first_name, ' ', p.last_name) as patient_name,
                   b.total_amount, 
                   b.payment_screenshot, 
                   b.created_at
            FROM billing b
            JOIN appointments a ON b.appointment_id = a.appointment_id
            JOIN patients p ON a.patient_id = p.patient_id
            WHERE b.payment_status = 'Paid'
            ORDER BY b.created_at DESC
            """
            cursor.execute(query)
            paid_patients = cursor.fetchall()
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to fetch data:\n{e}")
        return
    finally:
        if conn:
            conn.close()
    
    if not paid_patients:
        messagebox.showinfo("No Data", "No paid patients found.")
        return
    
    # Create main window
    paid_window = Toplevel()
    paid_window.title("Paid Patients - Payment Screenshots")
    paid_window.configure(bg=DBC)
    paid_window.geometry("850x650")
    paid_window.resizable(True, True)
    
    # Make window modal
    paid_window.transient()
    paid_window.grab_set()
    
    # Title
    title_label = ctk.CTkLabel(paid_window, 
                             text="💳 Paid Patients - Payment Screenshots", 
                             font=("Arial", 24, "bold"), 
                             text_color=ACCENT_COLOR)
    title_label.pack(pady=20)
    
    # Main scrollable frame
    main_frame = ctk.CTkFrame(paid_window, fg_color=LBC, corner_radius=10)
    main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    # Create scrollable area
    canvas = ctk.CTkCanvas(main_frame, bg=LBC, highlightthickness=0)
    scrollbar = ctk.CTkScrollbar(main_frame, orientation="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas, fg_color=LBC)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
    scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
    
    # Add patient entries
    for bill_id, patient_name, amount, screenshot_blob, created_at in paid_patients:
        # Patient card frame
        patient_frame = ctk.CTkFrame(scrollable_frame, fg_color=DBC, corner_radius=8)
        patient_frame.pack(fill="x", padx=10, pady=8)
        
        # Patient info container
        info_container = ctk.CTkFrame(patient_frame, fg_color="transparent")
        info_container.pack(fill="x", padx=15, pady=12)
        
        # Left side - Patient details
        details_frame = ctk.CTkFrame(info_container, fg_color="transparent")
        details_frame.pack(side="left", fill="x", expand=True)
        
        # Patient name
        name_label = ctk.CTkLabel(details_frame, 
                                text=f"👤 {patient_name}",
                                font=("Arial", 16, "bold"),
                                text_color=TEXT_COLOR,
                                anchor="w")
        name_label.pack(anchor="w")
        
        # Bill details
        bill_info = f"Bill ID: {bill_id} | Amount: ₹{amount} | Date: {created_at.strftime('%Y-%m-%d %H:%M')}"
        info_label = ctk.CTkLabel(details_frame, 
                                text=bill_info,
                                font=("Arial", 12),
                                text_color="lightgray",
                                anchor="w")
        info_label.pack(anchor="w", pady=(5, 0))
        
        # Right side - Screenshot button
        button_frame = ctk.CTkFrame(info_container, fg_color="transparent")
        button_frame.pack(side="right", padx=(10, 0))
        
        if screenshot_blob:
            screenshot_btn = ctk.CTkButton(
                button_frame, 
                text="📷 View Screenshot", 
                font=("Arial", 12, "bold"),
                fg_color=INFO_COLOR, 
                hover_color=INFO_HOVER,
                width=150, 
                height=35,
                corner_radius=6,
                command=lambda blob=screenshot_blob, name=patient_name: show_payment_screenshot(blob, name)
            )
            screenshot_btn.pack()
        else:
            no_img_label = ctk.CTkLabel(button_frame, 
                                      text="No Screenshot", 
                                      font=("Arial", 12, "italic"),
                                      text_color="gray")
            no_img_label.pack(pady=10)
    
    # Mouse wheel scrolling
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    # Close button
    close_btn = ctk.CTkButton(paid_window, 
                            text="Close Window", 
                            font=("Arial", 14, "bold"),
                            fg_color=REJECT_COLOR, 
                            hover_color=REJECT_HOVER,
                            width=120, 
                            height=40,
                            command=paid_window.destroy)
    close_btn.pack(pady=(0, 20))

# Handle placeholder text behavior
def on_entry_click(event):
    if search_entry.get() == "SEARCH PATIENT":
        search_entry.delete(0, "end")

def on_focus_out(event):
    if not search_entry.get():
        search_entry.insert(0, "SEARCH PATIENT")

def close_appointment():
    paymentwindow.destroy()

def show_table():
    db = databaseconnectivity()
    cursor = db.cursor()
    sql = """SELECT 
                    b.bill_id,
                        CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
                        a.appointment_id,
                        a.appointment_date,
                        b.total_amount,
                        b.payment_status
                    FROM billing b
                    JOIN appointments a ON b.appointment_id = a.appointment_id
                    JOIN patients p ON a.patient_id = p.patient_id
                    ORDER BY b.bill_id;"""
    cursor.execute(sql)
    rows = cursor.fetchall()
    sqls = "select sum(total_amount) from billing"
    cursor.execute(sqls)
    total = cursor.fetchall()
    print(total[0][0])
    db.close()
    tree.delete(*tree.get_children())  # Clear old results
    for index, row in enumerate(rows):
        tag = mbc if index % 2 == 0 else lbc  # Alternate between colors
        tree.insert("", "end", values=row, tags=(tag,))

    tree.insert('', "end", values=(" ", " ", " ", " ", "Total :", total[0][0]), tags=("bold",))
    tree.tag_configure("bold", font=('Helvetica ', 18, 'bold'))


def on_refresh_enter(event):
    refresh_label.configure(text_color="grey")
def on_refresh_leave(event):
    refresh_label.configure(text_color="Black")
def on_enter(event):
    back_label.configure(text_color="grey") 

def on_leave(event):
    back_label.configure(text_color="black")


def unpaid_patients_action():
    """Function to handle unpaid patients button click - opens popup window"""
    try:
        db = databaseconnectivity()
        cursor = db.cursor()
        
        sql = """
            SELECT 
                b.bill_id,
                CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
                p.email,
                a.appointment_id,
                a.appointment_date,
                b.total_amount,
                b.payment_status
            FROM billing b
            JOIN appointments a ON b.appointment_id = a.appointment_id
            JOIN patients p ON a.patient_id = p.patient_id
            WHERE b.payment_status = 'Unpaid' OR b.payment_status = 'Pending'
            ORDER BY b.bill_id;
        """
        
        cursor.execute(sql)
        rows = cursor.fetchall()
        db.close()
        
        if not rows:
            messagebox.showinfo("No Results", "No unpaid patients found!")
            return
            
        # Create popup window
        create_unpaid_patients_window(rows)
        
    except pymysql.Error as e:
        messagebox.showerror("Database Error", f"Error fetching unpaid patients: {e}")

def create_unpaid_patients_window(unpaid_data):
    """Create popup window with unpaid patients list and email buttons"""
    popup = tk.Toplevel()
    popup.title("Unpaid Patients - Payment Reminders")
    popup.geometry("800x650")
    popup.resizable(True, True)
    popup.grab_set()
    
    # Global variable to store QR code path
    if not hasattr(create_unpaid_patients_window, 'qr_path'):
        create_unpaid_patients_window.qr_path = ""
    
    # Main frame
    main_frame = ttk.Frame(popup, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Configure grid weights
    popup.columnconfigure(0, weight=1)
    popup.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(1, weight=1)
    
    # Title
    title_label = ttk.Label(main_frame, text="Unpaid Patients", font=("Arial", 16, "bold"))
    title_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)
    
    # Create treeview with scrollbar
    tree_frame = ttk.Frame(main_frame)
    tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    tree_frame.columnconfigure(0, weight=1)
    tree_frame.rowconfigure(0, weight=1)
    
    # Define columns
    columns = ("Bill ID", "Patient Name", "Email", "Appointment ID", "Date", "Amount", "Status")
    
    popup_tree = ttk.Treeview(tree_frame,columns=columns, show="headings", height=15 )
    popup_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Configure column headings and widths
    popup_tree.heading("Bill ID", text="Bill ID")
    popup_tree.heading("Patient Name", text="Patient Name")
    popup_tree.heading("Email", text="Email")
    popup_tree.heading("Appointment ID", text="Appointment ID")
    popup_tree.heading("Date", text="Date")
    popup_tree.heading("Amount", text="Amount (Rs. )")
    popup_tree.heading("Status", text="Status")
   
    
    popup_tree.column("Bill ID", width=80)
    popup_tree.column("Patient Name", width=150)
    popup_tree.column("Email", width=200)
    popup_tree.column("Appointment ID", width=100)
    popup_tree.column("Date", width=100)
    popup_tree.column("Amount", width=100)
    popup_tree.column("Status", width=80)
    
    popup_tree.tag_configure("white", background="white")
    popup_tree.tag_configure(lbc, background=lbc)

    # Scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=popup_tree.yview)
    scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    popup_tree.configure(yscrollcommand=scrollbar.set)
    
    # Dictionary to store patient data mapped to tree item IDs
    patient_data_map = {}
    
    # Insert data and create send email buttons
    for i, row in enumerate(unpaid_data):
        bill_id, patient_name, email, appointment_id, appointment_date, total_amount, payment_status = row
        
        # Insert row data
        tag = mbc if index % 2 == 0 else lbc
        item_id = popup_tree.insert("", "end", values=(
            bill_id, patient_name, email, appointment_id, 
            appointment_date, f"Rs. {total_amount:.2f}", payment_status, ""
        ),tags=(tag,))
        
        # Store patient data for email sending
        patient_data_map[item_id] = {
            'bill_id': bill_id,
            'patient_name': patient_name,
            'email': email,
            'appointment_id': appointment_id,
            'appointment_date': appointment_date,
            'total_amount': total_amount,
            'payment_status': payment_status
        }

    def load_qr_path_from_database():
        """Load QR path from database, return None if not found"""
        try:
            cursor.execute("SELECT qr FROM doctor_login LIMIT 1")
            result = cursor.fetchone()
            if result and result[0]:
                return result[0]
            return None
        except Exception as e:
            print(f"Error loading QR path from database: {e}")
            return None

    def save_qr_path_to_database(qr_path):
        """Save QR path to database"""
        db = databaseconnectivity()
        cursor = db.cursor()
        try:
            # Check if any record exists
            cursor.execute("SELECT COUNT(*) FROM doctor_login")
            count = cursor.fetchone()[0]
            
            if count > 0:
                # Update existing record
                cursor.execute("UPDATE doctor_login SET qr = %s", (qr_path,))
            else:
                # Insert new record (you may need to adjust this based on your table structure)
                cursor.execute("INSERT INTO doctor_login (qr) VALUES (%s)", (qr_path,))
            
            db.commit()
            db.close()
            print("QR path saved to database successfully")
        except Exception as e:
            print(f"Error saving QR path to database: {e}") 

    # Bind double-click to send email

    def on_double_click(event):
        selected_items = popup_tree.selection()
        if selected_items:
            qr_path = qr_path_var.get().strip()
            if not qr_path:
                messagebox.showwarning("QR Code Required", "Please provide the QR code image path before sending emails.")
                return
                
            item = selected_items[0]
            patient_data = patient_data_map.get(item)
            if patient_data:
                send_payment_reminder_email(patient_data, qr_path)
    
    popup_tree.bind("<Double-1>", on_double_click)
    
    # QR Code path configuration frame
    qr_frame = ttk.LabelFrame(main_frame, text="QR Code Configuration", padding="10")
    qr_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    qr_frame.columnconfigure(1, weight=1)
    
    ttk.Label(qr_frame, text="QR Code Path:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
    db_qr_path = load_qr_path_from_database()
    initial_qr_path = db_qr_path if db_qr_path else ""

    qr_path_var = tk.StringVar(value=initial_qr_path)
    qr_path_entry = ttk.Entry(qr_frame, textvariable=qr_path_var, width=50)
    qr_path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))

    if hasattr(create_unpaid_patients_window, 'qr_path'):
        create_unpaid_patients_window.qr_path = initial_qr_path

    def browse_qr_file():
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select QR Code Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff")]
        )
        if file_path:
            qr_path_var.set(file_path)
            # Save to database immediately when user selects a new file
            save_qr_path_to_database(file_path)
            # Update window attribute if it exists
            if hasattr(create_unpaid_patients_window, 'qr_path'):
                create_unpaid_patients_window.qr_path = file_path
            print("QR path updated and saved to database")
           
    # browse_btn = ttk.Button(qr_frame, text="Browse", command=browse_qr_file)
    # browse_btn.grid(row=0, column=2)
    browse_btn = tk.Button(qr_frame,
                       text="Browse",
                       command=browse_qr_file,
                       bg="#90EE90",    # Light green
                       fg="black",      # Text color
                       font=("Arial", 12),
                       width=10,
                       height=1)
    browse_btn.grid(row=0, column=2)

    # Update QR path when entry changes manually
    def on_qr_path_change(*args):
        new_path = qr_path_var.get()
        # Save to database when path is changed manually
        if new_path.strip():  # Only save if path is not empty
            save_qr_path_to_database(new_path)
        # Update window attribute if it exists
        if hasattr(create_unpaid_patients_window, 'qr_path'):
            create_unpaid_patients_window.qr_path = new_path
    
    qr_path_var.trace_add('write', on_qr_path_change)
    
    # Buttons frame
    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.grid(row=3, column=0, pady=(10, 0), sticky=tk.W)
    
    # Send email to selected patient button
    def send_to_selected():
        selected_items = popup_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a patient to send email to.")
            return
        
        qr_path = qr_path_var.get().strip()
        if not qr_path:
            messagebox.showwarning("QR Code Required", "Please provide the QR code image path before sending emails.")
            return
        
        for item in selected_items:
            patient_data = patient_data_map.get(item)
            if patient_data:
                send_payment_reminder_email(patient_data, qr_path)
    
    # send_selected_btn = ttk.Button(buttons_frame, text="Send Email to Selected" ,command=send_to_selected)
    # send_selected_btn.grid(row=0, column=0, padx=(0, 10))
    send_selected_btn = Button(buttons_frame,
    text="Send Email to Selected",
    width=20,
    height=2,
    bg=mbc,
    fg="white",
    font=("Arial", 15),
    command=send_to_selected
)
    send_selected_btn.grid(row=0, column=0, padx=(0, 10))
    
    # Send email to all unpaid patients button
    def send_to_all():
        qr_path = qr_path_var.get().strip()
        if not qr_path:
            messagebox.showwarning("QR Code Required", "Please provide the QR code image path before sending emails.")
            return
            
        if messagebox.askyesno("Confirm", "Send payment reminder emails to all unpaid patients?"):
            for item in popup_tree.get_children():
                patient_data = patient_data_map.get(item)
                if patient_data:
                    send_payment_reminder_email(patient_data, qr_path)
    
    # send_all_btn = ttk.Button(buttons_frame, text="Send Email to All", command=send_to_all)
    # send_all_btn.grid(row=0, column=1, padx=(0, 10))
    
    send_selected_btn = tk.Button(
    buttons_frame,
    text="Send Email to All",
    bg=mbc,
    fg="white",
    font=("Arial", 15),
    width=20,
    height=2,  # Adjusted for better appearance
    command=lambda:send_to_all()
)
    send_selected_btn.grid(row=0, column=2, padx=(0, 10))

    # Close button
    # close_btn = ttk.Button(buttons_frame, text="Close", command=popup.destroy)
    # close_btn.grid(row=0, column=2)
    close_btn = tk.Button(buttons_frame, text="Close", command=popup.destroy,
                      bg="#DC3545",    # Red background
                      fg="white",      # White text
                      font=("Arial", 12),
                      width=10,
                      height=1)
    close_btn.grid(row=0, column=3)

    # Instructions label
    instructions = ttk.Label(main_frame, 
                           text="Instructions: 1) Set QR code path first, 2) Double-click on a patient row or select and click 'Send Email to Selected'.",
                           font=("Arial", 9))
    instructions.grid(row=4, column=0, pady=(10, 0), sticky=tk.W)

def send_payment_reminder_email(patient_data, qr_image_path):
    """Send payment reminder email with QR code attachment"""
    try:
        # Email configuration - UPDATE THESE WITH YOUR ACTUAL EMAIL SETTINGS
        smtp_server = "smtp.gmail.com"  # Change to your email provider
        smtp_port = 587
        sender_email = ""  # Change to your email
        sender_password = ""  # Change to your app password
        
        # Patient details
        patient_name = patient_data['patient_name']
        patient_email = patient_data['email']
        amount = patient_data['total_amount']
        bill_id = patient_data['bill_id']
        appointment_date = patient_data['appointment_date']
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = patient_email
        msg['Subject'] = f"Payment Reminder - Bill #{bill_id}"
        
        # Email body
        body = f"""
Dear {patient_name},

We hope this message finds you well. This is a friendly reminder regarding your outstanding payment for the medical services provided.

Payment Details:
- Bill ID: {bill_id}
- Appointment Date: {appointment_date}
- Amount Due: Rs. {amount:.2f}

For your convenience, we have attached a QR code that you can scan to make the payment quickly and securely.

Payment Options:
1. Scan the QR code attached to this email
2. Visit our clinic during business hours
3. Call us at [Your Phone Number] to make payment over the phone

If you have already made this payment, please disregard this message. If you have any questions or concerns regarding this bill, please don't hesitate to contact us.

Thank you for your prompt attention to this matter.

Best regards,
CLINCLOUD
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach QR code image
        if os.path.exists(qr_image_path):
            with open(qr_image_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= "Payment_QR_Code.png"'
                )
                msg.attach(part)
        else:
            messagebox.showwarning("QR Code Not Found", 
                                 f"QR code image not found at: {qr_image_path}\n"
                                 "Please provide the correct path to your QR code image.")
            return
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, patient_email, text)
        server.quit()
        
        messagebox.showinfo("Email Sent", f"Payment reminder sent successfully to {patient_name} ({patient_email})")
        
    except Exception as e:
        messagebox.showerror("Email Error", f"Failed to send email to {patient_data['patient_name']}: {str(e)}")

# Configuration function to set up email settings
def configure_email_settings():
    """Function to configure email settings - call this once to set up your email"""
    config_window = tk.Toplevel()
    config_window.title("Email Configuration")
    config_window.geometry("400x300")
    
    # Add configuration fields here
    # This is a placeholder for email configuration UI
    # You can implement this to save email settings to a config file
    pass

def dr_charges():
    drcharges = ctk.CTkInputDialog(title="Doctor Fee", text="Enter the Doctor Fees :").get_input()
    if not drcharges:
        messagebox.showerror("Error", "Please enter the Doctor Fees ")
        return
    db=databaseconnectivity()
    cursor = db.cursor()
    cursor.execute("update doctor_login set doctor_charges=%s",(drcharges))
    db.commit()
    db.close()

def additional_charges():
    """Function to handle additional charges - first asks for bill ID, then opens popup for adding charges"""
    
    # First, get the bill ID
    def get_bill_id():
        """Function to get bill_id from user before opening charges window"""
        bill_id_window = ctk.CTkToplevel()
        bill_id_window.title("Enter Bill ID")
        bill_id_window.geometry("450x350")
        bill_id_window.grab_set()
        bill_id_window.resizable(False, False)
        
        # Center the window
        bill_id_window.transient()
        bill_id_window.focus()
        
        # Configure appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Title
        title_label = ctk.CTkLabel(bill_id_window, text="Add Additional Charges", 
                                  font=ctk.CTkFont(size=20, weight="bold"),
                                  text_color="#1f2937")
        title_label.pack(pady=(30, 15))
        
        # Instructions
        instructions = ctk.CTkLabel(bill_id_window, text="Enter the Bill ID to add additional charges:", 
                                   font=ctk.CTkFont(size=14),
                                   text_color="#4b5563")
        instructions.pack(pady=(0, 25))
        
        # Bill ID input frame
        input_frame = ctk.CTkFrame(bill_id_window, fg_color="transparent")
        input_frame.pack(pady=15)
        
        bill_id_label = ctk.CTkLabel(input_frame, text="Bill ID:", 
                                    font=ctk.CTkFont(size=14, weight="bold"),
                                    text_color="#374151")
        bill_id_label.pack(pady=(0, 10))
        
        bill_id_entry = ctk.CTkEntry(input_frame, 
                                    font=ctk.CTkFont(size=16), 
                                    width=200, 
                                    height=40,
                                    justify='center',
                                    placeholder_text="Enter Bill ID",
                                    corner_radius=10)
        bill_id_entry.pack()
        bill_id_entry.focus()
        
        # Buttons frame
        button_frame = ctk.CTkFrame(bill_id_window, fg_color="transparent")
        button_frame.pack(pady=30)
        
        def proceed_with_bill():
            """Validate bill ID and proceed to charges window"""
            try:
                bill_id = int(bill_id_entry.get().strip())
                if bill_id <= 0:
                    messagebox.showerror("Invalid Input", "Please enter a valid Bill ID (positive number)")
                    return
                
                # Check if bill exists in database
                try:
                    db = databaseconnectivity()
                    cursor = db.cursor()
                    cursor.execute("SELECT bill_id, total_amount FROM billing WHERE bill_id = %s", (bill_id,))
                    bill_data = cursor.fetchone()
                    db.close()
                    
                    if not bill_data:
                        messagebox.showerror("Bill Not Found", f"Bill ID {bill_id} does not exist in the database!")
                        return
                    
                    # Bill exists, close this window and open charges window
                    bill_id_window.destroy()
                    # Convert decimal to float for consistency
                    current_total = float(bill_data[1]) if bill_data[1] is not None else 0.0
                    open_charges_window(bill_id, current_total)  # Pass bill_id and current total
                    
                except Exception as e:
                    messagebox.showerror("Database Error", f"Error checking bill: {str(e)}")
                    
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid numeric Bill ID")
        
        def cancel_operation():
            """Close the window without proceeding"""
            bill_id_window.destroy()
        
        # Proceed button
        proceed_btn = ctk.CTkButton(button_frame, 
                                   text="✓ Proceed", 
                                   font=ctk.CTkFont(size=14, weight="bold"),
                                   fg_color="#22c55e",
                                   hover_color="#16a34a",
                                   width=140, 
                                   height=45,
                                   corner_radius=15,
                                   command=proceed_with_bill)
        proceed_btn.pack(side="left", padx=(0, 15))
        
        # Cancel button
        cancel_btn = ctk.CTkButton(button_frame, 
                                  text="✗ Cancel", 
                                  font=ctk.CTkFont(size=14, weight="bold"),
                                  fg_color="#ef4444",
                                  hover_color="#dc2626",
                                  width=140, 
                                  height=45,
                                  corner_radius=15,
                                  command=cancel_operation)
        cancel_btn.pack(side="left")
        
        # Bind Enter key to proceed
        bill_id_entry.bind('<Return>', lambda e: proceed_with_bill())
        
    def open_charges_window(bill_id, current_total):
        """Open the charges window for the specified bill ID"""
        
        # Create popup window
        charges_window = ctk.CTkToplevel()
        charges_window.title(f"Additional Charges - Bill ID: {bill_id}")
        charges_window.geometry("800x600")
        charges_window.resizable(True, True)
        charges_window.grab_set()
        
        # Main scrollable frame
        main_frame = ctk.CTkScrollableFrame(charges_window, 
                                           width=750, 
                                           height=500,
                                           corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title with bill info
        title_label = ctk.CTkLabel(main_frame, 
                                  text=f"Additional Charges for Bill ID: {bill_id}", 
                                  font=ctk.CTkFont(size=22, weight="bold"),
                                  text_color="#1f2937")
        title_label.pack(pady=(20, 10))
        
        # Current total display
        current_total_frame = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#f0f9ff")
        current_total_frame.pack(pady=(0, 25), padx=20, fill="x")
        
        current_total_label = ctk.CTkLabel(current_total_frame, 
                                          text=f"Current Bill Total: ₹{current_total:.2f}", 
                                          font=ctk.CTkFont(size=16, weight="bold"),
                                          text_color="#0369a1")
        current_total_label.pack(pady=15)
        
        # Container for charge entries
        charges_container = ctk.CTkFrame(main_frame, corner_radius=12)
        charges_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # List to store charge entry widgets
        charge_entries = []
        
        def create_charge_entry(parent, row_num=1):
            """Create a single charge entry row with amount and description fields"""
            
            # Frame for each charge entry
            entry_frame = ctk.CTkFrame(parent, corner_radius=10)
            entry_frame.pack(fill="x", pady=10, padx=15)
            
            # Title for the charge
            charge_title = ctk.CTkLabel(entry_frame, 
                                       text=f"Charge #{row_num}",
                                       font=ctk.CTkFont(size=16, weight="bold"),
                                       text_color="#374151")
            charge_title.pack(pady=(15, 10))
            
            # Input fields container
            fields_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
            fields_frame.pack(fill="x", padx=20, pady=(0, 15))
            
            # Amount field
            amount_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
            amount_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
            
            amount_label = ctk.CTkLabel(amount_frame, 
                                       text="Amount (₹):",
                                       font=ctk.CTkFont(size=14, weight="bold"),
                                       text_color="#374151")
            amount_label.pack(anchor="w", pady=(0, 5))
            
            amount_entry = ctk.CTkEntry(amount_frame, 
                                       font=ctk.CTkFont(size=14), 
                                       height=35,
                                       placeholder_text="0.00",
                                       corner_radius=8)
            amount_entry.pack(fill="x")
            
            # Description field
            desc_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
            desc_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))
            
            desc_label = ctk.CTkLabel(desc_frame, 
                                     text="Description:",
                                     font=ctk.CTkFont(size=14, weight="bold"),
                                     text_color="#374151")
            desc_label.pack(anchor="w", pady=(0, 5))
            
            desc_entry = ctk.CTkEntry(desc_frame, 
                                     font=ctk.CTkFont(size=14), 
                                     height=35,
                                     placeholder_text="Enter description",
                                     corner_radius=8)
            desc_entry.pack(fill="x")
            
            # Remove button
            remove_btn = ctk.CTkButton(entry_frame, 
                                      text="❌ Remove", 
                                      font=ctk.CTkFont(size=12, weight="bold"),
                                      fg_color="#ef4444",
                                      hover_color="#dc2626",
                                      width=100,
                                      height=30,
                                      corner_radius=8,
                                      command=lambda: remove_charge_entry(entry_frame))
            remove_btn.pack(pady=(0, 15))
            
            # Store references
            entry_data = {
                'frame': entry_frame,
                'amount': amount_entry,
                'description': desc_entry,
                'remove_btn': remove_btn,
                'title': charge_title
            }
            
            charge_entries.append(entry_data)
            update_remove_buttons()
            
            return entry_data
        
        def remove_charge_entry(frame_to_remove):
            """Remove a charge entry"""
            # Find and remove the entry from the list
            for i, entry in enumerate(charge_entries):
                if entry['frame'] == frame_to_remove:
                    entry['frame'].destroy()
                    charge_entries.pop(i)
                    break
            
            # Update numbering
            update_entry_numbers()
            update_remove_buttons()
        
        def update_entry_numbers():
            """Update the numbering of charge entries"""
            for i, entry in enumerate(charge_entries):
                entry['title'].configure(text=f"Charge #{i+1}")
        
        def update_remove_buttons():
            """Show/hide remove buttons based on number of entries"""
            show_remove = len(charge_entries) > 1
            for entry in charge_entries:
                if show_remove:
                    entry['remove_btn'].pack(pady=(0, 15))
                else:
                    entry['remove_btn'].pack_forget()
        
        def add_more_charges():
            """Add another charge entry field"""
            create_charge_entry(charges_container, len(charge_entries) + 1)
            # Auto-scroll to show new entry
            main_frame._parent_canvas.yview_moveto(1.0)
        
        def save_charges():
            """Save all the additional charges to the specified bill"""
            charges_data = []
            
            # Collect all charge data
            for i, entry in enumerate(charge_entries):
                amount = entry['amount'].get().strip()
                description = entry['description'].get().strip()
                
                if amount and description:
                    try:
                        amount_float = float(amount)
                        if amount_float > 0:
                            charges_data.append({
                                'amount': amount_float,
                                'description': description
                            })
                        else:
                            messagebox.showerror("Invalid Amount", f"Charge #{i+1}: Amount must be greater than 0")
                            return
                    except ValueError:
                        messagebox.showerror("Invalid Amount", f"Charge #{i+1}: Please enter a valid number for amount")
                        return
                elif amount or description:  # If one field is filled but not the other
                    messagebox.showwarning("Incomplete Entry", f"Charge #{i+1}: Both amount and description are required")
                    return
            
            if not charges_data:
                messagebox.showwarning("No Charges", "Please add at least one charge with both amount and description")
                return
            
            # Calculate totals
            additional_total = sum(charge['amount'] for charge in charges_data)
            new_total = float(current_total) + additional_total
            
            # Show confirmation with summary
            summary_text = f"Additional Charges for Bill ID: {bill_id}\n\n"
            for i, charge in enumerate(charges_data, 1):
                summary_text += f"{i}. {charge['description']}: ₹{charge['amount']:.2f}\n"
            summary_text += f"\nAdditional Charges: ₹{additional_total:.2f}"
            summary_text += f"\nCurrent Total: ₹{current_total:.2f}"
            summary_text += f"\nNew Total: ₹{new_total:.2f}"
            
            if messagebox.askyesno("Confirm Charges", f"{summary_text}\n\nProceed to save these charges?"):
                save_to_database(bill_id, charges_data, additional_total, new_total)
        
        def save_to_database(bill_id, charges_data, additional_total, new_total):
            """Save charges to database"""
            try:
                db = databaseconnectivity()
                cursor = db.cursor()
                
                # Insert charges into billing_items
                for charge in charges_data:
                    cursor.execute("""
                        INSERT INTO billing_items (bill_id, description, amount) 
                        VALUES (%s, %s, %s)
                    """, (bill_id, charge['description'], charge['amount']))
                
                # Update total amount in billing table
                cursor.execute("""
                    UPDATE billing SET total_amount = %s WHERE bill_id = %s
                """, (new_total, bill_id))
                
                db.commit()
                db.close()
                
                messagebox.showinfo("Success", 
                    f"Charges added to Bill ID {bill_id} successfully!\n"
                    f"Additional Charges: ₹{additional_total:.2f}\n"
                    f"New Total: ₹{new_total:.2f}")
                
                charges_window.destroy()
                show_table()  # Refresh the main table
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Error adding charges to bill: {str(e)}")
        
        def clear_all_charges():
            """Clear all charge entries"""
            if messagebox.askyesno("Clear All", "Are you sure you want to clear all charges?"):
                # Remove all entries except the first one
                while len(charge_entries) > 1:
                    remove_charge_entry(charge_entries[-1]['frame'])
                
                # Clear the first entry
                if charge_entries:
                    charge_entries[0]['amount'].delete(0, 'end')
                    charge_entries[0]['description'].delete(0, 'end')
        
        # Create initial charge entry
        create_charge_entry(charges_container, 1)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=25, padx=20, fill="x")
        
        # Left side buttons
        left_buttons = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        left_buttons.pack(side="left", fill="x")
        
        # Add More button
        add_more_btn = ctk.CTkButton(left_buttons, 
                                    text="➕ Add More", 
                                    font=ctk.CTkFont(size=14, weight="bold"),
                                    fg_color="#22c55e",
                                    hover_color="#16a34a",
                                    width=140, 
                                    height=50,
                                    corner_radius=12,
                                    command=add_more_charges)
        add_more_btn.pack(side="left", padx=(0, 15))
        
        # Clear All button
        clear_btn = ctk.CTkButton(left_buttons, 
                                 text="🗑️ Clear All", 
                                 font=ctk.CTkFont(size=14, weight="bold"),
                                 fg_color="#f59e0b",
                                 hover_color="#d97706",
                                 width=140, 
                                 height=50,
                                 corner_radius=12,
                                 command=clear_all_charges)
        clear_btn.pack(side="left")
        
        # Right side buttons
        right_buttons = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        right_buttons.pack(side="right")
        
        # Save button
        save_btn = ctk.CTkButton(right_buttons, 
                                text="💾 Save Charges", 
                                font=ctk.CTkFont(size=14, weight="bold"),
                                fg_color="#3b82f6",
                                hover_color="#2563eb",
                                width=160, 
                                height=50,
                                corner_radius=12,
                                command=save_charges)
        save_btn.pack(side="right", padx=(15, 0))
        
        # Close button
        close_btn = ctk.CTkButton(right_buttons, 
                                 text="❌ Close", 
                                 font=ctk.CTkFont(size=14, weight="bold"),
                                 fg_color="#6b7280",
                                 hover_color="#4b5563",
                                 width=120, 
                                 height=50,
                                 corner_radius=12,
                                 command=charges_window.destroy)
        close_btn.pack(side="right")
        
        # Instructions
        instructions_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#f8fafc")
        instructions_frame.pack(pady=(10, 20), padx=20, fill="x")
        
        instructions = ctk.CTkLabel(instructions_frame, 
                                   text="💡 Instructions:\n• Enter amount and description for each charge\n• Click 'Add More' to add additional charges\n• Use 'Remove' to delete individual charges\n• Click 'Save Charges' when done",
                                   font=ctk.CTkFont(size=12),
                                   text_color="#64748b",
                                   justify="left")
        instructions.pack(pady=15, padx=20)
        
        # Focus on first amount entry
        if charge_entries:
            charge_entries[0]['amount'].focus()
    
    # Start the process by asking for bill ID
    get_bill_id()

def total_bills():
    cursor1.execute("""
    SELECT COALESCE(SUM(total_amount), 0) AS total_today
    FROM billing
    WHERE DATE(created_at) = CURDATE()
""")
    day_total = cursor1.fetchone()[0]

    cursor1.execute("""
    SELECT SUM(total_amount) AS total_this_week_so_far
    FROM billing
    WHERE DATE(created_at) BETWEEN DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY)
                              AND CURDATE()
""")
    w_total = cursor1.fetchone()[0]
    cursor1.execute("""SELECT SUM(total_amount) AS total_this_month_so_far
                        FROM billing
                        WHERE DATE(created_at) BETWEEN DATE_FORMAT(CURDATE(), '%Y-%m-01') AND CURDATE();
                        """)
    m_total = cursor1.fetchone()[0]

    daily_total = ctk.CTkLabel(main_frame, text=f"Today's total - {day_total} ₹", 
                              fg_color=mbc, text_color='white', 
                              font=('arial', 18), width=300, height=60, 
                              corner_radius=100)
    daily_total.place(x=15, y=115)
    
    week_total = ctk.CTkLabel(main_frame, text=f"Week's total - {w_total} ₹", 
                             fg_color=mbc, text_color='white', 
                             font=('arial', 18), width=300, height=60, 
                             corner_radius=100)
    week_total.pack(padx=5, pady=1)
    
    month_total = ctk.CTkLabel(main_frame, text=f"Monthly's total - {m_total} ₹", 
                              fg_color=mbc, text_color='white', 
                              font=('arial', 18), width=300, height=60, 
                              corner_radius=100)
    month_total.place(x=screen_width-350, y=115)



def mark_paid():
    """Function to mark bill as paid/unpaid - asks for bill ID and toggles payment status"""
    
    def get_bill_id():
        """Function to get bill_id from user before checking status"""
        bill_id_window = ctk.CTkToplevel()
        bill_id_window.title("Mark Bill Payment Status")
        bill_id_window.geometry("500x400")
        bill_id_window.grab_set()
        bill_id_window.resizable(False, False)
        
        # Center the window
        bill_id_window.transient()
        bill_id_window.focus()
        
        # Configure appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Title
        title_label = ctk.CTkLabel(bill_id_window, 
                                  text="Update Payment Status", 
                                  font=ctk.CTkFont(size=22, weight="bold"),
                                  text_color="#1f2937")
        title_label.pack(pady=(30, 20))
        
        # Icon and instructions frame
        instructions_frame = ctk.CTkFrame(bill_id_window, corner_radius=15, fg_color="#f0f9ff")
        instructions_frame.pack(pady=(0, 25), padx=40, fill="x")
        
        # Instructions
        instructions = ctk.CTkLabel(instructions_frame, 
                                   text="💳 Enter the Bill ID to update payment status\nThe system will check current status and allow you to toggle it",
                                   font=ctk.CTkFont(size=14),
                                   text_color="#0369a1",
                                   justify="center")
        instructions.pack(pady=20)
        
        # Bill ID input section
        input_section = ctk.CTkFrame(bill_id_window, fg_color="transparent")
        input_section.pack(pady=20)
        
        bill_id_label = ctk.CTkLabel(input_section, 
                                    text="Bill ID:",
                                    font=ctk.CTkFont(size=16, weight="bold"),
                                    text_color="#374151")
        bill_id_label.pack(pady=(0, 10))
        
        bill_id_entry = ctk.CTkEntry(input_section, 
                                    font=ctk.CTkFont(size=18), 
                                    width=220, 
                                    height=45,
                                    justify='center',
                                    placeholder_text="Enter Bill ID",
                                    corner_radius=12)
        bill_id_entry.pack()
        bill_id_entry.focus()
        
        # Buttons frame
        button_frame = ctk.CTkFrame(bill_id_window, fg_color="transparent")
        button_frame.pack(pady=35)
        
        def check_bill_status():
            """Check bill status and proceed accordingly"""
            try:
                bill_id = int(bill_id_entry.get().strip())
                if bill_id <= 0:
                    messagebox.showerror("Invalid Input", "Please enter a valid Bill ID (positive number)")
                    return
                
                # Check if bill exists and get current status
                try:
                    db = databaseconnectivity()
                    cursor = db.cursor()
                    cursor.execute("SELECT bill_id, total_amount, payment_status FROM billing WHERE bill_id = %s", (bill_id,))
                    bill_data = cursor.fetchone()
                    db.close()
                    
                    if not bill_data:
                        messagebox.showerror("Bill Not Found", f"Bill ID {bill_id} does not exist in the database!")
                        return
                    
                    # Bill exists, close this window and show status confirmation
                    bill_id_window.destroy()
                    current_status = bill_data[2]  # payment_status
                    total_amount = float(bill_data[1]) if bill_data[1] is not None else 0.0
                    show_status_confirmation(bill_id, current_status, total_amount)
                    
                except Exception as e:
                    messagebox.showerror("Database Error", f"Error checking bill: {str(e)}")
                    
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid numeric Bill ID")
        
        def cancel_operation():
            """Close the window without proceeding"""
            bill_id_window.destroy()
        
        # Check Status button
        check_btn = ctk.CTkButton(button_frame, 
                                 text="🔍 Check Status", 
                                 font=ctk.CTkFont(size=16, weight="bold"),
                                 fg_color="#3b82f6",
                                 hover_color="#2563eb",
                                 width=160, 
                                 height=50,
                                 corner_radius=15,
                                 command=check_bill_status)
        check_btn.pack(side="left", padx=(0, 20))
        
        # Cancel button
        cancel_btn = ctk.CTkButton(button_frame, 
                                  text="❌ Cancel", 
                                  font=ctk.CTkFont(size=16, weight="bold"),
                                  fg_color="#6b7280",
                                  hover_color="#4b5563",
                                  width=140, 
                                  height=50,
                                  corner_radius=15,
                                  command=cancel_operation)
        cancel_btn.pack(side="left")
        
        # Bind Enter key to check status
        bill_id_entry.bind('<Return>', lambda e: check_bill_status())
    
    def show_status_confirmation(bill_id, current_status, total_amount):
        """Show current status and ask for confirmation to change"""
        
        # Create confirmation window
        status_window = ctk.CTkToplevel()
        status_window.title(f"Payment Status - Bill ID: {bill_id}")
        status_window.geometry("550x450")
        status_window.resizable(False, False)
        status_window.grab_set()
        
        # Center the window
        status_window.transient()
        status_window.focus()
        
        # Title
        title_label = ctk.CTkLabel(status_window, 
                                  text=f"Bill ID: {bill_id}", 
                                  font=ctk.CTkFont(size=24, weight="bold"),
                                  text_color="#1f2937")
        title_label.pack(pady=(25, 10))
        
        # Bill details frame
        details_frame = ctk.CTkFrame(status_window, corner_radius=15)
        details_frame.pack(pady=(10, 20), padx=40, fill="x")
        
        # Total amount
        amount_label = ctk.CTkLabel(details_frame, 
                                   text=f"Total Amount: ₹{total_amount:.2f}", 
                                   font=ctk.CTkFont(size=18, weight="bold"),
                                   text_color="#374151")
        amount_label.pack(pady=(20, 10))
        
        # Current status display
        status_color = "#22c55e" if current_status == "Paid" else "#ef4444"
        status_icon = "✅" if current_status == "Paid" else "❌"
        
        current_status_frame = ctk.CTkFrame(details_frame, corner_radius=12, fg_color=status_color)
        current_status_frame.pack(pady=(10, 20), padx=20, fill="x")
        
        current_status_label = ctk.CTkLabel(current_status_frame, 
                                           text=f"{status_icon} Current Status: {current_status}", 
                                           font=ctk.CTkFont(size=20, weight="bold"),
                                           text_color="white")
        current_status_label.pack(pady=15)
        
        # Action message based on current status
        if current_status == "Unpaid":
            action_message = "📝 This bill is currently UNPAID.\nWould you like to mark it as PAID?"
            new_status = "Paid"
            action_color = "#22c55e"
            action_icon = "✅"
        else:
            action_message = "⚠️ This bill is already PAID.\nDo you want to mark it as UNPAID?"
            new_status = "Unpaid"
            action_color = "#ef4444"
            action_icon = "❌"
        
        # Action message frame
        message_frame = ctk.CTkFrame(status_window, corner_radius=12, fg_color="#f8fafc")
        message_frame.pack(pady=(0, 25), padx=40, fill="x")
        
        message_label = ctk.CTkLabel(message_frame, 
                                    text=action_message,
                                    font=ctk.CTkFont(size=16),
                                    text_color="#374151",
                                    justify="center")
        message_label.pack(pady=20)
        
        # Buttons frame
        button_frame = ctk.CTkFrame(status_window, fg_color="transparent")
        button_frame.pack(pady=20)
        
        def update_payment_status():
            """Update the payment status in database"""
            try:
                db = databaseconnectivity()
                cursor = db.cursor()
                
                # Update payment status
                cursor.execute("UPDATE billing SET payment_status = %s WHERE bill_id = %s", 
                             (new_status, bill_id))
                
                db.commit()
                db.close()
                
                # Success message
                success_icon = "✅" if new_status == "Paid" else "❌"
                messagebox.showinfo("Status Updated", 
                    f"{success_icon} Payment status updated successfully!\n\n"
                    f"Bill ID: {bill_id}\n"
                    f"Amount: ₹{total_amount:.2f}\n"
                    f"Status: {current_status} → {new_status}")
                
                status_window.destroy()
                # Refresh the main table if it exists
                try:
                    show_table()
                except:
                    pass  # show_table function might not be available
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Error updating payment status: {str(e)}")
        
        def cancel_status_change():
            """Close without making changes"""
            status_window.destroy()
        
        # Confirm button
        confirm_btn = ctk.CTkButton(button_frame, 
                                   text=f"{action_icon} Mark as {new_status}", 
                                   font=ctk.CTkFont(size=16, weight="bold"),
                                   fg_color=action_color,
                                   hover_color=action_color,
                                   width=180, 
                                   height=55,
                                   corner_radius=15,
                                   command=update_payment_status)
        confirm_btn.pack(side="left", padx=(0, 20))
        
        # Cancel button
        cancel_btn = ctk.CTkButton(button_frame, 
                                  text="🚫 Cancel", 
                                  font=ctk.CTkFont(size=16, weight="bold"),
                                  fg_color="#6b7280",
                                  hover_color="#4b5563",
                                  width=140, 
                                  height=55,
                                  corner_radius=15,
                                  command=cancel_status_change)
        cancel_btn.pack(side="left")
        
        # Additional info
        info_frame = ctk.CTkFrame(status_window, corner_radius=10, fg_color="#fef3c7")
        info_frame.pack(pady=(15, 25), padx=40, fill="x")
        
        info_label = ctk.CTkLabel(info_frame, 
                                 text="💡 Note: This action will immediately update the payment status in the database",
                                 font=ctk.CTkFont(size=12),
                                 text_color="#92400e",
                                 justify="center")
        info_label.pack(pady=10)
    
    # Start the process by asking for bill ID
    get_bill_id()
    
# Create main window
paymentwindow = ctk.CTk()
paymentwindow.title("A.K Healthcare")
paymentwindow.configure(fg_color=lbc)

# Get screen dimensions and set window to fullscreen
screen_width = paymentwindow.winfo_screenwidth()
screen_height = paymentwindow.winfo_screenheight()
paymentwindow.geometry(f"{screen_width}x{screen_height}+0+0")

# Main content frame
main_frame = ctk.CTkFrame(paymentwindow, fg_color=lbc)
main_frame.pack(fill='both', expand=True)

# Back Button
back_label = ctk.CTkLabel(main_frame, text="🔙", text_color="black", font=("Calibri", 40), cursor="hand2")
back_label.place(x=5, y=2)
back_label.bind("<Enter>", on_enter) 
back_label.bind("<Leave>", on_leave) 
back_label.bind("<Button-1>", lambda event: close_appointment())

refresh_label = ctk.CTkLabel(main_frame, text="🔄", text_color="Black", font=("Segoe UI", 40), cursor="hand2")
refresh_label.place(x=1440, y=5)
refresh_label.bind("<Enter>", on_refresh_enter)
refresh_label.bind("<Leave>", on_refresh_leave)
refresh_label.bind("<Button-1>", lambda event: show_table())
# Title Label
payment_details = ctk.CTkLabel(main_frame, text="PAYMENT DETAILS", text_color='black', font=('Arial', 18, 'bold'))
payment_details.pack(pady=5)

# Search bar frame
search_frame = ctk.CTkFrame(main_frame, fg_color='white', border_width=2)
search_frame.pack(pady=20, padx=15, fill='x')

search_entry = ctk.CTkEntry(search_frame, font=('Arial', 12), text_color='grey', fg_color='white', border_width=0)
search_entry.pack(side='left', fill='x', expand=True, padx=5, pady=5)
search_entry.insert(0, "SEARCH PATIENT")
search_entry.bind("<FocusIn>", on_entry_click)
search_entry.bind("<FocusOut>", on_focus_out)

search_btn = ctk.CTkButton(search_frame, text="Search", fg_color='white', text_color='black', 
                          font=('Arial', 12, 'bold'), border_width=0, command=search_patient)
search_btn.pack(side='left', padx=5, pady=5)
total_bills()

style = ttk.Style()
style.configure("Treeview", rowheight=40)

# Table frame
table_frame = ctk.CTkFrame(main_frame, fg_color=lbc, width=1500, height=700)
table_frame.place(x=15, y=200)

# Table using Treeview (CustomTkinter doesn't have a built-in table, so we use ttk.Treeview)
headers = ["SR.NO", "NAME", "APPOINTMENT ID", "DATE", "BILL", "STATUS"]
tree = ttk.Treeview(table_frame, columns=headers, show="headings", height=14)

# Set column widths
tree.column("SR.NO", width=50,  anchor="center")
tree.column("NAME", width=150, anchor="center")
tree.column("APPOINTMENT ID", width=100, anchor="center")
tree.column("DATE", width=150, anchor="center")
tree.column("BILL", width=300, anchor="center")
tree.column("STATUS", width=150, anchor="center")

# Set column headings
for col in headers:
    tree.heading(col, text=col)

for header in headers:
    tree.heading(header, text=header)
    tree.column(header, width=312)

tree.tag_configure("white", background="white")
tree.tag_configure(lbc, background=lbc)

tree.pack(fill="both", expand=True)


paid_btn = ctk.CTkButton(main_frame, 
                        text="💰 Payment Status", 
                        fg_color="dark green",  # Blue since it handles both paid/unpaid
                        text_color='white', 
                        hover_color="#2563eb", 
                        font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
                        width=200, 
                        height=50,
                        corner_radius=12,
                        command=mark_paid)
paid_btn.place(x=970,y=screen_height-150)

test_btn = ctk.CTkButton(main_frame, 
                           text="🚑 Paid Patients", 
                        fg_color="blue",  # Blue since it handles both paid/unpaid
                        text_color='white', 
                        hover_color="#2563eb", 
                        font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
                        width=200, 
                        height=50,
                        corner_radius=12,
                        command=show_paid_patients_window)
test_btn.place(x=1250,y=screen_height-150)

# Load initial data
db = databaseconnectivity()
cursor = db.cursor()
sql = """SELECT 
                 b.bill_id,
                    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
                    a.appointment_id,
                    a.appointment_date,
                    b.total_amount,
                    b.payment_status
                FROM billing b
                JOIN appointments a ON b.appointment_id = a.appointment_id
                JOIN patients p ON a.patient_id = p.patient_id
                ORDER BY b.bill_id;"""
cursor.execute(sql)
rows = cursor.fetchall()
sqls = "select sum(total_amount) from billing"
cursor.execute(sqls)
total = cursor.fetchall()
print(total[0][0])
db.close()

for index, row in enumerate(rows):
    tag = mbc if index % 2 == 0 else lbc  # Alternate between colors
    tree.insert("", "end", values=row, tags=(tag,))

tree.insert('', "end", values=(" ", " ", " ", " ", "Total :", total[0][0]), tags=("bold",))
tree.tag_configure("bold", font=('Helvetica ', 18, 'bold'))


    
# Unpaid Patients Button at bottom middle
unpaid_btn = ctk.CTkButton(main_frame, text="💳 Unpaid Patients", 
                          fg_color="red", text_color='white',hover_color=hbc,
                          font=('Arial', 16, 'bold'), 
                          width=200, height=50,
                          corner_radius=10,
                          command=unpaid_patients_action)
unpaid_btn.place(x=680,y=screen_height-150)

drcharges = ctk.CTkButton(main_frame, text="🩺 DR Charges", 
                          fg_color=dbc, text_color='white',hover_color=hbc, 
                          font=('Arial', 16, 'bold'), 
                          width=200, height=50,
                          corner_radius=10,
                          command=dr_charges
                          )
drcharges.place(x=100,y=screen_height-150)

addcharges = ctk.CTkButton(main_frame, text="💲Additional Charges", 
                          fg_color=dbc, text_color='white',hover_color=hbc, 
                          font=('Arial', 16, 'bold'), 
                          width=200, height=50,
                          corner_radius=10,
                          command=additional_charges
                          )
addcharges.place(x=screen_width//2 - 370, y=screen_height - 150)


paymentwindow.mainloop()
