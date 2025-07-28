import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from PIL import Image as I
from tkinter import *
from tkinter import ttk, messagebox
import re
import subprocess
import tkinter as tk
from PIL import Image,ImageTk
import pymysql
from datetime import datetime
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib import colors
from tkinter import filedialog
from reportlab.lib.utils import ImageReader
import json
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string

#COLORS 
dbc = "#007BFF"  #007BFF
mbc = "#4EBEFA"
lbc = "#0056b3" #4EBEFA" #0056b3 
hbc = "#1A2750"

# EMAIL CONFIGURATION
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_ADDRESS = "karanyad9072@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "lwwx vdgp smbf eeks"    # Replace with your app password

# Store OTPs temporarily
otp_storage = {}

# DATABASE CONNECTIVITY
def Database_Connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="clinic_management"
    )

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp, user_type,username):
    """Send OTP via email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = email
        msg['Subject'] = f"Password Reset OTP - CLINICLOUD"
        
        body = f"""
        Dear User,
        Username : {username}
        Your OTP for password reset is: {otp}
        
        This OTP will expire in 10 minutes.
        
        If you didn't request this password reset, please ignore this email.
        
        Best regards,
        CLINICLOUD Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, email, text)
        server.quit()
        
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send OTP: {str(e)}")
        return False

def doctor_change_password_window():
    """Doctor change password window with OTP verification"""
    def send_otp():
        email = doctor_email_entry.get().strip()
        if not email:
            messagebox.showerror("Error", "Please enter email address")
            return
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            messagebox.showerror("Error", "Please enter a valid email address")
            return
        
        # Check if email exists in doctor_login table
        mydb = Database_Connection()
        mycursor = mydb.cursor()
        
        try:
            mycursor.execute("SELECT username FROM doctor_login WHERE email=%s", (email,))
            drusername = mycursor.fetchone()
            
            if not drusername:
                messagebox.showerror("Error", "Email address not found in our records")
                return
            
            # Generate and send OTP
            otp = generate_otp()
            if send_otp_email(email, otp, "doctor",drusername[0]):
                otp_storage[email] = otp
                messagebox.showinfo("Success", "OTP sent to your email address")
                
                # Enable OTP entry and verify button
                doctor_otp_entry.configure(state="normal")
                verify_otp_btn.configure(state="normal")
                send_otp_btn.configure(state="disabled")
                
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")
        finally:
            mycursor.close()
            mydb.close()
    
    def verify_otp():
        email = doctor_email_entry.get().strip()
        entered_otp = doctor_otp_entry.get().strip()
        
        if not entered_otp:
            messagebox.showerror("Error", "Please enter OTP")
            return
        
        if email in otp_storage and otp_storage[email] == entered_otp:
            messagebox.showinfo("Success", "OTP verified successfully")
            
            # Enable password fields
            doctor_new_password_entry.configure(state="normal")
            doctor_confirm_password_entry.configure(state="normal")
            change_password_btn.configure(state="normal")
            
            # Disable OTP fields
            doctor_otp_entry.configure(state="disabled")
            verify_otp_btn.configure(state="disabled")
            
        else:
            messagebox.showerror("Error", "Invalid OTP")
    
    def change_password():
        email = doctor_email_entry.get().strip()
        new_password = doctor_new_password_entry.get().strip()
        confirm_password = doctor_confirm_password_entry.get().strip()
        
        if not new_password or not confirm_password:
            messagebox.showerror("Error", "Please fill all password fields")
            return
        
        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        # Validate password strength
        password_re = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$&\-#])[A-Za-z\d@$&\-#]{6,}$")
        if not password_re.match(new_password):
            messagebox.showerror("Error", "Password must be at least 6 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character")
            return
        
        # Update password in database
        mydb = Database_Connection()
        mycursor = mydb.cursor()
        
        try:
            mycursor.execute("UPDATE doctor_login SET password=%s WHERE email=%s", (new_password, email))
            mydb.commit()
            
            # Clear OTP from storage
            if email in otp_storage:
                del otp_storage[email]
            
            messagebox.showinfo("Success", "Password changed successfully")
            doctor_change_pass_win.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to change password: {str(e)}")
        finally:
            mycursor.close()
            mydb.close()
    
    doctor_change_pass_win = ctk.CTkToplevel()
    doctor_change_pass_win.geometry("600x700+700+200")
    doctor_change_pass_win.title("Doctor - Change Password")
    doctor_change_pass_win.transient(root)
    doctor_change_pass_win.grab_set()
    doctor_change_pass_win.configure(fg_color=lbc)
    
    ctk.CTkLabel(doctor_change_pass_win, text="Change Password", font=("Arial", 24, "bold")).pack(pady=20)
    
    # Email Entry
    ctk.CTkLabel(doctor_change_pass_win, text="Email Address:").pack(pady=(10, 0))
    doctor_email_entry = ctk.CTkEntry(doctor_change_pass_win, width=400, height=40, placeholder_text="Enter registered email")
    doctor_email_entry.pack(pady=10)
    
    send_otp_btn = ctk.CTkButton(doctor_change_pass_win, text="Send OTP", width=200, command=send_otp)
    send_otp_btn.pack(pady=10)
    
    # OTP Entry
    ctk.CTkLabel(doctor_change_pass_win, text="Enter OTP:").pack(pady=(10, 0))
    doctor_otp_entry = ctk.CTkEntry(doctor_change_pass_win, width=400, height=40, placeholder_text="Enter 6-digit OTP", state="disabled")
    doctor_otp_entry.pack(pady=10)
    
    verify_otp_btn = ctk.CTkButton(doctor_change_pass_win, text="Verify OTP", width=200, command=verify_otp, state="disabled")
    verify_otp_btn.pack(pady=10)
    
    # New Password Entry
    ctk.CTkLabel(doctor_change_pass_win, text="New Password:").pack(pady=(10, 0))
    doctor_new_password_entry = ctk.CTkEntry(doctor_change_pass_win, width=400, height=40, show="*", placeholder_text="Enter new password", state="disabled")
    doctor_new_password_entry.pack(pady=10)
    
    DRNEWppassword_toggle_btn = ctk.CTkButton(doctor_new_password_entry, text="", image=show_icon_img, width=30, height=30, 
                                    fg_color="transparent", hover_color="white",
                                    command=lambda: toggle_password(doctor_new_password_entry, DRNEWppassword_toggle_btn))
    DRNEWppassword_toggle_btn.place(relx=1.0, rely=0.5, anchor="e", x=-2)  # Align inside the entry field
    # Confirm Password Entry
    ctk.CTkLabel(doctor_change_pass_win, text="Confirm Password:").pack(pady=(10, 0))
    doctor_confirm_password_entry = ctk.CTkEntry(doctor_change_pass_win, width=400, height=40, show="*", placeholder_text="Confirm new password", state="disabled")
    doctor_confirm_password_entry.pack(pady=10)

    DRNEWCONppassword_toggle_btn = ctk.CTkButton(doctor_confirm_password_entry, text="", image=show_icon_img, width=30, height=30, 
                                    fg_color="transparent", hover_color="white",
                                    command=lambda: toggle_password(doctor_confirm_password_entry, DRNEWCONppassword_toggle_btn))
    DRNEWCONppassword_toggle_btn.place(relx=1.0, rely=0.5, anchor="e", x=-2)  # Align inside the entry field

    change_password_btn = ctk.CTkButton(doctor_change_pass_win, text="Change Password", width=200, command=change_password, state="disabled")
    change_password_btn.pack(pady=20)

def patient_change_password_window():
    """Patient change password window with OTP verification"""
    def send_otp():
        email = patient_email_entry.get().strip()
        if not email:
            messagebox.showerror("Error", "Please enter email address")
            return
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            messagebox.showerror("Error", "Please enter a valid email address")
            return
        
        # Check if email exists in patients table (assuming patients have email field)
        mydb = Database_Connection()
        mycursor = mydb.cursor()
        
        try:
            # Check if email exists in users table (joined with patients)
            mycursor.execute("SELECT u.username FROM users u JOIN patients p ON u.user_id = p.userid WHERE p.email=%s", (email,))
            p_username = mycursor.fetchone()
            
            if not p_username:
                messagebox.showerror("Error", "Email address not found in our records")
                return
            
            # Generate and send OTP
            otp = generate_otp()
            if send_otp_email(email, otp, "patient",p_username):
                otp_storage[email] = otp
                messagebox.showinfo("Success", "OTP sent to your email address")
                
                # Enable OTP entry and verify button
                patient_otp_entry.configure(state="normal")
                verify_otp_btn.configure(state="normal")
                send_otp_btn.configure(state="disabled")
                
        except Exception as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")
        finally:
            mycursor.close()
            mydb.close()
    
    def verify_otp():
        email = patient_email_entry.get().strip()
        entered_otp = patient_otp_entry.get().strip()
        
        if not entered_otp:
            messagebox.showerror("Error", "Please enter OTP")
            return
        
        if email in otp_storage and otp_storage[email] == entered_otp:
            messagebox.showinfo("Success", "OTP verified successfully")
            
            # Enable password fields
            patient_new_password_entry.configure(state="normal")
            patient_confirm_password_entry.configure(state="normal")
            change_password_btn.configure(state="normal")
            
            # Disable OTP fields
            patient_otp_entry.configure(state="disabled")
            verify_otp_btn.configure(state="disabled")
            
        else:
            messagebox.showerror("Error", "Invalid OTP")
    
    def change_password():
        email = patient_email_entry.get().strip()
        new_password = patient_new_password_entry.get().strip()
        confirm_password = patient_confirm_password_entry.get().strip()
        
        if not new_password or not confirm_password:
            messagebox.showerror("Error", "Please fill all password fields")
            return
        
        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        # Validate password strength
        password_re = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$&\-#])[A-Za-z\d@$&\-#]{6,}$")
        if not password_re.match(new_password):
            messagebox.showerror("Error", "Password must be at least 6 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character")
            return
        
        # Update password in database
        mydb = Database_Connection()
        mycursor = mydb.cursor()
        
        try:
            # Update password in users table for the patient
            mycursor.execute("""
                UPDATE users u 
                JOIN patients p ON u.user_id = p.userid 
                SET u.password = %s 
                WHERE p.email = %s
            """, (new_password, email))
            mydb.commit()
            
            # Clear OTP from storage
            if email in otp_storage:
                del otp_storage[email]
            
            messagebox.showinfo("Success", "Password changed successfully")
            patient_change_pass_win.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to change password: {str(e)}")
        finally:
            mycursor.close()
            mydb.close()
    
    patient_change_pass_win = ctk.CTkToplevel()
    patient_change_pass_win.geometry("600x700+700+200")
    patient_change_pass_win.title("Patient - Change Password")
    patient_change_pass_win.transient(root)
    patient_change_pass_win.grab_set()
    patient_change_pass_win.configure(fg_color=lbc)
    
    ctk.CTkLabel(patient_change_pass_win, text="Change Password", font=("Arial", 24, "bold")).pack(pady=20)
    
    # Email Entry
    ctk.CTkLabel(patient_change_pass_win, text="Email Address:").pack(pady=(10, 0))
    patient_email_entry = ctk.CTkEntry(patient_change_pass_win, width=400, height=40, placeholder_text="Enter registered email")
    patient_email_entry.pack(pady=10)
    
    send_otp_btn = ctk.CTkButton(patient_change_pass_win, text="Send OTP", width=200, command=send_otp)
    send_otp_btn.pack(pady=10)
    
    # OTP Entry
    ctk.CTkLabel(patient_change_pass_win, text="Enter OTP:").pack(pady=(10, 0))
    patient_otp_entry = ctk.CTkEntry(patient_change_pass_win, width=400, height=40, placeholder_text="Enter 6-digit OTP", state="disabled")
    patient_otp_entry.pack(pady=10)
    
    verify_otp_btn = ctk.CTkButton(patient_change_pass_win, text="Verify OTP", width=200, command=verify_otp, state="disabled")
    verify_otp_btn.pack(pady=10)
    
    # New Password Entry
    ctk.CTkLabel(patient_change_pass_win, text="New Password:").pack(pady=(10, 0))
    patient_new_password_entry = ctk.CTkEntry(patient_change_pass_win, width=400, height=40, show="*", placeholder_text="Enter new password", state="disabled")
    patient_new_password_entry.pack(pady=10)

    NEWppassword_toggle_btn = ctk.CTkButton(patient_new_password_entry, text="", image=show_icon_img, width=30, height=30, 
                                    fg_color="transparent", hover_color="white",
                                    command=lambda: toggle_password(patient_new_password_entry, NEWppassword_toggle_btn))
    NEWppassword_toggle_btn.place(relx=1.0, rely=0.5, anchor="e", x=-2)  # Align inside the entry field
    
    # Confirm Password Entry
    ctk.CTkLabel(patient_change_pass_win, text="Confirm Password:").pack(pady=(10, 0))
    patient_confirm_password_entry = ctk.CTkEntry(patient_change_pass_win, width=400, height=40, show="*", placeholder_text="Confirm new password", state="disabled")
    patient_confirm_password_entry.pack(pady=10)

    CONNEWppassword_toggle_btn = ctk.CTkButton(patient_confirm_password_entry, text="", image=show_icon_img, width=30, height=30, 
                                    fg_color="transparent", hover_color="white",
                                    command=lambda: toggle_password(patient_confirm_password_entry, CONNEWppassword_toggle_btn))
    CONNEWppassword_toggle_btn.place(relx=1.0, rely=0.5, anchor="e", x=-2)  # Align inside the entry field
    
    change_password_btn = ctk.CTkButton(patient_change_pass_win, text="Change Password", width=200, command=change_password, state="disabled")
    change_password_btn.pack(pady=20)

def open_registration_windows():
    subprocess.Popen([sys.executable,"Clinic_System/raw/registration.py"])

def patient_login_action():
    username = pusername_entry.get().strip()
    password = ppassword_entry.get().strip()

    if not username or not password:
        messagebox.showerror("Error", "Please fill all fields")
        return

    mydb = Database_Connection()
    mycursor = mydb.cursor()

    queries = "select patients.patient_id from patients join users on users.user_id=patients.userid where users.username=%s and users.password=%s;"
    mycursor.execute(queries, (username, password))
    patient_ids = mycursor.fetchall()
    if not patient_ids:
        messagebox.showerror("Error", "Invalid username or password")
        return
    print(patient_ids[0][0])
    query = "SELECT * FROM users WHERE BINARY username=%s AND BINARY password=%s"
    mycursor.execute(query, (username, password))
    result = mycursor.fetchone()
    if result:
        messagebox.showinfo("Success", "Patient login successful")
        subprocess.Popen([sys.executable, "Clinic_System/raw/PATIENT_DASHBOARD.py", str(patient_ids[0][0])])
        pusername_entry.delete(0,END)
        ppassword_entry.delete(0,END)
        mycursor.execute("INSERT INTO patient_login_history (patient_id, login_time) VALUES (%s, NOW())",(patient_ids[0][0],))
        mydb.commit()
        # root.destroy()
        # call patient dashboard here
    else:
        messagebox.showerror("Error", "Invalid credentials")

def show_frames(frames):
    frames.tkraise()

def login_action():
    username = (login_username_entry.get()).strip()
    password = (login_password_entry.get()).strip()
    mydb = Database_Connection()
    if mydb is None:
        return  # Stop if the database connection failed
    mycursor = mydb.cursor()
    
    if username == "":
        messagebox.showerror("Error", "Please enter username")
        return
    elif password == "":
        messagebox.showerror("Error", "Please enter password")
        return   
    else:
        query = "SELECT * FROM doctor_login  WHERE BINARY username=%s AND BINARY password=%s"
        mycursor.execute(query, (username, password))
        myresult = mycursor.fetchall()
        print(myresult)
        if myresult:
            if myresult[0][6]=="FALSE" :
                messagebox.showerror("Error", "Your account is Deactive")
                if messagebox.askyesno("Activation","Do you want to activate your account"):
                    query = "UPDATE doctor_login SET is_active=%s WHERE username=%s"
                    mycursor.execute(query, ("TRUE", username))
                    mydb.commit()
                    messagebox.showinfo("Success", "Your account is activated")
            elif myresult:
                messagebox.showinfo("Success", "Login Successful") 
                subprocess.Popen([sys.executable, "Clinic_System/raw/dash.py"])
                login_username_entry.delete(0,END)
                login_password_entry.delete(0,END)
                root.destroy()
        else:
            messagebox.showerror("Error", "Invalid username or password")
            return        
def signup_action():
    username=(username_entry.get()).strip()
    password=(password_entry.get()).strip()
    confirm_password_=confirm_password_entry.get()
    
    password_re = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$&\-#])[A-Za-z\d@$&\-#]{6,}$")
    mydb=Database_Connection()
    mycursor = mydb.cursor()
    
    if username=="":
        messagebox.showerror("Error", "Please enter username")
        return
    elif password=="":
        messagebox.showerror("Error", "Please enter password")
        return
    elif confirm_password_=="":
        messagebox.showerror("Error", "Please enter confirm password")
        return
    elif password!=confirm_password_:
        messagebox.showerror("Error", "Passwords do not match")
        return
    elif not password_re.match(password):
        messagebox.showerror("Error", "Password must be at least 6 characters long and contain atleast one uppercase letter, one lowercase letter, one digit, and one special character")
        return
    else:
        try:
            query = "Select * from doctor_login;"
            mycursor.execute(query)
            myresult = mycursor.fetchall()
            if myresult:
                username_entry.delete(0,END)
                password_entry.delete(0,END)
                confirm_password_entry.delete(0,END)
                messagebox.showerror("Already Exist","In CLINICLOUD There is already Dr. ")
                return
            else:
                query = "INSERT INTO doctor_login  (username, password) VALUES (%s, %s)"
                val = (username, password)
                mycursor.execute(query, val)
                mydb.commit()
                mycursor.execute("select doctor_id from doctor_login where username = %s", (username,))
                myresult = mycursor.fetchall()
                messagebox.showinfo("Success", "Account created successfully/n Your Doctor ID is: "+str(myresult[0][0]))
                show_frames(DR_login_frame)
                username_entry.delete(0,END)
                password_entry.delete(0,END)
                confirm_password_entry.delete(0,END)
        except pymysql.IntegrityError :
            messagebox.showerror("Error","Username already exists. Please choose another.")
            return
    mycursor.close()

def toggle_password(entry, button):
    if entry.cget("show") == "*":
        entry.configure(show="")  # Show password
        button.configure(image=hide_icon_img)  # Change to "hide" icon
    else:
        entry.configure(show="*")  # Hide password
        button.configure(image=show_icon_img)
    
# Configure the main window
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
root = ctk.CTk()
root.update_idletasks()  # Ensure correct rendering
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.geometry(f"{width}x{height}+0+0")  # Set to full screen dimensions
root.title("CLINICLOUD")
root.configure(bg=dbc)  # Light green background

container = ctk.CTkFrame(root,width=1600, height=1200)
container.place(x=0, y=0)  # Full screen

# FRAMES
DR_login_frame = ctk.CTkFrame(container, fg_color=lbc)
DR_login_frame.place(x=0, y=0, relwidth=1, relheight=1)
DR_signup_frame = ctk.CTkFrame(container, bg_color=dbc) #A8F0A4, 
PATIENT_SIGNIN = ctk.CTkFrame(container, fg_color=dbc)


for frame in (DR_login_frame, DR_signup_frame,PATIENT_SIGNIN):
    frame.place(x=0, y=0, relwidth=1, relheight=1)  # Ensure proper frame placement

PATIENT_SIGNIN.tkraise()

# Load images correctly using CTkImage
show_icon_img = ctk.CTkImage(light_image=Image.open(r"Clinic_System/build/OPEN-eye-icon.jpg"), size=(20, 30))
hide_icon_img = ctk.CTkImage(light_image=Image.open(r"Clinic_System/build/CLOSED-EYE-ICON.jpg"), size=(20, 20))

# Left Green Panel
left_frame = ctk.CTkFrame(DR_signup_frame, width=850, height=800, fg_color=dbc)  # DARK GREEN 23BC3A,3FA448 , 1EA332
left_frame.place(x=0, y=0)

# CLINICLOUD Title
title_label = ctk.CTkLabel(left_frame, text="CLINI", font=("Times New Roman", 60, "bold"), text_color="white")
title_label.place(x=10, y=10)
subtitle_label = ctk.CTkLabel(left_frame, text="CLOUD – Doctor Portal", font=("Times New Roman", 22, "bold"), text_color="white")
subtitle_label.place(x=10, y=75)

# Welcome Text
welcome_label = ctk.CTkLabel(left_frame, text="Welcome !!", font=("Algerian", 70), text_color="white")
welcome_label.place(x=125, y=200)

slogan_label = ctk.CTkLabel(left_frame, text="Compassion, Care, and Commitment - Healing Hands,\nCaring Hearts.",
                            font=("Calibri", 20), text_color="white", wraplength=500)
slogan_label.place(x=105, y=285)

already_user_label = ctk.CTkLabel(left_frame, text="Already a user ?", font=("Alibri", 24), text_color="white")
already_user_label.place(x=225, y=450)

# Log In Button
login_button = ctk.CTkButton(left_frame, text="Log In", font=("Arial", 18), fg_color="white",
                             command=lambda: show_frames(DR_login_frame),
                             text_color="black", hover_color="#C0C0C0", width=130, height=45, corner_radius=0)
login_button.place(x=240, y=500)

# Right Panel
right_frame = ctk.CTkFrame(DR_signup_frame, width=1100, height=900, fg_color=lbc) #C8F7C5
right_frame.place(x=650, y=0)

create_account_label = ctk.CTkLabel(right_frame, text="Register as Doctor",
                                    font=("Algerian", 36), text_color="white")
create_account_label.place(x=50, y=150)

# Entry Fields
username_label = ctk.CTkLabel(right_frame, text="Username", font=("EB Garamond", 23), text_color="white")
username_label.place(x=50, y=220)
username_entry = ctk.CTkEntry(right_frame, width=450, height=45, corner_radius=0,placeholder_text="Enter UserName")
username_entry.place(x=50, y=260)
# Password Entry
password_label = ctk.CTkLabel(right_frame, text="Password", font=("EB Garamond", 23), text_color="white")
password_label.place(x=50, y=320)
password_entry = ctk.CTkEntry(right_frame, width=450, height=45, show="*", corner_radius=0,placeholder_text="Enter Password")
password_entry.place(x=50, y=360)

# Password Toggle Button (inside entry box)
password_toggle_btn = ctk.CTkButton(password_entry, text="", image=show_icon_img, width=30, height=30, 
                                    fg_color="transparent", hover_color="white",
                                    command=lambda: toggle_password(password_entry, password_toggle_btn))
password_toggle_btn.place(relx=1.0, rely=0.5, anchor="e", x=-2)  # Align inside the entry field

# Confirm Password Entry
confirm_password_label = ctk.CTkLabel(right_frame, text="Confirm Password", font=("EB Garamond", 23), text_color="white")
confirm_password_label.place(x=50, y=420)
confirm_password_entry = ctk.CTkEntry(right_frame, width=450, height=45, show="*", corner_radius=0,placeholder_text="Confirm Password")
confirm_password_entry.place(x=50, y=460)

# Confirm Password Toggle Button (inside entry box)
confirm_password_toggle_btn = ctk.CTkButton(confirm_password_entry, text="", image=show_icon_img, width=30, height=30, 
                                            fg_color="transparent", hover_color="white",
                                            command=lambda: toggle_password(confirm_password_entry, confirm_password_toggle_btn))
confirm_password_toggle_btn.place(relx=1.0, rely=0.5, anchor="e", x=-2)  # Align inside the entry field


# Submit Button
signup_button = ctk.CTkButton(right_frame, text="Sign Up", font=("Arial", 18), fg_color= dbc, #136B0B,226622
                              hover_color=hbc, width=450, height=50, corner_radius=0, border_color="#154360",command=signup_action)
signup_button.place(x=50, y=530)

# ICON
icon = Image.open(r"Clinic_System/build/google.png")  
icon = icon.resize((32, 32))  # Resize if needed
icon_ctk = ctk.CTkImage(dark_image=icon, size=(32, 32))

# style line
styleline = ctk.CTkLabel(right_frame, text="---------------------------------------------------------------------------------", 
text_color="black",font=("Arial", 18 , "bold"), fg_color= lbc, #136B0B,226622 
                         width=150, height=30, corner_radius=0)
styleline.place(x=50, y=570)

# Patient Button
Patient_button = ctk.CTkButton(right_frame, text="Patient Portal", font=("Arial",16), fg_color= dbc, #136B0B,226622
                              hover_color=hbc, width=150, height=25, corner_radius=0, border_color="#154360",command=lambda:show_frames(PATIENT_SIGNIN))
Patient_button.place(x=195, y=610)

# LOGIN FRAME UI
green_frame = ctk.CTkFrame(DR_login_frame, width=800, height=500, fg_color=mbc, corner_radius=50) # DARK GREEN 54BA4C,1EA332
green_frame.place(x=600 , y=200) 

inner_frame = ctk.CTkFrame(green_frame, fg_color="transparent")
inner_frame.pack(padx=30, pady=30, fill="both", expand=True)  # Adds space inside

ltitle = ctk.CTkLabel(inner_frame, text="Log in",text_color="white", font=("Calibri",22 , "bold"))
ltitle.pack(padx=5)
# Username Entry
login_username_entry = ctk.CTkEntry(inner_frame, width=300, height=45, placeholder_text="Username or Email Address")
login_username_entry.pack(pady=10)

# Password Entry
login_password_entry = ctk.CTkEntry(inner_frame, width=300, height=45, show="*", placeholder_text="Password")
login_password_entry.pack(pady=10)

# Password Toggle Button (inside entry box)
login_password_toggle_btn = ctk.CTkButton(login_password_entry, text="", image=show_icon_img, width=30, height=30, 
                                    fg_color="transparent", hover_color="white",
                                    command=lambda: toggle_password(login_password_entry,login_password_toggle_btn))
login_password_toggle_btn.place(relx=1.0, rely=0.5, anchor="e", x=-2)  # Align inside the entry field

# Sign In Button
sign_in_button = ctk.CTkButton(inner_frame, text="Sign In", width=150, height=40,text_color="white",corner_radius=10,command=lambda:login_action(),fg_color=dbc)
sign_in_button.pack(pady=20)

# Change Password Button for Doctor
change_password_doctor_btn = ctk.CTkButton(inner_frame, text="Change Password", width=150, height=30, corner_radius=10,
                                          command=doctor_change_password_window, fg_color="orange", text_color="white")
change_password_doctor_btn.pack(pady=5)

# Back Button
back_button = ctk.CTkButton(inner_frame, text="Go Back", width=100, height=30, corner_radius=10,command=lambda:show_frames(DR_signup_frame),fg_color="white", text_color="black")
back_button.pack(pady=5)

# Password Entry
show_icon = Image.open(r"Clinic_System/build/OPEN-eye-icon.jpg")
hide_icon = Image.open(r"Clinic_System/build/CLOSED-EYE-ICON.jpg")

# Convert images to CTkImage for better scaling on high-DPI displays
show_icon_img = ctk.CTkImage(light_image=show_icon, size=(20, 20))
hide_icon_img = ctk.CTkImage(light_image=hide_icon, size=(20, 20))

# Patient log in----------------------------------------------------------------------------------------------
left_patient_frame = ctk.CTkFrame(PATIENT_SIGNIN, width=850, height=800, fg_color=dbc)  
left_patient_frame.place(x=0, y=0)
right_patient_frame = ctk.CTkFrame(PATIENT_SIGNIN, width=1100, height=900, fg_color=lbc)  
right_patient_frame.place(x=650, y=0)

# CLINICLOUD Title
ptitle_label = ctk.CTkLabel(left_patient_frame, text="CLINI", font=("Times New Roman", 60, "bold"), text_color="white")
ptitle_label.place(x=10, y=10)
psubtitle_label = ctk.CTkLabel(left_patient_frame, text="CLOUD – Patient Portal", font=("Times New Roman", 22, "bold"), text_color="white")
psubtitle_label.place(x=10, y=75)

# Welcome Text
pwelcome_label = ctk.CTkLabel(left_patient_frame, text="Welcome !!", font=("Algerian", 70), text_color="white")
pwelcome_label.place(x=125, y=200)

pslogan_label = ctk.CTkLabel(left_patient_frame, text="Compassion, Care, and Commitment - Healing Hands,\nCaring Hearts.",
                            font=("Calibri", 20), text_color="white", wraplength=500)
pslogan_label.place(x=105, y=285)

palready_user_label = ctk.CTkLabel(left_patient_frame, text="New user ?", font=("Alibri", 24 , "bold"), text_color="white")
palready_user_label.place(x=250, y=450)

# Log In Button
plogin_button = ctk.CTkButton(left_patient_frame, text="Register", font=("Arial", 18), fg_color="white",
                             text_color="black", hover_color="#C0C0C0", width=130, height=45, corner_radius=0,command=open_registration_windows)
plogin_button.place(x=240, y=500)

# Right Panel
right_patient_frame = ctk.CTkFrame(PATIENT_SIGNIN, width=1100, height=900, fg_color=lbc) #C8F7C5
right_patient_frame.place(x=650, y=0)

pcreate_account_label = ctk.CTkLabel(right_patient_frame, text="Patient Login",
                                    font=("Algerian", 36), text_color="white")
pcreate_account_label.place(x=50, y=150)

# Entry Fields
pusername_label = ctk.CTkLabel(right_patient_frame, text="Username", font=("EB Garamond", 23), text_color="white")
pusername_label.place(x=50, y=220)
pusername_entry = ctk.CTkEntry(right_patient_frame, width=450, height=45, corner_radius=0,placeholder_text="Enter UserName")
pusername_entry.place(x=50, y=260)
# Password Entry
ppassword_label = ctk.CTkLabel(right_patient_frame, text="Password", font=("EB Garamond", 23), text_color="white")
ppassword_label.place(x=50, y=320)
ppassword_entry = ctk.CTkEntry(right_patient_frame, width=450, height=45, show="*", corner_radius=0,placeholder_text="Enter Password")
ppassword_entry.place(x=50, y=360)

# Password Toggle Button (inside entry box)
ppassword_toggle_btn = ctk.CTkButton(ppassword_entry, text="", image=show_icon_img, width=30, height=30, 
                                    fg_color="transparent", hover_color="white",
                                    command=lambda: toggle_password(ppassword_entry, ppassword_toggle_btn))
ppassword_toggle_btn.place(relx=1.0, rely=0.5, anchor="e", x=-2)  # Align inside the entry field

# Submit Button
psignup_button = ctk.CTkButton(right_patient_frame, text="Log in", font=("Arial", 18), fg_color= dbc, #136B0B,226622
                              hover_color=hbc, width=200, height=35, corner_radius=20, border_color="#154360",command=patient_login_action)
psignup_button.place(x=50, y=420)



# Change Password Button for Patient
change_password_patient_btn = ctk.CTkButton(right_patient_frame, text="Change Password", font=("Arial", 14), fg_color="orange",
                                           hover_color="darkorange", width=200, height=35, corner_radius=20,
                                           command=patient_change_password_window)
change_password_patient_btn.place(x=270, y=420)

# style line
styleline = ctk.CTkLabel(right_patient_frame, text="---------------------------------------------------------------------------------", 
text_color="black",font=("Arial", 18 , "bold"), fg_color= lbc, #136B0B,226622 
                         width=150, height=30, corner_radius=0)
styleline.place(x=50, y=470)

# Patient Button
Doctor_button = ctk.CTkButton(right_patient_frame, text="Doctor Portal", font=("Arial",16), fg_color= dbc, #136B0B,226622
                              hover_color=hbc, width=150, height=25, corner_radius=0, border_color="#154360" ,command=lambda:show_frames(DR_signup_frame))
Doctor_button.place(x=180, y=510)
root.mainloop()