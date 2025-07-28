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


#COLORS 
dbc = "#007BFF"  #007BFF
mbc = "#4EBEFA"
lbc = "#0056b3" #4EBEFA" #0056b3 
hbc = "#1A2750"
tc = "white"
refresh_job = None  # Global variable to store after job ID

conn = pymysql.connect(
            host="localhost", 
            user="root", password="root",
            database="clinic_management"
        )
cursor =conn.cursor()
def Database_Connection():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="clinic_management"
    )
    cursor = conn.cursor()
    return conn
def appointment():
    subprocess.Popen(["python","Clinic_System/raw/appointment.py"])
    
def leavewindowopen():
    subprocess.Popen(["python","Clinic_System/raw/leave_letter.py"])
def medicineswindowsopen():
    subprocess.Popen(["python","Clinic_System/raw/medicines.py"])

def patientswindowsopen():
    subprocess.Popen(["python","Clinic_System/raw/Patient.py"]) 

def paymentwindowsopen():
    subprocess.Popen(["python","Clinic_System/raw/payment.py"])

def profiles():
    subprocess.Popen(["python","Clinic_System/raw/profile.py"])

def loginwindowopen():
    global refresh_job
    if refresh_job is not None:
        refresh_label.after_cancel(refresh_job)
        refresh_job = None
    root.destroy()
    subprocess.Popen(["python", "Clinic_System/raw/signup_login.py"])

def fetch_data():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="root",
            database="clinic_management"
        )
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM patients")
        total_patients = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Appointments")
        total_appointments = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM appointments WHERE DATE(appointment_date) = CURDATE()")
        today_appointments = cursor.fetchone()[0]

        cursor.execute("SELECT medicine_name, stock_quantity FROM medicines LIMIT 16;")
        medicinesdata = cursor.fetchall()

        cursor.execute("""
            SELECT 
                CONCAT(p.first_name, ' ', p.last_name) AS full_name,
                TIMESTAMPDIFF(YEAR, p.dob, CURDATE()) AS age,
                p.blood_group,
                p.contact_number,
                a.appointment_date,
                a.appointment_time,
                a.appointment_type
            FROM appointments a
            JOIN patients p ON p.patient_id = a.patient_id
            WHERE CONCAT(a.appointment_date, ' ', a.appointment_time) = (
                SELECT MIN(CONCAT(appointment_date, ' ', appointment_time))
                FROM appointments
                WHERE (appointment_date > CURRENT_DATE)
                OR (appointment_date = CURRENT_DATE AND appointment_time > CURRENT_TIME)
            )
            LIMIT 1;
        """)
        next_patient = cursor.fetchone()

        conn.close()

        return total_patients, total_appointments, today_appointments, medicinesdata, next_patient

    except Exception as e:
        print("[ERROR in fetch_data]:", e)
        return 0, 0, 0, [], None



np_name = np_age = np_blood = np_phone = np_date = np_time = noap = None
def on_refresh_enter(event):
    refresh_label.configure(text_color=lbc)

def on_refresh_leave(event):
    refresh_label.configure(text_color="#F0F0F0")  # Softer than pure white



def refresh_dash():
    CONN=Database_Connection()
    cursor=CONN.cursor()
    cursor.execute("select is_active from doctor_login where doctor_id = 1")
    is_active = cursor.fetchone()[0]
    print(is_active)
    if is_active == "FALSE":
        root.destroy()
        subprocess.Popen(["python", "Clinic_System/raw/signup_login.py"])
        # messagebox.showwarning("Error", "Your account is deactivated. Please Activate From Login Page.")
        return
    
    with open("profile_data.json", "r") as file:
            profile_datas = json.load(file)
    newimage = ctk.CTkImage(light_image=Image.open(profile_datas["profile_pic"]), size=(150, 110))
    profile_pic.configure(image=newimage)
    global np_name, np_age, np_blood, np_phone, np_date, np_time, noap

    total_patients, total_appointments, today_appointments, _, next_patient = fetch_data()
    print("Fetched:", total_patients, total_appointments, today_appointments)

    ltotal_patients.configure(text=str(total_patients))
    Total_Appointment.configure(text=str(total_appointments))
    today_appointment.configure(text=str(today_appointments))

    refresh_label.configure(text_color="white")

    # --- NEXT PATIENT LOGIC ---
    if next_patient:
        # If "No Appointments" label exists, destroy it
        if noap:
            noap.destroy()
            noap = None

        # If labels don't exist yet, create them
        if not np_name:
            np_name = ctk.CTkLabel(next_patient_frame, text="", text_color="white", font=("calibri", 25))
            np_name.place(x=40, y=70)
        if not np_age:
            np_age = ctk.CTkLabel(next_patient_frame, text="", text_color="white", font=("calibri", 25))
            np_age.place(x=40, y=125)
        if not np_blood:
            np_blood = ctk.CTkLabel(next_patient_frame, text="", text_color="white", font=("calibri", 25))
            np_blood.place(x=40, y=180)
        if not np_phone:
            np_phone = ctk.CTkLabel(next_patient_frame, text="", text_color="white", font=("calibri", 25))
            np_phone.place(x=40, y=235)
        if not np_date:
            np_date = ctk.CTkLabel(next_patient_frame, text="", text_color="white", font=("calibri", 25))
            np_date.place(x=40, y=290)
        if not np_time:
            np_time = ctk.CTkLabel(next_patient_frame, text="", text_color="white", font=("calibri", 25))
            np_time.place(x=40, y=330)

        # Update their texts
        np_name.configure(text=f"Name - {next_patient[0]}")
        np_age.configure(text=f"Age - {next_patient[1]}")
        np_blood.configure(text=f"Blood Group - {next_patient[2]}")
        np_phone.configure(text=f"Phone - {next_patient[3]}")
        np_date.configure(text=f"Appointment Date - {next_patient[4]}")
        np_time.configure(text=f"Appointment Time - {next_patient[5]}")
    
    else:
        # No upcoming appointment: destroy labels if exist
        for var in [np_name, np_age, np_blood, np_phone, np_date, np_time]:
            if var:
                var.destroy()

        np_name = np_age = np_blood = np_phone = np_date = np_time = None

        # Show "No Appointments" label if not already shown
        if not noap:
            noap = ctk.CTkLabel(
                next_patient_frame,
                text="📅 No Upcoming Appointments!\nTake a deep breath and relax 😌",
                text_color=tc,
                font=("Georgia", 25, "bold"),
                justify="center"
            )
            noap.place(x=40, y=170)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.update_idletasks()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.geometry(f"{width}x{height}+0+0")
root.title("A.K Healthcare")
root.configure(fg_color=dbc)  # Correct way to set background color

with open("profile_data.json", "r") as file:
    profile_data = json.load(file)

g_frame = ctk.CTkFrame(root, fg_color=lbc, width=260, height=755,corner_radius=10)
g_frame.place(x=10, y=10)

# Transparent Sidebar
sidebar = ctk.CTkFrame(g_frame, width=260, height=770, fg_color="transparent",corner_radius=10)
sidebar.place(x=0,y=0)
# Load the image using PIL
image = ctk.CTkImage(light_image=Image.open(profile_data["profile_pic"]), size=(150, 110))
# Create a CTkLabel with the image
profile_pic = ctk.CTkLabel(sidebar, image=image, text=None, width=200, height=110)
profile_pic.place(x=10,y=19)

# Doctor Name Label
dr_name = ctk.CTkLabel(sidebar, text=profile_data["name"].upper(), text_color=tc, font=("Helvetica", 25))
dr_name.place(x=40,y=150)

#Dahboard button

# Common style settings
button_width = 180
button_x = 30
start_y = 230
gap = 70
button_radius = 8
button_font = ("Calibri", 25)
shadow_offset = 5

# ✅ Updated function with optional image
def create_shadow_button(parent, text, y, command, image_path=None):
    # Create image object if image path is provided
    image_obj = None
    if image_path:
        img = Image.open(image_path)
        # img = img.resize((24, 24), Image.ANTIALIAS)
        img.resize((24, 24), Image.Resampling.LANCZOS)
        image_obj = ctk.CTkImage(light_image=img, dark_image=img, size=(24, 24))

    # Shadow frame (slightly offset)
    ctk.CTkFrame(parent, fg_color="black", corner_radius=button_radius,
                 width=button_width, height=40).place(x=button_x + shadow_offset, y=y + shadow_offset)

    # Button with optional image
    ctk.CTkButton(parent, text=text, text_color="black", font=button_font,
                  fg_color=mbc, hover_color=hbc, corner_radius=button_radius,
                  width=button_width, height=40, command=command,
                  image=image_obj, compound="left").place(x=button_x, y=y)

# Sidebar buttons with shadows
create_shadow_button(sidebar, "Profile", 230, profiles, "Clinic_System/build/profilebutton.png")
create_shadow_button(sidebar, "Patients", 300, patientswindowsopen, "Clinic_System/build/patientbutton.png")
create_shadow_button(sidebar, "Appointment", 370, appointment, "Clinic_System/build/calendar.png")
create_shadow_button(sidebar, "Payments", 440, paymentwindowsopen, "Clinic_System/build/payment.png")
create_shadow_button(sidebar, "Medicines", 510, medicineswindowsopen, "Clinic_System/build/medicine.png")
create_shadow_button(sidebar, "LeaveLetter", 580, leavewindowopen, "Clinic_System/build/mail.png")
create_shadow_button(sidebar, "Log Out", 695, loginwindowopen, "Clinic_System/build/logout.png")


# Dashboard Layout
header = ctk.CTkLabel(root, text="Dashboard", font=("Algerian", 45), text_color="black")
header.place(x=320, y=10)   

refresh_label = ctk.CTkLabel(root, text="🔄", text_color="white", font=("Calibri", 40), cursor="hand2")
refresh_label.place(x=1420, y=10) 
refresh_label.bind("<Enter>", on_refresh_enter)
refresh_label.bind("<Leave>", on_refresh_leave)
refresh_label.bind("<Button-1>", lambda event: refresh_dash())

total_patients, total_appointments, today_appointments, medicinesdata, next_patient= fetch_data()
# Total Patients
total_patients_label = ctk.CTkFrame(root, fg_color=lbc, width=350, height=200)
total_patients_label.place(x=320, y=78)

pimage_path = r"Clinic_System/build/pp3.png"
p_image = ctk.CTkImage(light_image=Image.open(pimage_path),size=(120,120))
patient_image = ctk.CTkLabel(total_patients_label,image=p_image,text=None,width=130, height=130)
patient_image.place(x=25,y=44)

total_label = ctk.CTkLabel(total_patients_label, text=f"Total Patients", text_color=tc, font=("Georgia", 25))
total_label.place(x=100,y=3)
ltotal_patients = ctk.CTkLabel(total_patients_label, text=f"{total_patients}", text_color=tc, font=("calibri", 45))
ltotal_patients.place(x=170,y=63)

# Today's Patients
Total_Appointments_label = ctk.CTkFrame(root, fg_color=lbc, width=350, height=200)
Total_Appointments_label.place(x=720, y=78)
p1image_path = r"Clinic_System/build/pp.png"
p1image = ctk.CTkImage(light_image=Image.open(p1image_path),size=(120,120))
patient1_image = ctk.CTkLabel(Total_Appointments_label,image=p1image,text="", width=130, height=130)
patient1_image.place(x=25,y=44)
today_label = ctk.CTkLabel(Total_Appointments_label, text=f"Total Appointments", text_color=tc,font=("Georgia", 25))
today_label.place(x=81,y=3)
Total_Appointment = ctk.CTkLabel(Total_Appointments_label, text=f"{total_appointments}", text_color=tc, font=("Georgia", 45))
Total_Appointment.place(x=170,y=63)

# Today's Appointments
today_appointments_label = ctk.CTkFrame(root, fg_color=lbc, width=350, height=200)
today_appointments_label.place(x=1120, y=78)
aimage_path = r"Clinic_System/build/a1.png"
a_image = ctk.CTkImage(light_image=Image.open(aimage_path),size=(150,150))
app_image = ctk.CTkLabel(today_appointments_label,image=a_image,text="", width=130, height=130)
app_image.place(x=20,y=36)
appointment_label = ctk.CTkLabel(today_appointments_label, text=f"Today's Appointments", text_color=tc,font=("Georgia", 25))
appointment_label.place(x=70,y=3)
today_appointment = ctk.CTkLabel(today_appointments_label, text=f"{today_appointments}", text_color=tc, font=("Georgia", 45))
today_appointment.place(x=170,y=63)

# Pie Chart
pielabel = ctk.CTkFrame(root, fg_color=lbc, width=600, height=460)
pielabel.place(x=320, y=305)
pitxt = ctk.CTkLabel(pielabel, text=f"Total Medicine Stocks", text_color=tc,font=("Georgia", 25))
pitxt.place(x=190,y=15)
fig, ax = plt.subplots(figsize=(6,4.5))
ax.pie([item[1] for item in medicinesdata], labels=[item[0] for item in medicinesdata], colors = ["gray", "blue", "red", "orange", "green",
          "yellow", "purple", "pink", "cyan", "magenta",
          "teal", "brown", "black", "white", "gold"]
, autopct='%1.1f%%')
canvas = FigureCanvasTkAgg(fig, master=pielabel)
canvas.get_tk_widget().place(x=80, y=65)

# Next Patient Details
next_patient_frame = ctk.CTkFrame(root, fg_color=lbc, width=500, height=460)
next_patient_frame.place(x=970, y=305)

if next_patient:
    next_patient_label = ctk.CTkLabel(next_patient_frame, text="Next Appointment", text_color=tc, font=("Georgia", 30))
    next_patient_label.place(x=115,y=5)
    np_name = ctk.CTkLabel(next_patient_frame,text=f"Name - {next_patient[0]}", text_color=tc, font=("calibri",25))
    np_name.place(x=40,y=70)
    np_age = ctk.CTkLabel(next_patient_frame,text=f"Age - {next_patient[1]}", text_color=tc, font=("calibri",25))
    np_age.place(x=40,y=125)
    np_blood = ctk.CTkLabel(next_patient_frame,text=f"Blood Group - {next_patient[2]}", text_color=tc, font=("calibri",25))
    np_blood.place(x=40,y=180)
    np_phone = ctk.CTkLabel(next_patient_frame,text=f"Phone - {next_patient[3]}", text_color=tc, font=("calibri",25))
    np_phone.place(x=40,y=235)
    np_date = ctk.CTkLabel(next_patient_frame,text=f"Appointment Date - {next_patient[4]}", text_color=tc, font=("calibri",25))
    np_date.place(x=40,y=290)
    np_time = ctk.CTkLabel(next_patient_frame,text=f"Appointment Time - {next_patient[5]}", text_color=tc, font=("calibri",25))
    np_time.place(x=40,y=330)
else:
    noap = ctk.CTkLabel(next_patient_frame,text="📅 No Upcoming Appointments!\nTake a deep breath and relax 😌",text_color=tc,font=("Georgia", 25, "bold"),justify="center")
    noap.place(x=40, y=170)

    
refresh_dash()  
root.mainloop()

