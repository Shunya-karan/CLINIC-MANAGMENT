import customtkinter as ctk
from tkinter import filedialog, messagebox, Toplevel
from PIL import Image, ImageTk
from customtkinter import CTkImage
import pymysql
from tkcalendar import Calendar
from datetime import datetime
import re
from tkcalendar import DateEntry
from datetime import date, timedelta
import smtplib
from email.mime.text import MIMEText
import random
import string

def generate_secure_password(length=8):
    """Generate a secure random password"""
    characters = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(random.choice(characters) for _ in range(length))

def send_credentials_email(to_email, username, password):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = ""
    sender_password = ""

    subject = "Your Patient Portal Credentials"
    body = f"""
    Dear Patient,

    We are pleased to inform you that your patient portal account has been successfully created.

    Below are your login credentials for accessing the portal:

    Username: {username}
    Password: {password}

    Please keep these credentials secure and do not share them with anyone.
    Important Notes:
    - For security reasons, we recommend changing your password after your first login.
    - If you forget your password, use the "Forgot Password" option on the login page.
    - Your personal data is protected and will not be shared with third parties.

    Thank you for choosing CLINICLOUD. We are committed to providing you with the best care.

    Best regards,
    The CLINICLOUD Team
    """

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

# Configure CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Global variables for form entries
fields = {}

def create_registration_form():
    global registrationwindows
    
    def maximize_window():
        if registrationwindows.winfo_exists():  # Ensure the window still exists
            registrationwindows.state("zoomed")

    ctk.set_appearance_mode("light")  # Set light mode appearance
    ctk.set_default_color_theme("blue")  # Use blue theme
    registrationwindows = ctk.CTk()
    registrationwindows.title("CLINI CLOUD")  # Set window title
    registrationwindows.configure(bg="#294B82")
    registrationwindows.after(100, maximize_window)

    main_frame = ctk.CTkFrame(registrationwindows, fg_color="#007BFF")
    main_frame.pack(fill="both", expand=True)

    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(0, weight=1)

    left_frame = ctk.CTkFrame(main_frame, corner_radius=20, fg_color="#0056b3")
    left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    right_frame = ctk.CTkFrame(main_frame, corner_radius=20, fg_color="white")
    right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    # Left Side
    title_label = ctk.CTkLabel(left_frame, text="CLINI", font=("Times New Roman", 60, "bold"), text_color="white")
    title_label.place(x=10, y=10)
    subtitle_label = ctk.CTkLabel(left_frame, text="CLOUD – Patient Portal", font=("Times New Roman", 22, "bold"), text_color="white")
    subtitle_label.place(x=10, y=75)

    # Welcome Text
    welcome_label = ctk.CTkLabel(left_frame, text="Welcome !!", font=("Algerian", 70), text_color="white")
    welcome_label.place(x=125, y=200)

    slogan_label = ctk.CTkLabel(left_frame, text="Compassion, Care, and Commitment - Healing Hands,\nCaring Hearts.",
                                font=("Calibri", 20), text_color="white", wraplength=500)
    slogan_label.place(x=105, y=285)

    ctk.CTkButton(left_frame, text="Log In", width=200, height=40, fg_color="white", text_color="#0056b3",
                  hover_color="#e6e6e6", command=sign_in).place(relx=0.5, rely=0.75, anchor="center")

    # Right Side
    ctk.CTkLabel(right_frame, text="Patient Registration Form", font=("Arial", 28, "bold"), text_color="#007BFF").pack(pady=(20, 10))

    scrollable_form = ctk.CTkScrollableFrame(right_frame, fg_color="transparent", width=400, height=450)
    scrollable_form.pack(fill="both", expand=True, padx=20, pady=(0, 10))

    # Form fields
    add_entry(scrollable_form, "First Name")
    add_entry(scrollable_form, "Last Name")
    add_combobox(scrollable_form, "Gender", ["Male", "Female", "Other"])
    add_datepicker(scrollable_form, "Date of Birth")
    add_entry(scrollable_form, "Contact Number")
    add_entry(scrollable_form, "Email")
    add_textbox(scrollable_form, "Address")
    add_entry(scrollable_form, "Emergency Contact")
    add_combobox(scrollable_form, "Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
    add_entry(scrollable_form,"Doctor Id")
    fields["ImageLabel"] = ctk.CTkLabel(scrollable_form, text="No Image", text_color="gray")
    fields["ImageLabel"].pack(pady=5)
    
    # Initialize ImagePath to avoid KeyError
    fields["ImagePath"] = ""

    ctk.CTkButton(scrollable_form, text="Upload Profile Image", command=upload_image).pack(pady=5)

    btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
    btn_frame.pack(pady=20)

    ctk.CTkButton(btn_frame, text="Submit", command=submit_form, fg_color="#007BFF",
                  hover_color="#0056b3", width=150, height=40).pack(side="left", padx=10)

    registrationwindows.mainloop()

def add_entry(parent, label_text):
    ctk.CTkLabel(parent, text=label_text + ":", font=("Arial", 16)).pack(pady=(10, 0))
    entry = ctk.CTkEntry(parent, width=300)
    entry.pack(pady=5)
    fields[label_text] = entry

def add_combobox(parent, label_text, values):
    ctk.CTkLabel(parent, text=label_text + ":", font=("Arial", 16)).pack(pady=(10, 0))
    combo = ctk.CTkComboBox(parent, values=values, width=300)
    combo.pack(pady=5)
    fields[label_text] = combo

def add_textbox(parent, label_text):
    ctk.CTkLabel(parent, text=label_text + ":", font=("Arial", 16)).pack(pady=(10, 0))
    textbox = ctk.CTkTextbox(parent, width=300, height=80, fg_color="#C5EAFE")
    textbox.pack(pady=5)
    fields[label_text] = textbox

def add_datepicker(parent, label_text):
    ctk.CTkLabel(parent, text=label_text + ":", font=("Arial", 16)).pack(pady=(10, 0))
    calendar = DateEntry(parent, width=25, font=("Georgia", 17), selectmode="day",
                         date_pattern="yyyy-mm-dd", mindate=date(1900, 1, 1))
    calendar.pack(pady=5)
    fields[label_text] = calendar

def upload_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if file_path:
        fields["ImagePath"] = file_path
        try:
            image = Image.open(file_path).resize((100, 100))
            photo = CTkImage(light_image=image, dark_image=image, size=(100, 100))
            fields["ImageLabel"].configure(image=photo, text="")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")

def validate_form():
    errors = []
    today = datetime.today().date()
    get = lambda k: fields[k].get() if k in fields and hasattr(fields[k], 'get') else ""
    
    conn = None
    cursor = None
    
    try:
        conn = pymysql.connect(
            host="localhost", 
            user="root", 
            password="root", 
            database="clinic_management"
        )
        cursor = conn.cursor()
        
        # Check email uniqueness
        cursor.execute("SELECT email FROM patients WHERE email = %s", (get("Email"),))
        if cursor.fetchone():
            errors.append("Email already exists")
        
        # Check contact number uniqueness
        cursor.execute("SELECT contact_number FROM patients WHERE contact_number = %s", (get("Contact Number"),))
        if cursor.fetchone():
            errors.append("Contact Number already exists")

        cursor.execute("SELECT doctor_id FROM doctor_login")
        doctor_ids = [str(row[0]) for row in cursor.fetchall()]
    except pymysql.Error as e:
        errors.append(f"Database error during validation: {str(e)}")
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    # Field validations
    if not get("First Name").strip():
        errors.append("First Name is required.")
    
    if not get("Last Name").strip():
        errors.append("Last Name is required.")
    
    if not get("Gender"):
        errors.append("Gender is required.")


    doctor_id=get("Doctor Id")
    if not doctor_id:
        errors.append("Doctor Id is required.")
    elif not doctor_id.isdigit():
        errors.append("Invalid Doctor Id")
    elif doctor_id not in doctor_ids:
        errors.append("Invalid Doctor Id")
    
    # Date of Birth validation
    min_age=18
    dob = get("Date of Birth")
    if not dob:
        errors.append("Date of Birth is required.")
    else:
        try:
            dob_date = datetime.strptime(str(dob), "%Y-%m-%d").date()
            if dob_date > today:
                errors.append("Date of Birth cannot be in the future.")
            # Check for reasonable age (e.g., not older than 120 years)
            if (today - dob_date).days > 120 * 365:
                errors.append("Please enter a valid Date of Birth.")
            age = (today - dob_date).days // 365
            if age < min_age:
                errors.append("Patient must be at least 18 years old.")

        except ValueError:
            errors.append("Date of Birth must be in YYYY-MM-DD format.")
    
    # Contact number validation
    contact = get("Contact Number").strip()
    if not contact:
        errors.append("Contact Number is required.")
    elif not contact.isdigit():
        errors.append("Contact Number must contain only digits.")
    elif len(contact) < 10 or len(contact) > 15:
        errors.append("Contact Number must be between 10-15 digits.")
    
    # Email validation - improved regex
    email = get("Email").strip()
    if not email:
        errors.append("Email is required.")
    elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        errors.append("Please enter a valid email address.")
    
    # Address validation
    if not fields["Address"].get("1.0", "end").strip():
        errors.append("Address is required.")
    
    # Emergency contact validation
    emergency_contact = get("Emergency Contact").strip()
    if not emergency_contact:
        errors.append("Emergency Contact is required.")
    elif not emergency_contact.isdigit():
        errors.append("Emergency Contact must contain only digits.")
    elif len(emergency_contact) < 10 or len(emergency_contact) > 15:
        errors.append("Emergency Contact must be between 10-15 digits.")
    
    if not get("Blood Group"):
        errors.append("Blood Group is required.")
    
    return errors

def submit_form():
    errors = validate_form()
    if errors:
        messagebox.showerror("Validation Error", "\n".join(errors))
        return

    conn = None
    cursor = None
    
    try:
        conn = pymysql.connect(
            host="localhost", 
            user="root", 
            password="root", 
            database="clinic_management"
        )
        cursor = conn.cursor()

        # Generate secure credentials
        first_name = fields["First Name"].get().strip()
        last_name = fields["Last Name"].get().strip()
        email = fields["Email"].get().strip()
        
        # Insert patient into patients table first to get patient_id
        cursor.execute("""
            INSERT INTO patients
            (first_name, last_name, gender, dob, contact_number, email, address,
             emergency_contact, blood_group, image)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            first_name,
            last_name,
            fields["Gender"].get(),
            fields["Date of Birth"].get(),
            fields["Contact Number"].get(),
            email,
            fields["Address"].get("1.0", "end").strip(),
            fields["Emergency Contact"].get(),
            fields["Blood Group"].get(),
            fields["ImagePath"]
        ))
        
        patient_id = cursor.lastrowid
        
        # Generate secure username and password
        username = f"{patient_id}_{first_name}_{last_name}".replace(" ", "")
        password = generate_secure_password()

        # Insert into users table
        cursor.execute("""
            INSERT INTO users (username, password, email) 
            VALUES (%s, %s, %s)
        """, (username, password, email))
        
        user_id = cursor.lastrowid
        
        # Update patients table with user_id
        cursor.execute("""
            UPDATE patients SET userid = %s WHERE patient_id = %s
        """, (user_id, patient_id))
        
        # Commit all changes
        conn.commit()
        
        # Try to send email
        email_sent = send_credentials_email(email, username, password)
        
        success_msg = f"Patient registered successfully!\nUsername: {username}\nPassword: {password}"
        if not email_sent:
            success_msg += "\n\nNote: Email could not be sent. Please note down the credentials."
        
        messagebox.showinfo("Success", success_msg)
        clear_form()
        registrationwindows.destroy()

    except pymysql.Error as err:
        if conn:
            conn.rollback()
        messagebox.showerror("Database Error", f"Registration failed: {str(err)}")
        
    except Exception as e:
        if conn:
            conn.rollback()
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def clear_form():
    """Clear all form fields"""
    for key, widget in fields.items():
        if key == "ImageLabel":
            widget.configure(image=None, text="No Image")
        elif key == "ImagePath":
            fields[key] = ""
        elif isinstance(widget, ctk.CTkEntry):
            widget.delete(0, "end")
        elif isinstance(widget, ctk.CTkTextbox):
            widget.delete("1.0", "end")
        elif isinstance(widget, ctk.CTkComboBox):
            widget.set("")
        elif isinstance(widget, DateEntry):
            widget.set_date(date.today())

def sign_in():
    """Close registration window and return to login"""
    try:
        registrationwindows.destroy()
    except:
        pass

# Start the app
if __name__ == "__main__":

    create_registration_form()
