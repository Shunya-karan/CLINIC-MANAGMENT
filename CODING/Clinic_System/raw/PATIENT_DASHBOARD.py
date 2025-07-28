import customtkinter as ctk
from tkinter import filedialog
import tkinter.ttk as ttk
from PIL import Image, ImageTk
from tkcalendar import DateEntry
from tkinter import messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from datetime import datetime, date
from tkinter import filedialog, messagebox
import sys
import pymysql
import os
import re
from collections import defaultdict
from customtkinter import CTkImage
import requests
import json

value = sys.argv[1]
# value = 109
# print(value)
dbc = "#007BFF"  #007BFF
mbc = "#4EBEFA"
lbc = "#0056b3" #4EBEFA" #0056b3 
hbc = "#858FB2"
tb = "black"
# Setup appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Main window
app = ctk.CTk()
app.title("AK Healthcare")
app.configure(fg_color=dbc)

screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

app.geometry(f"{screen_width}x{screen_height}+0+0")  

# Fonts
heading_font = ("ALGERIAN", 50)
label_font = ("Georgia", 25)
name_font = ("Georgia", 32, "bold")
button_font = ("Georgia", 20)



profile_image_path = None
profile_image = None  # Global image object

# Welcome texts
ctk.CTkLabel(app, text="CliniCloud", font=("Times New Roman", 50, "bold"), text_color="white", bg_color=dbc).place(x=40, y=20)
ctk.CTkLabel(app, text="Welcome !!", font=heading_font, text_color="white", bg_color=dbc).place(x=40, y=120)

def open_clinic_bot():
    API_KEY = "Bearer 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"  # Add your key here
    MODEL = "deepseek/deepseek-r1:free"
    REFERER = "http://localhost"
    TITLE = "ClinicBot"
    API_URL = "https://openrouter.ai/api/v1/chat/completions"

    # ---------- GUI SETTINGS ----------
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    botwindow = ctk.CTkToplevel()
    botwindow.title("Clinic Cloud - Chatbot Assistant")
    botwindow.geometry("700x600")
    botwindow.resizable(False, False)
    botwindow.configure(fg_color="#356eff")
    botwindow.grab_set()

    # ---------- HEADER ----------
    header_frame = ctk.CTkFrame(botwindow, height=80, fg_color="#112742", corner_radius=0)
    header_frame.pack(fill="x")

    clinic_title = ctk.CTkLabel(header_frame, text="🏥 Clinic Cloud", font=("Georgia", 26, "bold"), text_color="white")
    clinic_title.place(x=20, y=20)

    bot_title = ctk.CTkLabel(header_frame, text="AI Assistant - ClinicBot", font=("Georgia", 16), text_color="white")
    bot_title.place(x=25, y=50)
    logo_pil_image = Image.open("Clinic_System/build/clinic-logo.png").resize((50, 50))
    logo_image = CTkImage(dark_image=logo_pil_image, light_image=logo_pil_image, size=(50, 50))
    logo_label = ctk.CTkLabel(header_frame, image=logo_image, text="")
    logo_label.place(x=620, y=15)


    # ---------- CHAT DISPLAY ----------
    chat_display = ctk.CTkTextbox(botwindow, width=660, height=380, corner_radius=12, font=("Arial", 14), wrap="word")
    chat_display.place(x=20, y=100)
    chat_display.insert("end", "🤖 ClinicBot: Hello! How can I assist you today?\n\n")
    chat_display.configure(state="disabled")

    # ---------- USER INPUT ----------
    user_input = ctk.CTkEntry(botwindow, placeholder_text="Type your message here...", width=520, height=40, font=("Arial", 14))
    user_input.place(x=20, y=500)

    # ---------- SEND FUNCTION ----------
    def send_message():
        message = user_input.get().strip()
        if not message:
            return

        # Show user message
        chat_display.configure(state="normal")
        chat_display.insert("end", f"👤 You: {message}\n")
        chat_display.configure(state="disabled")
        chat_display.see("end")
        user_input.delete(0, "end")

        # Prepare API payload
        headers = {
            "Authorization": API_KEY,
            "Content-Type": "application/json",
            "HTTP-Referer": REFERER,
            "X-Title": TITLE
        }

        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": message}]
        }

        try:
            response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
            result = response.json()

            # Extract response
            if "choices" in result:
                bot_reply = result["choices"][0]["message"]["content"]
            else:
                bot_reply = "❌ Error: No response from OpenRouter."

        except Exception as e:
            bot_reply = f"⚠️ Exception: {str(e)}"

        # Show bot reply
        chat_display.configure(state="normal")
        chat_display.insert("end", f"🤖 ClinicBot: {bot_reply}\n\n")
        chat_display.configure(state="disabled")
        chat_display.see("end")

    # ---------- SEND BUTTON ----------
    send_button = ctk.CTkButton(botwindow, text="Send", width=120, height=40, font=("Arial", 14, "bold"), fg_color="#1C3D64", text_color="white", hover_color="#143250", command=send_message)
    send_button.place(x=560, y=500)

    botwindow.mainloop()

def on_refresh_enter(event):
    refresh_label.configure(text_color="grey")
def on_refresh_leave(event):
    refresh_label.configure(text_color="White")

# 🔄 Refresh icon
refresh_label = ctk.CTkLabel(app, text="🔄", text_color="White", font=("Calibri", 50), cursor="hand2")
refresh_label.place(x=1450, y=10)
refresh_label.bind("<Enter>", on_refresh_enter)
refresh_label.bind("<Leave>", on_refresh_leave)
refresh_label.bind("<Button-1>", lambda event: show_table())

def on_enter(event):
    app.configure(text_color="grey") 

def on_leave(event):
    app.configure(text_color="black")  

def show_table():
    LeaveLetter(value)
    Bills(value)
    Appointments(value)
    Prescriptions(value)
#functions
conn = pymysql.connect(
            host="localhost", 
            user="root", password="root",
            database="clinic_management"
        )
cursor =conn.cursor()
import pymysql
def mysqlconnection():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="clinic_management"
    )
    return conn   # ✅ Return the connection object


def generate_invoice_pdf(bill_data, medicine_list=None, diagnosis=None, signature_path=None, db_connection=None):
    (
        bill_id, appointment_date, fee, status,
        doctor_name, patient_name
    ) = bill_data

    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        initialfile=f"Invoice_{bill_id}.pdf",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not file_path:
        return

    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    # Light blue background
    c.setFillColorRGB(0.88, 0.95, 1)
    c.rect(0, 0, width, height, fill=1)

    # Clinic Logo
    try:
        logo = ImageReader("Clinic_System/build/clinic-logo.png")
        c.drawImage(logo, 40, height - 100, width=80, height=80, mask='auto')
    except:
        pass

    # HeadingFki
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.darkblue)
    c.drawString(150, height - 60, "")

    c.setFont("Helvetica-Bold", 18)
    c.drawString(150, height - 90, "Invoice")

    c.setStrokeColor(colors.darkblue)
    c.setLineWidth(1.5)
    c.line(40, height - 100, width - 40, height - 100)

    # Basic Table Info
    c.setFont("Helvetica", 12)
    table_data = [
        ["Field", "Value"],
        ["Bill ID", bill_id],
        ["Patient Name", patient_name],
        ["Doctor", doctor_name],
        ["Appointment Date", appointment_date],
        ["Payment Status", status],
    ]

    x_start = 60
    y_start = height - 140
    row_height = 25
    col1_width = 160
    col2_width = 370

    for row_num, row in enumerate(table_data):
        y = y_start - row_num * row_height
        c.setFillColor(colors.white if row_num == 0 else colors.black)
        c.rect(x_start, y - row_height, col1_width, row_height, stroke=1, fill=row_num == 0)
        c.rect(x_start + col1_width, y - row_height, col2_width, row_height, stroke=1, fill=row_num == 0)
        c.setFillColor(colors.black)
        c.drawString(x_start + 5, y - 17, str(row[0]))
        c.drawString(x_start + col1_width + 5, y - 17, str(row[1]))

    # Billing Items Section
    # Billing Items Section
    billing_items = []
    total_amount = 0

    if db_connection:
        try:
            cursor = db_connection.cursor()
            cursor.execute("SELECT description, amount FROM billing_items WHERE bill_id = %s", (bill_id,))
            billing_items = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Error fetching billing items: {e}")

    if billing_items:
        # Total from billing items
        total_amount = sum(float(item[1]) for item in billing_items)

        # Billing Section Heading
        items_y_start = y - 60
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x_start, items_y_start, "Billing Details:")

        # Table setup
        items_table_y = items_y_start - 30
        item_row_height = 20
        desc_width = 300
        amount_width = 100

        # Table headers
        c.setFillColor(colors.lightgrey)
        c.rect(x_start, items_table_y, desc_width, item_row_height, stroke=1, fill=1)
        c.rect(x_start + desc_width, items_table_y, amount_width, item_row_height, stroke=1, fill=1)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_start + 5, items_table_y + 6, "Description")
        c.drawString(x_start + desc_width + 5, items_table_y + 6, "Amount (Rs.)")

        # Table rows
        c.setFont("Helvetica", 10)
        for i, (description, amount) in enumerate(billing_items):
            row_y = items_table_y - (i + 1) * item_row_height

            c.setFillColor(colors.white if i % 2 == 0 else colors.lightgrey)
            c.rect(x_start, row_y, desc_width, item_row_height, stroke=1, fill=1)
            c.rect(x_start + desc_width, row_y, amount_width, item_row_height, stroke=1, fill=1)

            c.setFillColor(colors.black)
            c.drawString(x_start + 5, row_y + 6, str(description).strip())
            c.drawString(x_start + desc_width + 5, row_y + 6, f"{float(amount):.2f}")

        # Total row
        total_y = items_table_y - (len(billing_items) + 1) * item_row_height
        c.setFillColor(colors.darkblue)
        c.rect(x_start, total_y, desc_width, item_row_height, stroke=1, fill=1)
        c.rect(x_start + desc_width, total_y, amount_width, item_row_height, stroke=1, fill=1)

        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_start + 5, total_y + 6, "TOTAL AMOUNT")
        c.drawString(x_start + desc_width + 5, total_y + 6, f"{total_amount:.2f}")

        current_y = total_y - 40  # Continue below
    else:
        # If no billing items, show original fee
        current_y = y - 60
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x_start, current_y, f"Total Fee: ₹{fee}")
        current_y -= 30


        # Medicine List Section
    if medicine_list:
        c.setFillColorRGB(0, 0, 1)  # Set color to blue
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x_start, current_y, "Prescribed Medicines:")
        c.setFont("Helvetica", 12)
        for i, med in enumerate(medicine_list, 1):
            current_y -= 18
            c.drawString(x_start + 15, current_y, f"{i}. {med}")
        current_y -= 20

    # Diagnosis Section
    if diagnosis:
        c.setFillColorRGB(0, 0, 1)  # Set color to blue again (in case color reset)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x_start, current_y, "Diagnosis:")
        c.setFont("Helvetica", 12)
        current_y -= 20
        text_object = c.beginText(x_start + 15, current_y)
        for line in diagnosis.split("\n"):
            text_object.textLine(line)
        c.drawText(text_object)

    # Optional: Reset color to black if you want to continue with default color later
    c.setFillColorRGB(0, 0, 0)


    # Signature Box
    sig_y = 100
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width - 200, sig_y + 40, "Signature:")

    # Draw signature box
    c.rect(width - 200, sig_y, 120, 30, stroke=1, fill=0)

    # Digital Signature (if provided)
    if signature_path:
        try:
            sign = ImageReader(signature_path)
            c.drawImage(sign, width - 198, sig_y + 2, width=115, height=26, mask='auto')
        except Exception as e:
            print(f"Signature load error: {e}")

    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(50, 30, f"Generated on: {datetime.now().strftime('%d-%m-%Y %I:%M %p')}")

    c.save()
    messagebox.showinfo("Success", f"Invoice saved as {file_path}")

def generate_leave_letter_pdf(leave_data, signature_path=None):
    # Unpack leave data
    try:
        leave_id, reason, days, payment, status, patient_name, doctor_name, issue_date = leave_data
    except ValueError:
        messagebox.showerror("Error", "Invalid leave data format.")
        return

    if payment.lower() != "paid":
        messagebox.showwarning("Payment Required", "Consultation letter can only be generated after payment is completed.")
        return

    # Ask where to save PDF
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        initialfile=f"Consultation_Leave_Letter_{leave_id}.pdf",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not file_path:
        return

    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    # Background
    c.setFillColorRGB(0.96, 0.98, 1)
    c.rect(0, 0, width, height, fill=1)

    # Clinic Header
    try:
        logo = ImageReader("Clinic_System/build/clinic-logo.png")
        c.drawImage(logo, 40, height - 100, width=70, height=70, mask='auto')
    except:
        pass

    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(colors.darkblue)
    c.drawString(120, height - 60, "")

    c.setFont("Helvetica-Bold", 16)
    c.drawString(120, height - 90, "Consultation Leave Letter")

    c.setStrokeColor(colors.darkblue)
    c.setLineWidth(1.2)
    c.line(40, height - 100, width - 40, height - 100)

    # Body Content
    c.setFont("Helvetica", 12)
    content_y = height - 140

    letter_body = f"""
Date: {issue_date}

To Whom It May Concern,

This is to certify that {patient_name} has consulted with Dr. {doctor_name} at our clinic 
on the above-mentioned date. Based on the diagnosis and health condition, the patient 
is advised to take rest for {days} day(s) due to the following reason:

Reason for Leave: {reason}

The consultation fee has been paid in full, and this letter is issued upon request 
for official or personal leave documentation.

We wish {patient_name} a speedy recovery.

Sincerely,
CLINCLOUD
"""

    # Draw the letter line-by-line
    text = c.beginText(60, content_y)
    text.setFont("Helvetica", 12)
    for line in letter_body.strip().split("\n"):
        text.textLine(line.strip())
    c.drawText(text)

    # Signature
    sig_y = 120
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width - 200, sig_y + 40, "Authorized Signature:")

    c.rect(width - 200, sig_y, 130, 30, stroke=1, fill=0)

    if signature_path:
        try:
            sign = ImageReader(signature_path)
            c.drawImage(sign, width - 198, sig_y + 2, width=125, height=26, mask='auto')
        except Exception as e:
            print(f"Signature load error: {e}")

    # Footer
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.gray)
    c.drawString(60, 30, f"Generated on: {datetime.now().strftime('%d-%m-%Y %I:%M %p')}")

    c.save()
    messagebox.showinfo("Success", f"Leave letter saved as:\n{file_path}")

info_frame = ctk.CTkFrame(app, fg_color=lbc, corner_radius=30, width=1100, height=490)
info_frame.place(x=40, y=180)
prescription_frame = ctk.CTkFrame(app, fg_color=lbc, corner_radius=30, width=1100, height=490)
bills_frame      = ctk.CTkFrame(app, fg_color=lbc, corner_radius=30, width=1100, height=490)
appointment_frame = ctk.CTkFrame(app, fg_color=lbc, corner_radius=30, width=1100, height=490)
LeaveLetter_frame = ctk.CTkFrame(app, fg_color=lbc, corner_radius=30, width=1100, height=490)

def show_info():
    prescription_frame.place_forget()
    appointment_frame.place_forget()
    bills_frame.place_forget()
    LeaveLetter_frame.place_forget()
    info_frame.place(x=40, y=180)

def hide_all_frames():
    info_frame.place_forget()
    prescription_frame.place_forget()
    appointment_frame.place_forget()
    bills_frame.place_forget()
    LeaveLetter_frame.place_forget()

def Bills(value):
    def view_invoice():
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Error", "Select a bill to generate invoice")
            return
        values = tree.item(selected, "values")
        appointment_id = values[1]
        appointment_date = values[2]
        fee = values[3]
        status = values[4]

        try:
            # Get bill_id from billing
            cursor.execute("SELECT bill_id FROM billing WHERE appointment_id = %s", (appointment_id,))
            bill_row = cursor.fetchone()
            if not bill_row:
                messagebox.showerror("Error", "Bill ID not found for this appointment")
                return
            bill_id = bill_row[0]

            # Get patient name
            cursor.execute("""
                SELECT p.first_name 
                FROM appointments a 
                JOIN patients p ON a.patient_id = p.patient_id 
                WHERE a.appointment_id = %s
            """, (appointment_id,))
            patient_row = cursor.fetchone()
            patient_name = patient_row[0] if patient_row else "Unknown"

            # Doctor (optional)
            doctor_name = " Kiran C. Patel"

            # ✅ Step 1: Get visit_id and diagnosis from visits
            cursor.execute("SELECT visit_id, diagnosis FROM visits WHERE appointment_id = %s", (appointment_id,))
            visit_row = cursor.fetchone()
            diagnosis = None
            medicine_list = []

            if visit_row:
                visit_id, diagnosis = visit_row

                # ✅ Step 2: Get prescription_id from prescriptions
                cursor.execute("SELECT prescription_id FROM prescriptions WHERE visit_id = %s", (visit_id,))
                pres_row = cursor.fetchone()

                if pres_row:
                    prescription_id = pres_row[0]

                    # ✅ Step 3: Get medicine names using prescription_items
                    cursor.execute("""
                        SELECT m.medicine_name
                        FROM prescription_items pi
                        JOIN medicines m ON pi.medicine_id = m.medicine_id
                        WHERE pi.prescription_id = %s
                    """, (prescription_id,))
                    medicine_list = [row[0] for row in cursor.fetchall()]

            # Prepare PDF input
            bill_data = (
                bill_id,
                appointment_date,
                fee,
                status,
                doctor_name,
                patient_name
            )

            generate_invoice_pdf(
                bill_data=bill_data,
                medicine_list=medicine_list,
                diagnosis=diagnosis,
                db_connection=mysqlconnection(),
                signature_path="Clinic_System/build/Signature.png"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate invoice: {e}")


    def appointment_paybills():
        app__to_update = ctk.CTkInputDialog(title="PAY BILLS", text="Enter the Appointment ID:").get_input()
        if not app__to_update:
            messagebox.showerror("Error", "Please enter the Appointment ID.")
            return

        if not app__to_update.isdigit():
            messagebox.showerror("Error", "Appointment ID must be a number.")
            return

        appointment_id = int(app__to_update)

        # Get all appointment IDs for this patient
        cursor.execute("SELECT appointment_id FROM appointments WHERE patient_id = %s", (value,))
        rows = cursor.fetchall()
        valid_ids = [row[0] for row in rows]

        if appointment_id not in valid_ids:
            messagebox.showerror("Error", f"Appointment ID {appointment_id} not found.")
            return

        cursor.execute("SELECT payment_status, Total_amount FROM billing WHERE appointment_id = %s", (appointment_id,))
        billing_row = cursor.fetchone()

        if not billing_row:
            messagebox.showerror("Error", "No billing record found.")
            return

        payment_status, total_amount = billing_row

        if payment_status == "Paid":
            messagebox.showinfo("Info", "The bill is already paid.")
            return

        cursor.execute("SELECT qr FROM doctor_login")
        result = cursor.fetchone()

        if not result or not result[0]:
            messagebox.showerror("Error", "QR code not found for the doctor.")
            return

        qr_path = result[0]

        try:
            qr_image = Image.open(qr_path).resize((250, 250))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load QR image:\n{e}")
            return

        paybills_frame = ctk.CTkToplevel()
        paybills_frame.geometry("500x580")
        paybills_frame.title("Pay Bills")
        paybills_frame.configure(fg_color="#f0f9ff")
        paybills_frame.resizable(False, False)
        paybills_frame.grab_set()

        uploaded_screenshot = None

        def upload_screenshot():
            nonlocal uploaded_screenshot
            file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
            if not file_path:
                return

            try:
                with open(file_path, "rb") as file:
                    uploaded_screenshot = file.read()
                messagebox.showinfo("Uploaded", "Screenshot uploaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload screenshot:\n{e}")

        def confirm_payment():
            if not uploaded_screenshot:
                messagebox.showerror("Error", "Please upload a screenshot of the payment before confirming.")
                return

            try:
                # 🔻 Save screenshot to DB - Write your query here
                query = "UPDATE billing SET payment_screenshot = %s WHERE appointment_id = %s"
                cursor.execute(query, (uploaded_screenshot, appointment_id))
                conn.commit()

                messagebox.showinfo("Success", "Payment marked as completed and screenshot saved.")
                paybills_frame.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error saving payment: {e}")

        title_label = ctk.CTkLabel(paybills_frame, text="Pay Your Medical Bill", font=("Arial", 22, "bold"), text_color="#000000")
        title_label.place(x=130, y=20)

        amount_label = ctk.CTkLabel(paybills_frame, text=f"Amount Due: ₹{total_amount}", font=("Arial", 18), text_color="#000000")
        amount_label.place(x=170, y=60)

        doc_label = ctk.CTkLabel(paybills_frame, text=f"Doctor: Dr. Karan yadav", font=("Arial", 16), text_color="#000000")
        doc_label.place(x=170, y=100)

        qr_photo = CTkImage(light_image=qr_image, size=(250, 250))
        qr_label = ctk.CTkLabel(paybills_frame, image=qr_photo, text="")
        qr_label.place(x=125, y=150)

        # Upload Screenshot Button
        upload_button = ctk.CTkButton(paybills_frame, text="Upload Screenshot", command=upload_screenshot, fg_color="#2196F3", hover_color="#1976D2")
        upload_button.place(x=170, y=420)

        # Instruction Label
        instruction_label = ctk.CTkLabel(
            paybills_frame,
            text="📌 Please scan the QR code, pay, and upload the screenshot below.",
            font=("Arial", 12),
            text_color="#000000",
            wraplength=460,
            justify="center"
        )
        instruction_label.place(x=30, y=380)

        # Confirm and Cancel Buttons
        confirm_button = ctk.CTkButton(paybills_frame, text="Confirm Payment", command=confirm_payment, fg_color="#38b000", hover_color="#2e7d32")
        confirm_button.place(x=80, y=520)

        cancel_button = ctk.CTkButton(paybills_frame, text="Cancel", command=paybills_frame.destroy, fg_color="#d62828", hover_color="#b71c1c")
        cancel_button.place(x=230, y=520)

        
    hide_all_frames()
    bills_frame.place(x=40, y=180)

    # Clear previous widgets
    for widget in bills_frame.winfo_children():
        widget.destroy()

    ctk.CTkLabel(
        bills_frame,
        text="Bills",
        font=("Georgia", 30, "bold"),
        text_color="white"
    ).place(x=520,y=30)

    # Table container
    table_container = ctk.CTkFrame(bills_frame, fg_color="#FFFFFF")
    table_container.place(x=40,y=90)

    # Columns
    columns = ("Bill Id","Appointments ID","Appointment Date", "Fee", "Status")
    cursor.execute(f"select b.bill_id,a.appointment_id,a.appointment_date,b.total_amount,b.payment_status from billing b,appointments a where b.appointment_id=a.appointment_id and a.patient_id={value}")
    billdata = cursor.fetchall()
    conn.commit()

    # for row in billdata:
    #     tree.insert("", "end", values=row)

    tree = ttk.Treeview(table_container, columns=columns, show="headings", height=18)

    for col in columns:
        tree.heading(col, text=col )
        tree.column(col, anchor="center", width=250)

    # Row tag colors
    tree.tag_configure("paid", background="#e1f7d5")     # Light green
    tree.tag_configure("unpaid", background="#ff6d6d")   # Light red

    tree.tag_configure("rowfont", font=("Arial", 10))

    for row in billdata:
        tag = "paid" if row[4].lower() == "paid" else "unpaid"
        tree.insert("", "end", values=row, tags=("rowfont", tag))


    # Scrollbar
    scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(side="left", fill="both", expand=True)

    # Button Frame
    button_frame = ctk.CTkFrame(bills_frame, fg_color="transparent",width=1050,height=50)
    button_frame.place(x=10,y=420)

    # Back Button
    back_button = ctk.CTkButton(
        button_frame,
        text="← Back",
        font=("Georgia", 16, "bold"),
        width=120,
        height=40,
        corner_radius=20,
        fg_color="red",
        text_color="white",
        hover_color="#0B2E52",
        command=show_info
    )
    back_button.place(x=5,y=10)

    # View Invoice Button
    view_button = ctk.CTkButton(
        button_frame,
        text="View Invoice",
        font=("Georgia", 16, "bold"),
        width=150,
        height=40,
        corner_radius=20,
        fg_color="#1C3D64",
        text_color="white",
        hover_color="#0B2E52",
        command=view_invoice
    )
    view_button.place(x=880,y=10)

    Pay_amount = ctk.CTkButton(
        button_frame,
        text="Pay",
        font=("Georgia", 16, "bold"),
        width=150,
        height=40,
        corner_radius=20,
        fg_color="#2EFF96",
        text_color="white",
        hover_color="#12A559",
        command=appointment_paybills
    )
    Pay_amount.place(x=700,y=10)

def get_available_time_slots(appt_date):
    """Returns a dictionary of hour -> (booked count, max)"""
    time_ranges = [
        range(9, 12),     # 9–11 AM
        range(12, 16),    # 12–3 PM
        range(17, 21),    # 5–8 PM
    ]
    max_per_hour = 2
    slot_data = {}

    for time_range in time_ranges:
        for hour in time_range:
            cursor.execute("""
                SELECT COUNT(*) FROM appointments
                WHERE appointment_date = %s AND HOUR(appointment_time) = %s
            """, (appt_date.strftime("%Y-%m-%d"), hour))
            count = cursor.fetchone()[0]
            slot_data[f"{hour:02}"] = (count, max_per_hour)

    return slot_data

def Appointments(value):
    # Get today's available hours when window opens
    default_date = datetime.today().date()
    slot_info = get_available_time_slots(default_date)
    available_hours = [hour for hour, (booked, maxx) in slot_info.items() if booked < maxx]

    def cancel_appointments():
        app__to_update = ctk.CTkInputDialog(title="Cancel Appointment", text="Enter the Appointment ID:").get_input()
        if not app__to_update:
            messagebox.showerror("Error", "Please enter the Appointment ID.")
            return

        if not app__to_update.isdigit():
            messagebox.showerror("Error", "Appointment ID must be a number.")
            return

        appointment_id = int(app__to_update)
        
        # Get all appointment IDs for this patient
        cursor.execute("SELECT appointment_id FROM appointments WHERE patient_id = %s", (value,))
        rows = cursor.fetchall()
        valid_ids = [row[0] for row in rows]

        cursor.execute("SELECT status FROM appointments WHERE appointment_id = %s", (appointment_id,))
        rows = cursor.fetchall()
        print(rows)

        if appointment_id not in valid_ids:
            messagebox.showerror("Error", f"Appointment ID {appointment_id} not found ")
            return
        elif rows[0][0] == "Completed":
            messagebox.showerror("Error", f"Appointment: {appointment_id} is Completed ")
            return
        
        # Proceed to cancel the appointment
        cursor.execute("""
            UPDATE appointments 
            SET status = %s 
            WHERE patient_id = %s AND appointment_id = %s
        """, ("Cancelled", value, appointment_id))
        conn.commit()

        messagebox.showinfo("Success", f"Appointment {appointment_id} cancelled successfully.")
        load_appointments() 

    def load_appointments():
        # Clear previous rows
        for row in tree.get_children():
            tree.delete(row)

        # Re-fetch data
        cursor.execute("""
            SELECT a.appointment_id, a.appointment_date, a.appointment_time, a.status, v.Diagnosis 
            FROM appointments a
            JOIN visits v ON a.appointment_id = v.appointment_id
            WHERE a.patient_id = %s
        """, (value,))
        rows = cursor.fetchall()
        conn.commit()

        tree.tag_configure("Cancelled", background="#ff8a8a")     # Light green
        tree.tag_configure("Scheduled", background="#848484") 
        tree.tag_configure("Completed", background="#b1ffb6")  
        tree.tag_configure("rowfont", font=("Arial", 10))
        for row in rows:
            status = row[3]
            if status == "Scheduled":
                status_tag = "Scheduled"
            elif status == "Cancelled":
                status_tag = "Cancelled"
            elif status == "Completed":
                status_tag = "Completed"
            else:
                status_tag = ""  # fallback if needed

            tree.insert("", "end", values=row, tags=("rowfont", status_tag))

    def apply_appointments():
        try:
            cursor.execute("select is_active from doctor_login")
            drstatus = cursor.fetchone()[0]
            print(drstatus)
            if drstatus == "False":
                messagebox.showerror("Status","Cannnot apply for appointment because Doctor is unavailable")
                return
        except Exception as e:
            print(e)
        def show_slot_popup(selected_date):
            slot_info = get_available_time_slots(selected_date)
            popup = ctk.CTkToplevel(apply_window)
            popup.title(f"Available Slots - {selected_date.strftime('%Y-%m-%d')}")
            popup.geometry("400x400")
            popup.configure(bg="white")

            ctk.CTkLabel(popup, text=f"Available Slots for {selected_date.strftime('%Y-%m-%d')}",
                        font=("Arial", 18, "bold"), text_color="black").pack(pady=10)

            slot_container = ctk.CTkFrame(popup, fg_color="white")
            slot_container.pack(fill="both", expand=True, padx=10, pady=10)

            row, col = 0, 0
            for hour, (booked, maxx) in slot_info.items():
                status = f"{booked}/{maxx}" if booked < maxx else "Full"
                time_label = f"{hour}:00"
                color = "#51CF66" if booked < maxx else "#FF6B6B"

                slot = ctk.CTkFrame(slot_container, width=80, height=60, fg_color=color, corner_radius=10)
                slot.grid(row=row, column=col, padx=8, pady=8)

                ctk.CTkLabel(slot, text=time_label, font=("Arial", 13, "bold")).pack()
                ctk.CTkLabel(slot, text=status, font=("Arial", 12)).pack()

                col += 1
                if col >= 4:
                    col = 0
                    row += 1

            ctk.CTkButton(popup, text="Close", command=popup.destroy,
                        fg_color="black", text_color="white").pack(pady=10)

        def show_slot_popup_safe():
            try:
                selected_date = date_entry.get_date()
                if not selected_date:
                    raise ValueError("No date selected")
                show_slot_popup(selected_date)
            except Exception:
                messagebox.showerror("Date Error", "Please select a valid appointment date.", parent=appointment_frame)

        def on_date_selected(event):
            selected_date = date_entry.get_date()
            slot_info = get_available_time_slots(selected_date)

            available_hours = [hour for hour, (booked, maxx) in slot_info.items() if booked < maxx]

            if not available_hours:
                messagebox.showinfo("Slots Full", "No available slots for selected date.")
                hour_combo.configure(values=[], state="disabled")
                minute_combo.configure(state="disabled")
                submit_button.configure(state="disabled")
            else:
                # Only set available hours
                hour_combo.configure(values=available_hours, state="normal")
                hour_combo.set(available_hours[0])
                minute_combo.configure(state="normal")
                submit_button.configure(state="normal")

        def submit_appointment():
            date = date_entry.get()
            selected_time = f"{hour_var.get()}:{minute_var.get()}"
            purpose = purpose_entry.get()
            notes = notes_entry.get()

            if datetime.strptime(date, "%Y-%m-%d").date() < datetime.today().date():
                messagebox.showerror("Invalid Date", "You cannot book appointments in the past.")
                return

            cursor.execute("""
                INSERT INTO appointments 
                VALUES (NULL, %s, %s, %s, DEFAULT, DEFAULT, DEFAULT, DEFAULT)
            """, (value, date, selected_time))
            conn.commit()

            appointment_id = cursor.lastrowid
            cursor.execute("INSERT INTO visits VALUES (NULL, %s, %s, NULL, NULL)", (appointment_id, purpose))
            conn.commit()

            tree.insert("", "end", values=(appointment_id, date, selected_time, "pending", purpose))
            apply_window.destroy()
            load_appointments()  # Refresh tree with new data


        # ---------- Apply Window ----------
        apply_window = ctk.CTkToplevel()
        apply_window.title("Apply for Appointment")
        apply_window.geometry("500x560")
        apply_window.configure(fg_color="#38BDFF")
        apply_window.grab_set()

        ctk.CTkLabel(apply_window, text="Apply for Appointment", font=("Georgia", 22, "bold")).pack(pady=15)

        form_frame = ctk.CTkFrame(apply_window, width=460, height=460, corner_radius=15, fg_color="white")
        form_frame.pack(padx=20, pady=10)

        # Appointment Date
        ctk.CTkLabel(form_frame, text="Appointment Date:", font=("Georgia", 14)).place(x=30, y=20)
        date_entry = DateEntry(form_frame, width=22, font=("Georgia", 14), date_pattern="yyyy-mm-dd")
        date_entry.place(x=30, y=55)
        date_entry.bind("<<DateEntrySelected>>", on_date_selected)

        ctk.CTkButton(form_frame, text="View Available Slots", command=show_slot_popup_safe,
                    fg_color="#007BFF", text_color="white", hover_color="#0056b3", width=180).place(x=270, y=42)

        # Appointment Time
        ctk.CTkLabel(form_frame, text="Select Time", font=("Georgia", 14)).place(x=30, y=100)
        ctk.CTkLabel(form_frame, text="Hour", font=("Georgia", 12)).place(x=30, y=135)
        hour_var = ctk.StringVar()
        hour_combo = ctk.CTkComboBox(form_frame, width=90, variable=hour_var, values=available_hours)
        hour_combo.place(x=80, y=135)

        if available_hours:
            hour_combo.set(available_hours[0])
        else:
            hour_combo.configure(state="disabled")


        ctk.CTkLabel(form_frame, text="Minute", font=("Georgia", 12)).place(x=200, y=135)
        minute_var = ctk.StringVar()
        minute_combo = ctk.CTkComboBox(form_frame, width=90, variable=minute_var, values=[f"{m:02d}" for m in range(0, 60, 5)])
        minute_combo.place(x=270, y=135)
        minute_combo.set("00")

        # Purpose
        ctk.CTkLabel(form_frame, text="Purpose of Visit:", font=("Georgia", 14)).place(x=30, y=180)
        purpose_entry = ctk.CTkEntry(form_frame, width=380, height=35, font=("Georgia", 12))
        purpose_entry.place(x=30, y=215)

        # Additional Notes
        ctk.CTkLabel(form_frame, text="Additional Notes (optional):", font=("Georgia", 14)).place(x=30, y=260)
        notes_entry = ctk.CTkEntry(form_frame, width=380, height=35, font=("Georgia", 12))
        notes_entry.place(x=30, y=295)

        # Submit
        submit_button = ctk.CTkButton(form_frame, text="Submit Appointment", command=submit_appointment,
                                    font=("Georgia", 14), fg_color="#1C3D64", text_color="white",
                                    hover_color="#153254", width=200, height=45, corner_radius=10)
        submit_button.place(x=130, y=370)

    hide_all_frames()
    appointment_frame.place(x=40, y=180)

    # Clear previous widgets
    for widget in appointment_frame.winfo_children():
        widget.destroy()

    ctk.CTkLabel(appointment_frame, text="Appointments", font=("Georgia", 30, "bold"), text_color="white").place(x=520,y=30)

    # Table container (as CTkFrame for background color support)
    table_container = ctk.CTkFrame(appointment_frame, fg_color="#FFFFFF")
    table_container.place(x=40,y=90)

    # Treeview for Appointments
    columns = ("Appointments ID", "Appointments Date","Appointments Time", "Status", "Reason")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", height=18)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=250)

    load_appointments()


    # Scrollbar
    scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(side="left", fill="both", expand=True)

    button_frame = ctk.CTkFrame(appointment_frame, fg_color=lbc, width=1050, height=50)
    button_frame.place(x=10, y=420)

    # Back Button
    back_button = ctk.CTkButton(
        button_frame,
        text="← Back",
        font=("Georgia", 16, "bold"),
        width=120,
        height=40,
        corner_radius=20,
        fg_color="#0B2E52", #0B2E52
        text_color="white",
        hover_color="red",
        command=show_info
    )
    back_button.place(x=5, y=10)

    # Cancel Button with slightly lighter red
    cancel_button = ctk.CTkButton(
        button_frame,
        text="Cancel Appointment",
        font=("Georgia", 16, "bold"),
        width=120,
        height=40,
        corner_radius=20,
        fg_color="red",  # Lighter red
        text_color="white",
        hover_color="#520B0B",
        command=cancel_appointments
    )
    cancel_button.place(x=570, y=10)

    # Apply Appointment Button
    apply_appointments_button = ctk.CTkButton(
        button_frame,
        text="Apply For Appointment",
        font=("Georgia", 16, "bold"),
        width=120,
        height=40,
        corner_radius=20,
        fg_color="green",
        text_color="white",
        hover_color="#0B2E52",
        command=apply_appointments
    )
    apply_appointments_button.place(x=800, y=10)


def Prescriptions(value):
    def load_prescriptions():
        tree.delete(*tree.get_children())  # Clear existing rows

        cursor.execute(f"SELECT appointment_id FROM appointments WHERE patient_id = {value}")
        appointment_ids = [row[0] for row in cursor.fetchall()]

        if appointment_ids:
            format_ids = ",".join(map(str, appointment_ids))
            cursor.execute(f""" SELECT visit_id FROM visits WHERE appointment_id IN ({format_ids}) """)
            visit_ids = [row[0] for row in cursor.fetchall()]
            visitformat_ids = ",".join(map(str, visit_ids))

            cursor.execute(f"""
                SELECT pi.item_id, p.prescription_id, m.medicine_name, pi.dosage, p.notes, p.issued_date 
                FROM prescription_items pi 
                JOIN medicines m ON pi.medicine_id = m.medicine_id 
                JOIN prescriptions p ON pi.prescription_id = p.prescription_id 
                WHERE p.visit_id IN ({visitformat_ids})
            """)
            pres = cursor.fetchall()
            conn.commit()
        else:
            pres = []

        grouped = defaultdict(list)
        notes_by_pid = {}
        date_by_pid = {}

        for item_id, prescription_id, medicine, dosage, notes, issued_date in pres:
            grouped[prescription_id].append((item_id, medicine, dosage))
            notes_by_pid[prescription_id] = notes
            date_by_pid[prescription_id] = issued_date

        row_colors = ["#C7FCFF", "#B3FACD", "#FFD1D1", "#EBD8FF"]

        for color_index, pid in enumerate(grouped):
            rows = grouped[pid]
            tag_name = f"pid_{pid}"
            tree.tag_configure(tag_name, background=row_colors[color_index % len(row_colors)])
            tree.tag_configure("rowfont", font=("Arial", 10))
            for idx, (prescription_id, medicine, dosage) in enumerate(rows):
                if idx == 0:
                    tree.insert(
                        "", "end",
                        values=(prescription_id, medicine, dosage, notes_by_pid[pid], date_by_pid[pid]),
                        tags=(tag_name,"rowfont")
                    )
                else:
                    tree.insert(
                        "", "end",
                        values=(prescription_id, medicine, dosage, "", ""),
                        tags=(tag_name,"rowfont")
                    )

    # Base layout
    hide_all_frames()
    prescription_frame.place(x=40, y=180)
    for widget in prescription_frame.winfo_children():
        widget.destroy()

    ctk.CTkLabel(prescription_frame, text="Prescriptions", font=("Georgia", 30, "bold"), text_color="white").place(x=520,y=30)

    table_container = ctk.CTkFrame(prescription_frame, fg_color="#FFFFFF")
    table_container.place(x=40,y=90)

    columns = ("prescription Id", "Medicine", "Dosage", "Notes", "Date")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", height=18)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=250)

    scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(side="left", fill="both", expand=True)

    # Buttons Frame
    button_frame = ctk.CTkFrame(prescription_frame, fg_color="transparent", width=1000, height=50)
    button_frame.place(x=10, y=420)

    # Back Button
    back_button = ctk.CTkButton(
        button_frame,
        text="← Back",
        font=("Georgia", 16, "bold"),
        width=120,
        height=40,
        corner_radius=20,
        fg_color="red",
        text_color="white",
        hover_color="#0B2E52",
        command=show_info
    )
    back_button.place(x=5, y=10)

    # Refresh Button
    # refresh_button = ctk.CTkButton(
    #     button_frame,
    #     text="↻ Refresh",
    #     font=("Georgia", 16, "bold"),
    #     width=120,
    #     height=40,
    #     corner_radius=20,
    #     fg_color="#1C3D64",
    #     text_color="white",
    #     hover_color="#0B2E52",
    #     command=load_prescriptions
    # )
    # refresh_button.place(x=450, y=10)

    # Initial load
    load_prescriptions()

def LeaveLetter(value):  # ⬅ Pass patient ID
    def apply_consultation():
        try:
            cursor.execute("SELECT is_active FROM doctor_login")
            drstatus = cursor.fetchone()[0]

            if drstatus == "False":
                messagebox.showerror("Doctor Unavailable", "Cannot apply for leave consultation because doctor is unavailable.")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Error checking doctor status: {e}")
            return
        apply_window = ctk.CTkToplevel()
        apply_window.title("Apply for Consultation Letter")
        apply_window.geometry("460x500")
        apply_window.grab_set()

        ctk.CTkLabel(apply_window, text="Apply for Consultation Letter", font=("Georgia", 18, "bold")).place(x=70, y=20)

        # Appointment ID
        ctk.CTkLabel(apply_window, text="Appointment ID:", font=("Georgia", 14)).place(x=30, y=80)
        appointment_entry = ctk.CTkEntry(apply_window, width=380, placeholder_text="Enter your Appointment ID")
        appointment_entry.place(x=30, y=110)

        # Reason
        ctk.CTkLabel(apply_window, text="Reason for Consultation:", font=("Georgia", 14)).place(x=30, y=150)
        reason_entry = ctk.CTkEntry(apply_window, width=380, placeholder_text="e.g., Fever, Injury")
        reason_entry.place(x=30, y=180)

        # Days Requested
        ctk.CTkLabel(apply_window, text="Days Requested:", font=("Georgia", 14)).place(x=30, y=220)
        days_entry = ctk.CTkEntry(apply_window, width=380, placeholder_text="e.g., 3")
        days_entry.place(x=30, y=250)

        # Consultation Type
        ctk.CTkLabel(apply_window, text="Consultation Type:", font=("Georgia", 14)).place(x=30, y=290)
        consultation_type_var = ctk.StringVar(value="Medical")
        consultation_type_menu = ctk.CTkComboBox(apply_window, width=380, values=["Medical", "Specialist", "Follow-up", "Emergency"], variable=consultation_type_var)
        consultation_type_menu.place(x=30, y=320)

        def submit_application():
            appointment_id = appointment_entry.get().strip()
            reason = reason_entry.get().strip()
            days = days_entry.get().strip()
            consultation_type = consultation_type_var.get()

            if not (appointment_id and reason and days):
                messagebox.showwarning("Missing Info", "Please fill in all fields.")
                return

            if not appointment_id.isdigit():
                messagebox.showerror("Invalid Appointment ID", "Appointment ID must be a number.")
                return

            if reason.isdigit() or len(reason) < 3:
                messagebox.showerror("Invalid Reason", "Reason must be a valid description.")
                return

            if not days.isdigit() or int(days) > 10:
                messagebox.showerror("Invalid Days", "Leave days must be a number ≤ 10.")
                return

            try:
                cursor.execute("""
                    SELECT patient_id FROM appointments WHERE appointment_id = %s AND patient_id = %s
                """, (appointment_id, value))
                result = cursor.fetchone()

                if not result:
                    messagebox.showerror("Error", "Invalid Appointment ID or not linked to your account.")
                    return

                cursor.execute("""
                    INSERT INTO consultation_letters 
                    (appointment_id, patient_name, days_requested, reason, status, payment_status, consultation_type, consultation_fee)
                    VALUES (%s, %s, %s, %s, 'Pending', 'Unpaid', %s, 100.00)
                """, (
                    appointment_id,
                    f"{fname} {lname}",  # ⬅ Ensure fname/lname are defined globally for patient
                    int(days),
                    reason,
                    consultation_type
                ))
                conn.commit()
                messagebox.showinfo("Success", "Consultation Letter Request Submitted.")
                apply_window.destroy()
                load_leave_letters()  # Refresh table
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to submit: {e}")

        # Submit Button
        ctk.CTkButton(
            apply_window,
            text="Submit",
            font=("Georgia", 14, "bold"),
            width=140,
            height=40,
            corner_radius=20,
            fg_color="#1C3D64",
            text_color="white",
            command=submit_application
        ).place(x=160, y=400)

    def leave_paybills(): 
        cus__to_update = ctk.CTkInputDialog(title="PAY Consultation BILLS", text="Enter the Consultation ID:").get_input()
        if not cus__to_update:
            messagebox.showerror("Error", "Please enter the Consultation ID.")
            return

        if not cus__to_update.isdigit():
            messagebox.showerror("Error", "Consultation ID must be a number.")
            return

        consultation_id = int(cus__to_update)

        cursor.execute("SELECT payment_status, consultation_fee FROM consultation_letters WHERE consultation_id = %s", (consultation_id,))
        billing_row = cursor.fetchone()

        if not billing_row:
            messagebox.showerror("Error", "No billing record found.")
            return

        payment_status, total_amount = billing_row

        if payment_status == "Paid":
            messagebox.showinfo("Info", "The bill is already paid.")
            return

        cursor.execute("SELECT qr FROM doctor_login")
        result = cursor.fetchone()

        if not result or not result[0]:
            messagebox.showerror("Error", "QR code not found for the doctor.")
            return

        qr_path = result[0]

        try:
            qr_image = Image.open(qr_path).resize((250, 250))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load QR image:\n{e}")
            return

        # GUI Window
        paybills_frame = ctk.CTkToplevel()
        paybills_frame.geometry("500x580")
        paybills_frame.title("Pay Consultation Bill")
        paybills_frame.configure(fg_color="#f0f9ff")
        paybills_frame.resizable(False, False)
        paybills_frame.grab_set()

        uploaded_screenshot = None

        def upload_screenshot():
            nonlocal uploaded_screenshot
            file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
            if not file_path:
                return
            try:
                with open(file_path, "rb") as file:
                    uploaded_screenshot = file.read()
                messagebox.showinfo("Uploaded", "Screenshot uploaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload screenshot:\n{e}")

        def confirm_payment():
            if not uploaded_screenshot:
                messagebox.showerror("Error", "Please upload a screenshot of the payment before confirming.")
                return
            try:
                # 🔻 Replace this query with your actual insert/update logic
                query = "UPDATE consultation_letters SET screenshot = %s WHERE consultation_id = %s"
                cursor.execute(query, (uploaded_screenshot, consultation_id))
                conn.commit()

                messagebox.showinfo("Success", "Payment confirmed and screenshot saved. Your Consultation Letter Application will be check by Doctor")
                paybills_frame.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to confirm payment: {e}")

        title_label = ctk.CTkLabel(paybills_frame, text="Pay Your Consultation Bill", font=("Arial", 22, "bold"), text_color="#000000")
        title_label.place(x=100, y=20)

        amount_label = ctk.CTkLabel(paybills_frame, text=f"Amount Due: ₹{total_amount}", font=("Arial", 18), text_color="#000000")
        amount_label.place(x=170, y=60)

        doc_label = ctk.CTkLabel(paybills_frame, text=f"Dr. Karan Yadav", font=("Arial", 16), text_color="#000000")
        doc_label.place(x=170, y=100)

        qr_photo = CTkImage(light_image=qr_image, size=(250, 250))
        qr_label = ctk.CTkLabel(paybills_frame, image=qr_photo, text="")
        qr_label.place(x=125, y=150)

        instruction_label = ctk.CTkLabel(
            paybills_frame,
            text="📌 Please scan the QR code, pay the amount, and upload the payment screenshot below.",
            font=("Arial", 12),
            text_color="#000000",
            wraplength=460,
            justify="center"
        )
        instruction_label.place(x=30, y=380)

        upload_button = ctk.CTkButton(paybills_frame, text="Upload Screenshot", command=upload_screenshot, fg_color="#2196F3", hover_color="#1976D2")
        upload_button.place(x=170, y=420)

        confirm_button = ctk.CTkButton(paybills_frame, text="Confirm Payment", command=confirm_payment, fg_color="#38b000", hover_color="#2e7d32")
        confirm_button.place(x=80, y=520)

        cancel_button = ctk.CTkButton(paybills_frame, text="Cancel", command=paybills_frame.destroy, fg_color="#d62828", hover_color="#b71c1c")
        cancel_button.place(x=230, y=520)

    def generate_pdf_from_selection():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a row from the table.")
            return

        values = tree.item(selected, "values")
        consultation_id, reason, days, payment_status, status, _ = values

        if status.lower() != "approved":
            messagebox.showinfo("Pending Approval", "Consultation letter can only be generated after approval.")
            return

        patient_name = f"{fname} {lname}"
        doctor_name = "Kiran C. Patel"
        issue_date = datetime.now().strftime("%Y-%m-%d")
        leave_data = (consultation_id, reason, days, payment_status, status, patient_name, doctor_name, issue_date)
        signature_path = "Clinic_System/build/Signature.png"

        generate_leave_letter_pdf(leave_data, signature_path)

    def refresh_tree():
        load_leave_letters()  # Refresh data

    def load_leave_letters():

        tree.delete(*tree.get_children())
        cursor.execute("""
            SELECT cl.consultation_id, cl.reason, cl.days_requested, cl.payment_status, cl.status,cl.consultation_fee
            FROM consultation_letters cl
            JOIN appointments a ON cl.appointment_id = a.appointment_id
            WHERE a.patient_id = %s
        """, (value,))

        LeaveLetters = cursor.fetchall()
        conn.commit()
        print("Fetched rows:", LeaveLetters)  # debug line

        for row in LeaveLetters:
            tree.insert("", "end", values=row)
        tree.update_idletasks()

    hide_all_frames()
    LeaveLetter_frame.place(x=40, y=180)

    for widget in LeaveLetter_frame.winfo_children():
        widget.destroy()

    ctk.CTkLabel(LeaveLetter_frame, text="Consultation Letters", font=("Georgia", 30, "bold"), text_color="white").place(x=450,y=30)

    table_container = ctk.CTkFrame(LeaveLetter_frame, fg_color="#FFFFFF")
    table_container.place(x=40,y=90)

    columns = ("ID", "Reason", "Days", "Payment", "Status","Consultation Fees")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", height=18)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=210)

    scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(side="left", fill="both", expand=True)

    button_frame = ctk.CTkFrame(LeaveLetter_frame, fg_color="transparent", width=1050, height=50)
    button_frame.place(x=10, y=420)

    back_button = ctk.CTkButton(
        button_frame,
        text="← Back",
        font=("Georgia", 16, "bold"),
        width=120,
        height=40,
        corner_radius=20,
        fg_color="red",
        text_color="white",
        hover_color="#0B2E52",
        command=show_info
    )
    back_button.place(x=5, y=10)


    ctk.CTkButton(
        button_frame,
        text="Apply For Consultation Letter",
        font=("Georgia", 16, "bold"),
        width=120,
        height=40,
        corner_radius=20,
        fg_color="#1C3D64",
        text_color="white",
        hover_color="#0B2E52",
        command=apply_consultation
    ).place(x=760, y=10)

    ctk.CTkButton(
        LeaveLetter_frame,
        text="Generate PDF",
        font=("Georgia", 16, "bold"),
        width=120,
        height=40,
        corner_radius=20,
        fg_color="#198754",
        text_color="white",
        hover_color="#157347",
        command=generate_pdf_from_selection
    ).place(x=880, y=30)
    Pay_amount = ctk.CTkButton(
        button_frame,
        text="Pay",
        font=("Georgia", 16, "bold"),
        width=150,
        height=40,
        corner_radius=20,
        fg_color="#2EFF96",
        text_color="white",
        hover_color="#12A559",
        command=leave_paybills
    )
    Pay_amount.place(x=600,y=10)

    # Initial load of data
    load_leave_letters()

def refresh_patient_info(patient_id):
    result = fetch_patient_by_id(patient_id)
    if not result:
        return
    
    ( patient_id, user_id, fname, lname, gender, dob, contact_number, email, address,
      emergency_no, blood_group, created, image, age ) = result

    # Update labels
    display_labels["name"].configure(text=f"NAME :{fname} {lname}")
    display_labels["dob"].configure(text=f"Dob :- {dob}")
    display_labels["blood group"].configure(text=f"BLOOD GROUP :-  {blood_group}")
    display_labels["contact"].configure(text=f"CONTACT :- {contact_number}")
    display_labels["email"].configure(text=f"Email Address :- {email}")
    display_labels["gender"].configure(text=f"GENDER :- {gender}")
    display_labels["address"].configure(text=f"ADDRESS :- {address}")
    display_labels["age"].configure(text=f"AGE :-{age}")

    # Update photo
    if image and os.path.exists(image):
        pil_img = Image.open(image)
        ctk_img = CTkImage(pil_img, size=(280, 220))
        photo_label.configure(image=ctk_img)
        # photo_label.image = ctk_img  # prevent garbage collection
    else:
        photo_label.configure(image=None, text="")

# Image box (placeholder)

def fetch_patient_by_id(value):
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='clinic_management'
        )

        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (value,))
                row = cursor.fetchone()
                cursor.execute(f"Select timestampdiff(year , dob , curdate()) as age from patients where patient_id={value}")
                age = cursor.fetchone()[0]
                if not row:
                    return None

                # Unpack tuple in exact column order
                (
                    patient_id,  
                    user_id,            # 1
                    fname,             # 2
                    lname,             # 3
                    gender,            # 4
                    dob,               # 5
                    contact_number,    # 6
                    email,             # 7
                    address,           # 8
                    emergency_no,      # 9
                    blood_group,       # 10
                    created,           
                    image,             # 13
                ) = row

                return (
                    patient_id,user_id,        # 1
                    fname,             # 2
                    lname,             # 3
                    gender,            # 4
                    dob,               # 5
                    contact_number,    # 6
                    email,             # 7
                    address,           # 8
                    emergency_no,      # 9
                    blood_group,       # 10
                    created,          
                    image, 
                    age
                )

    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        return None


result = fetch_patient_by_id(value)
if result:
        ( patient_id,user_id,       # 1
                    fname,             # 2
                    lname,             # 3
                    gender,            # 4
                    dob,               # 5
                    contact_number,    # 6
                    email,             # 7
                    address,           # 8
                    emergency_no,      # 9
                    blood_group,       # 10
                    created,           
                    image,
                    age ) = result
        
display_labels = {
    "name": ctk.CTkLabel(info_frame, text=f"NAME :{fname} {lname}", font=("Georgia", 25, "bold"), text_color="white"),
    "dob": ctk.CTkLabel(info_frame, text=f"Dob :- {dob}", font=label_font, text_color="white"),
    "blood group": ctk.CTkLabel(info_frame, text=f"BLOOD GROUP :-  {blood_group}", font=label_font, text_color="white"),
    "contact": ctk.CTkLabel(info_frame, text=f"CONTACT :- {contact_number}", font=label_font, text_color="white"),
    "email": ctk.CTkLabel(info_frame, text=f"Email Address :- {email}", font=label_font, text_color="white"),
    "gender": ctk.CTkLabel(info_frame, text=f"GENDER :- {gender}", font=label_font, text_color="white"),
    "address": ctk.CTkLabel(info_frame, text=f"ADDRESS :- {address}", font=label_font, text_color="white"),
    "age": ctk.CTkLabel(info_frame, text=f"AGE :- {age}", font=label_font, text_color="white")
}

if image and os.path.exists(image):
    pil_img = Image.open(image)
    ctk_img = CTkImage(pil_img, size=(280, 220))
    photo_label = ctk.CTkLabel(info_frame, image=ctk_img, text="", width=220, height=220, corner_radius=20, fg_color="white")
    photo_label.image = ctk_img  
    photo_label.place(x=28, y=28)
else:
    print("Image path is invalid or file not found.")


result = fetch_patient_by_id(value)
print(f"current date - {age}")
# Place profile info labels
display_labels["name"].place(x=50, y=260)

display_labels["age"].place(x=750, y=40)

display_labels["dob"].place(x=370, y=40)
display_labels["blood group"].place(x=370,y=160)

display_labels["gender"].place(x=370, y=100)
display_labels["contact"].place(x=750, y=100)

display_labels["email"].place(x=370, y=220)

# ctk.CTkLabel(info_frame, text="CURRENT STATUS :- WELL", font=label_font, text_color="white").place(x=370, y=130)
display_labels["address"].place(x=370, y=280)

# icons
pres_icon = ctk.CTkImage(light_image=Image.open("Clinic_System/build/medicine.png"), size=(70,70))
appt_icon = ctk.CTkImage(light_image=Image.open("Clinic_System/build/calendar.png"), size=(70,70))
bills_icon = ctk.CTkImage(light_image=Image.open("Clinic_System/build/payment.png"), size=(70,70))
leave_icon = ctk.CTkImage(light_image=Image.open("Clinic_System/build/mail.png"), size=(70,70))

buttons = [
    ("Prescriptions", 180, pres_icon, Prescriptions),
    ("Appointments", 310, appt_icon, Appointments),
    ("Bills",        440, bills_icon, Bills),
    ("Leave Letter", 570, leave_icon, LeaveLetter),
]

button_width = 290
button_height = 100
button_radius = 20
button_x = 1200
shadow_offset = 5

for text, y, icon, command_func in buttons:
    # Shadow Frame
    ctk.CTkFrame(
        app,
        fg_color="black",
        corner_radius=button_radius,
        width=button_width+2,
        height=button_height,
    ).place(x=button_x + shadow_offset, y=y + shadow_offset)

    # Actual Button
    ctk.CTkButton(
        app,
        text=text,
        image=icon,
        font=button_font,
        width=button_width,
        height=button_height,
        corner_radius=button_radius,
        fg_color=mbc,
        text_color=tb,
        hover_color="#6170A1",
        anchor="e",
        compound="right",
        command=lambda cmd=command_func: cmd(value)
    ).place(x=button_x, y=y)


# Update Profile Window
def open_update_window(value):
    connection = pymysql.connect(host='localhost', user='root', password='root', database='clinic_management')
    cursor = connection.cursor()
    cursor.execute("""SELECT concat(first_name," ",last_name), gender, dob, contact_number, email, blood_group, address,image FROM patients WHERE patient_id=%s""", (value,))
    patient_data = cursor.fetchone()

    update_window = ctk.CTkToplevel()
    update_window.geometry("600x710")
    update_window.title("Update Profile")
    update_window.configure(fg_color=dbc)
    update_window.resizable(False, False)
    update_window.grab_set()
    
    ctk.CTkLabel(update_window, text="Update Profile", font=("Georgia", 25, "bold"), text_color="white").place(x=230, y=10)
    if patient_data[7] and os.path.exists(patient_data[7]):
        pil_img = Image.open(patient_data[7])
        ctk_img = CTkImage(pil_img, size=(120, 120))
        uploaded_photo_label = ctk.CTkLabel(update_window,image=ctk_img, text="", width=220, height=120, corner_radius=60, fg_color="white")
        uploaded_photo_label.place(x=200, y=60)
    else:
        uploaded_photo_label = ctk.CTkLabel(update_window, text="", width=220, height=120, corner_radius=60, fg_color="white")
        uploaded_photo_label.place(x=200, y=60)

    profile_image_path=patient_data[7]
    def upload_photo():
        global profile_image
        nonlocal profile_image_path
        file_path = filedialog.askopenfilename(filetypes=[("Image files", ".png;.jpg;*.jpeg")])
        if file_path:
            profile_image_path = file_path
            image = Image.open(file_path).resize((120, 120))          # resize to label size
            profile_image = ctk.CTkImage(light_image=image, size=(120,120))  # same size here
            uploaded_photo_label.configure(image=profile_image)
            uploaded_photo_label.image = profile_image  # prevent garbage collection
    print("xyz",patient_data[7])
    print("abc",profile_image_path)
    ctk.CTkButton(update_window, text="Upload Photo", command=upload_photo, width=160).place(x=230, y=190)

    fields = {
        "Name": patient_data[0],
        "Gender": patient_data[1],
        "DOB": patient_data[2],
        "Contact": patient_data[3],
        "Email": patient_data[4],
        "Blood Group": patient_data[5],
        "Address": patient_data[6],
    }

    entries = {}
    y_position = 240
    for field, field_value in fields.items():
        label = ctk.CTkLabel(update_window, text=field, font=("Arial", 18, "bold"), text_color="white")
        label.place(x=50, y=y_position)

        if field == "Gender":
            entry = ctk.CTkComboBox(update_window, values=["Male", "Female", "Other"], width=280, font=("Arial", 14))
            if field_value:
                entry.set(field_value)
            else:
                entry.set("Select Gender")
        elif field == "Blood Group":
            entry = ctk.CTkComboBox(update_window, values=["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"], width=280, font=("Arial", 14))
            if field_value:
                entry.set(field_value)
            else:
                entry.set("Select Blood Group")
        else:
            entry = ctk.CTkEntry(update_window, font=("Arial", 14), width=280, corner_radius=5, text_color="black")
            if field_value:
                entry.insert(0, str(field_value))
            else:
                entry.configure(placeholder_text=f"Enter {field}")
        entry.place(x=200, y=y_position)
        entries[field] = entry

        y_position += 60  # Increase y position for next widget

    def save_changes():
        try:
            updated_values = {field: e.get().strip() for field, e in entries.items()}
            email_regx = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
            contact_number_regx = r"^\d{10}$"

            # Extract fields
            name = updated_values["Name"]
            dob_str = updated_values["DOB"]
            address = updated_values["Address"]

            # --- Name Validation ---
            if not name.replace(" ", "").isalpha():
                messagebox.showerror("Invalid Input", "Name must contain only letters.", parent=update_window)
                return

            # --- DOB Format Validation ---
            try:
                dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror("Invalid Input", "DOB must be in YYYY-MM-DD format.", parent=update_window)
                return

            # --- Age Calculation ---
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 18:
                messagebox.showerror("Invalid Age", "User must be at least 18 years old.", parent=update_window)
                return

            # --- Address Validation ---
            if len(address) < 3 or not any(c.isalnum() for c in address):
                messagebox.showerror("Invalid Input", "Please enter a valid address.", parent=update_window)
                return

            # --- Email & Contact Validation ---
            if not re.match(email_regx, updated_values["Email"]):
                messagebox.showerror("Invalid Input", "Invalid email address.", parent=update_window)
                return

            if not re.match(contact_number_regx, updated_values["Contact"]):
                messagebox.showerror("Invalid Input", "Contact number must be 10 digits.", parent=update_window)
                return

            # --- Safe Name Split ---
            name_parts = name.split()
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            # --- SQL Update ---
            cursor.execute("""
                UPDATE patients
                SET first_name=%s, last_name=%s, gender=%s, dob=%s, contact_number=%s,
                    email=%s, blood_group=%s, address=%s, image=%s
                WHERE patient_id=%s
            """, (
                first_name,
                last_name,
                updated_values["Gender"],
                dob_str,
                updated_values["Contact"],
                updated_values["Email"],
                updated_values["Blood Group"],
                address,
                profile_image_path,
                value
            ))

            connection.commit()
            messagebox.showinfo("Success", "Profile updated successfully!", parent=update_window)
            refresh_patient_info(value)
            update_window.destroy()

        except KeyError as ke:
            messagebox.showerror("Error", f"Missing field: {ke}", parent=update_window)

        except pymysql.MySQLError as db_err:
            messagebox.showerror("Database Error", f"Database error occurred:\n{db_err}", parent=update_window)

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}", parent=update_window)


    def request_account_deletion(patient_id):
        """Function for patient to request account deletion"""
        
        # Create deletion request window
        request_window = ctk.CTkToplevel()
        request_window.geometry("500x600")
        request_window.title("Request Account Deletion")
        request_window.configure(fg_color=dbc)
        request_window.resizable(False, False)
        request_window.grab_set()
        
        # Title
        ctk.CTkLabel(request_window, text="Request Account Deletion", 
                    font=("Georgia", 20, "bold"), text_color="white").pack(pady=20)
        
        # Warning message
        warning_text = """⚠ WARNING ⚠
        
    Requesting account deletion will:
    • Remove all your medical records
    • Cancel all future appointments
    • Delete your personal information
    • This action cannot be undone

    Your request will be reviewed by a doctor
    before final deletion."""
        
        ctk.CTkLabel(request_window, text=warning_text, 
                    font=("Arial", 14), text_color="#FFB6C1", 
                    justify="left").pack(pady=10, padx=20)
        
        # Reason for deletion
        ctk.CTkLabel(request_window, text="Reason for deletion (required):", 
                    font=("Arial", 14, "bold"), text_color="white").pack(pady=(20, 5))
        
        reason_textbox = ctk.CTkTextbox(request_window, width=450, height=100,
                                    font=("Arial", 12))
        reason_textbox.pack(pady=5, padx=20)
        
        def submit_deletion_request():
            reason = reason_textbox.get("1.0", "end-1c").strip()
            
            if not reason:
                messagebox.showerror("Error", "Please provide a reason for deletion", 
                                parent=request_window)
                return
            
            if len(reason) < 10:
                messagebox.showerror("Error", "Please provide a more detailed reason (minimum 10 characters)", 
                                parent=request_window)
                return
            
            # Confirm the request
            confirm = messagebox.askyesno("Confirm Request", 
                                        "Are you sure you want to submit this deletion request?\n\n" +
                                        "You will receive notification once a doctor reviews your request.",
                                        parent=request_window)
            
            if confirm:
                try:
                    connection = pymysql.connect(host='localhost', user='root', password='root', database='clinic_management')
                    cursor = connection.cursor()
                    
                    # Get patient name
                    cursor.execute("SELECT CONCAT(first_name, ' ', last_name) FROM patients WHERE patient_id = %s", (patient_id,))
                    patient_name = cursor.fetchone()[0]
                    
                    # Insert deletion request
                    cursor.execute("""
                        INSERT INTO patient_deletion_requests 
                        (patient_id, patient_name, reason_for_deletion) 
                        VALUES (%s, %s, %s)
                    """, (patient_id, patient_name, reason))
                    
                    connection.commit()
                    cursor.close()
                    connection.close()
                    
                    messagebox.showinfo("Request Submitted", 
                                    "Your account deletion request has been submitted successfully.\n\n" +
                                    "A doctor will review your request and you will be notified of the decision.",
                                    parent=request_window)
                    
                    request_window.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to submit request: {str(e)}", 
                                    parent=request_window)
        
        def cancel_request():
            request_window.destroy()
        
        # Buttons
        button_frame = ctk.CTkFrame(request_window, fg_color="transparent")
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame, text="Submit Request", command=submit_deletion_request,
                    fg_color="#dc3545", hover_color="#c82333", width=150).pack(side="left", padx=10)
        
        ctk.CTkButton(button_frame, text="Cancel", command=cancel_request,
                    fg_color="#6c757d", hover_color="#5a6268", width=150).pack(side="left", padx=10)


    # Buttons frame for better layout
    button_frame_y = 660
    
    # Save button
    ctk.CTkButton(
        update_window, 
        text="Save Changes", 
        command=save_changes, 
        width=180, 
        height=35,
        fg_color="#28a745",
        hover_color="#218838"
    ).place(x=120, y=button_frame_y)
    
    # Delete button
    ctk.CTkButton(
        update_window, 
        text="Delete Account", 
        command=lambda :request_account_deletion(value), 
        width=180, 
        height=35,
        fg_color="#dc3545",
        hover_color="#c82333"
    ).place(x=320, y=button_frame_y)


def logoutaction():
    app.destroy()
    cursor.execute("Update patient_login_history set logout_time=%s where patient_id=%s", (datetime.now(), value))
    conn.commit()
    
# Logout Button
# --- Shadow Frame behind the button ---
logout_shadow_frame = ctk.CTkFrame(
    app,
    width=168,
    height=55,
    corner_radius=20,
    fg_color="black"
)
logout_shadow_frame.place(x=45, y=705)  # Slight offset for shadow

# --- Load and convert image to CTkImage ---
logout_image_path = "Clinic_System/build/logout.png"  # 🔁 Replace with your image path
logout_img = Image.open(logout_image_path)
logout_icon = ctk.CTkImage(light_image=logout_img, dark_image=logout_img, size=(40, 40))

# --- LOG OUT Button ---
logout_button = ctk.CTkButton(
    app,
    text="LOG OUT",
    image=logout_icon,
    compound="right",  # ✅ Image on right
    font=("Georgia", 18, "bold"),  # Same as Update button
    width=150,
    height=55,
    corner_radius=20,
    fg_color=mbc,  # Same background color as Update button
    text_color="black",
    hover_color="#0B2E52",
    command=logoutaction
)
logout_button.place(x=40, y=700)

# # Update Button
# ctk.CTkButton(
#     app, text=" Update Profile", font=("Georgia", 14, "bold"), width=130, height=40,
#     corner_radius=20, fg_color="#1C3D64", text_color="white",
#     hover_color="#0B2E52", command=lambda: open_update_window(value)
# ).place(x=40, y=700)


# --- Shadow Frame behind the button ---
shadow_frame = ctk.CTkFrame(
    app,
    width=210,
    height=55,
    corner_radius=20,
    fg_color="black"
)
shadow_frame.place(x=905, y=705)  # Slight offset for shadow

# --- Load and convert image to CTkImage ---
image_path = "Clinic_System/build/profilebutton.png"  # ✅ Your icon path
img = Image.open(image_path)
button_icon = ctk.CTkImage(light_image=img, dark_image=img, size=(40, 40))



bot_icon_path = "Clinic_System/build/ai.png" 
try:
    bot_img = Image.open(bot_icon_path)
    bot_icon = ctk.CTkImage(light_image=bot_img, dark_image=bot_img, size=(65,63))
    
    ctk.CTkFrame(
    app,
    width=205,
    height=72,
    corner_radius=30,   # Must match button's radius
    fg_color="black"    # Shadow color
    ).place(x=920+4, y=90+4)
    
    clinic_bot_button = ctk.CTkButton(
        app,
        text="Need Help!!",  # No text, just the icon
        text_color= "black",
        font=("arial" , 15),
        image=bot_icon,
        width=65,   # Circular button
        height=65,
        corner_radius=30, # Half of width/height for a circle
        fg_color=mbc,     # Use your theme color
        hover_color=hbc,  # Use your theme hover color
        command=open_clinic_bot
    )
    # Position it in the bottom-right corner
    clinic_bot_button.place(x=920, y=90) 

except FileNotFoundError:
    print(f"Error: Chatbot icon not found at {bot_icon_path}")
    # Fallback to a text button if icon is missing
    clinic_bot_button = ctk.CTkButton(
        app,
        text="?",
        font=("Georgia", 24, "bold"),
        width=60,
        height=60,
        corner_radius=30,
        fg_color=mbc,
        hover_color=hbc,
        command=open_clinic_bot
    )
    clinic_bot_button.place(x=1400, y=90)
# --- Update Button with CTkImage ---
update_button = ctk.CTkButton(
    app,
    text="Update Profile",
    image=button_icon,
    compound="right",  # ✅ Image on right side
    font=("Georgia", 18, "bold"),
    width=150,
    height=55,
    corner_radius=20,
    fg_color=mbc,
    text_color="black",
    hover_color="#0B2E52",
    command=lambda: open_update_window(value)
)
update_button.place(x=900, y=700)

app.mainloop()