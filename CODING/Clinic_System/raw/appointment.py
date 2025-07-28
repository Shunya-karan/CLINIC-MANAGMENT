import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from PIL import Image
import pymysql
from datetime import datetime
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from tkinter import filedialog
from reportlab.lib.utils import ImageReader
from tkcalendar import DateEntry
from datetime import datetime
from datetime import date


dbc = "#07002B"
mbc = "blue"
lbc = "#4EBEFA"
hbc = "#1A2750"
# DATABASE CONNECTION
def Database_Connections():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="clinic_management"
    )


# NAVIGATION BAR
def create_navigation_bar(parent):
    def on_refresh_enter(event):
        refresh_label.configure(text_color="grey")
    def on_refresh_leave(event):
        refresh_label.configure(text_color="Black")

    nav_frame = ctk.CTkFrame(parent, width=1500, height=70, fg_color=("#4EBEFA", "#294B82"),corner_radius=0)
    nav_frame.pack(side="top", fill="x")
    header = ctk.CTkLabel(nav_frame, text="APPOINTMENT", font=("ALgerian", 40), text_color="black")
    header.place(x=630, y=5)

    refresh_label = ctk.CTkLabel(nav_frame, text="🔄", text_color="Black", font=("Segoe UI", 40), cursor="hand2")
    refresh_label.place(x=1440, y=5)
    refresh_label.bind("<Enter>", on_refresh_enter)
    refresh_label.bind("<Leave>", on_refresh_leave)
    refresh_label.bind("<Button-1>", lambda event: show_table())

    global large_font
    large_font = ctk.CTkFont(family="Helvetica", size=15)

    def on_enter(event):
        back_label.configure(text_color="grey") 

    def on_leave(event):
        back_label.configure(text_color="black")  
    
    back_label = ctk.CTkLabel(nav_frame, text="🔙", text_color="black", font=("Calibri", 40), cursor="hand2")
    back_label.place(x=5, y=5)

   
    back_label.bind("<Enter>", on_enter) 
    back_label.bind("<Leave>", on_leave) 

    back_label.bind("<Button-1>", lambda event: pateintwindowdestroy())

    return nav_frame

def mark_appointment_scheduled(appointment_id):
    mydb = Database_Connections()
    mycursor = mydb.cursor()

    try:
        mycursor.execute("""
            UPDATE appointments 
            SET status = 'Scheduled' 
            WHERE appointment_id = %s
        """, (appointment_id,))
        mydb.commit()
        messagebox.showinfo("Success", f"Appointment {appointment_id} marked as Completed.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update status: {e}")
    finally:
        mycursor.close()
        mydb.close()

#TABLE VIEWING
def show_table():
    
    def mark_selected_scheduled():
        selected_ids = []

        for item_id, checked in checkbox_states.items():
            if checked:
                appt_id = table.item(item_id, "values")[0]  # assuming appointment ID is first
                selected_ids.append(appt_id)

        if not selected_ids:
            messagebox.showwarning("No Selection", "Please select at least one appointment.")
            return

        for appt_id in selected_ids:
            mark_appointment_scheduled(appt_id)

        show_table()  

    """Displays a table with patient information and a selectable checkbox."""
    mydb = Database_Connections()
    mycursor = mydb.cursor()
    mycursor.execute("""SELECT 
            a.appointment_id AS 'Appointment ID',
            MAX(CONCAT(p.first_name, ' ', p.last_name)) AS 'Name',
            MAX(TIMESTAMPDIFF(YEAR, p.dob, CURDATE())) AS 'Age',
            MAX(p.gender) AS 'Gender',
            MAX(p.contact_number) AS 'Contact No.',
            MAX(p.blood_group) AS 'Blood Group',
            MAX(v.diagnosis) AS 'Diagnosis',
            GROUP_CONCAT(DISTINCT CONCAT(m.medicine_name, ' (', pi.dosage, ')') SEPARATOR ', ') AS 'Medicines',
            GROUP_CONCAT(DISTINCT pr.notes SEPARATOR '; ') AS 'Notes',
            MAX(a.appointment_date) AS 'Appointment Date',
            MAX(a.appointment_time) AS 'Time',
            MAX(b.total_amount) AS 'Bill',
            a.status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        LEFT JOIN visits v ON a.appointment_id = v.appointment_id
        LEFT JOIN prescriptions pr ON v.visit_id = pr.visit_id
        LEFT JOIN prescription_items pi ON pr.prescription_id = pi.prescription_id
        LEFT JOIN medicines m ON pi.medicine_id = m.medicine_id
        LEFT JOIN billing b ON a.appointment_id = b.appointment_id
        GROUP BY a.appointment_id;
        """ )
    myresult = mycursor.fetchall()

    global table, checkbox_states, medicine_text

    for widget in Patientwindow.winfo_children():
        if isinstance(widget, ttk.Frame):  
            widget.destroy()

    table_frame = ttk.Frame(Patientwindow)
    table_frame.pack(fill="both", expand=True, padx=20, pady=20)

    style = ttk.Style()
    style.configure("Treeview", font=("Helvetica", 12))  #  table text size
    style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))  #  heading font size        

    columns = ("Appointment ID", "Name", "Age", "Gender", "Contact No.", "Blood Group", 
           "Diagnosis", "Medicines", "Notes", "Appointment Date", "Time", "Bill", "Status", "Select")

    table = ttk.Treeview(table_frame, columns=columns, show="headings", style="Custom.Treeview")
    style.map("Treeview", background=[("selected", "#007acc")])
    table.tag_configure("oddrow", background="#e6f2ff")
    table.tag_configure("evenrow", background="#ffffff")

    for col in columns:
        table.heading(col, text=col)
        table.column(col, anchor="center", minwidth=100, width=150)

    for mad in ["Medicines","Appointment Date","Diagnosis"]:
            table.column(mad, width=230)  
            table.tag_configure("light_green", background="#67C2FB")  
            table.tag_configure("white", background="white") 


    for index, i in enumerate(myresult):
        tag = "light_green" if index % 2 == 0 else "white"  # Alternate row colors
        table.insert('', 'end', values=(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8],i[9],i[10],i[11],i[12],"❌"), tags=(tag,))

    checkbox_states = {}

    def toggle_checkbox(event):
        """Toggles checkbox icon in the 13th column (✔ / ❌) on click."""
        item_id = table.identify_row(event.y)
        col_id = table.identify_column(event.x)

        if item_id and col_id == "#14":  # column "#13" means 13th visible column (index 12)
            values = list(table.item(item_id, "values"))
            current_value = values[13]  # index 12 for the 13th column
            new_value = "✔" if current_value == "❌" else "❌"
            values[13] = new_value
            table.item(item_id, values=values)
            checkbox_states[item_id] = (new_value == "✔")


    def show_medicine_details(event):
        """Displays full medicine details and notes with a scrollbar in a separate widget."""
        selected_item = table.selection()
        if not selected_item:
            return

        item_values = table.item(selected_item[0], "values")
        
        medicines = item_values[7]  # Medicines column
        notes = item_values[8]      # Notes column

        full_text = f"Medicines:\n{medicines}\n\nAdditional Notes:\n{notes}"

        medicine_text.config(state="normal")
        medicine_text.delete("1.0", tk.END)
        medicine_text.insert("1.0", full_text)
        medicine_text.config(state="disabled")

    def show_patients_details_pdf():
        selected_item = table.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select Patient")
            return
 
        # Unpack patient values
        item_values = table.item(selected_item[0], "values")
        item_values = item_values[:13]  # Only take the first 11 values

        (
            appt_id, patient_name, patient_age, patient_gender,
            patient_phone, patient_bloodgrp, patient_disease,
            patient_medicine_details,Additional_note, patient_appointment_date,
            patient_appointment_time, total_bill,status
        ) = item_values

        mydb=Database_Connections()
        mycursor=mydb.cursor()
        # Fetch patient ID from DB
        mycursor.execute("""
            SELECT p.patient_id 
            FROM patients p 
            JOIN appointments a ON p.patient_id = a.patient_id 
            WHERE a.appointment_id = %s
        """, (appt_id,))
        patient_result = mycursor.fetchone()
        patient_id = patient_result[0] if patient_result else "N/A"
        print(patient_id)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"{patient_name}_{appt_id}.pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not file_path:
            return

        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter

        # Draw light blue background
        c.setFillColorRGB(0.88, 0.95, 1)  # Light blue
        c.rect(0, 0, width, height, fill=1)

        # Clinic Logo
        try:
            logo = ImageReader("Clinic_System/build/clinic-logo.png")
            c.drawImage(logo, 40, height - 100, width=80, height=80, mask='auto')
        except:
            pass  # Ignore if logo not found

        # Heading
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(colors.darkblue)
        c.drawString(150, height - 60, "")

        c.setFont("Helvetica-Bold", 18)
        c.drawString(150, height - 90, "Patient Report")

        # Right side Patient ID
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.black)
        c.drawString(width - 200, height - 90, f"Patient ID: {patient_id}")


        c.setStrokeColor(colors.darkblue)
        c.setLineWidth(1.5)
        c.line(40, height - 100, width - 40, height - 100)

        # Table Content
        c.setFont("Helvetica", 12)
        table_data = [
            ["Field", "Value"],
            ["Appointment ID", appt_id],
            ["Name", patient_name],
            ["Age", patient_age],
            ["Gender", patient_gender],
            ["Phone", patient_phone],
            ["Blood Group", patient_bloodgrp],
            ["Diagnosis", patient_disease],
            ["Appointment Date", patient_appointment_date],
            ["Appointment Time", patient_appointment_time],
            ["Total Bill", total_bill],
            ["Status",status]
        ]

        # Column positions
        x_start = 60
        y_start = height - 140
        row_height = 25
        col1_width = 160
        col2_width = 370

        # Draw table
        c.setStrokeColor(colors.black)
        for row_num, row in enumerate(table_data):
            y = y_start - row_num * row_height
            c.setFillColor(colors.white if row_num == 0 else colors.black)
            c.rect(x_start, y - row_height, col1_width, row_height, stroke=1, fill=row_num == 0)
            c.rect(x_start + col1_width, y - row_height, col2_width, row_height, stroke=1, fill=row_num == 0)
            c.setFillColor(colors.black)
            c.drawString(x_start + 5, y - 17, str(row[0]))
            c.drawString(x_start + col1_width + 5, y - 17, str(row[1]))

                # Draw multiline sections for medicine and notes
        multiline_y = y_start - (len(table_data) + 1) * row_height - 30  # below the table

        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_start, multiline_y, "Medicine Details:")
        c.setFont("Helvetica", 11)

        # Draw medicine details wrapped
        text = c.beginText(x_start, multiline_y - 15)
        text.setFont("Helvetica", 11)
        for line in patient_medicine_details.split('\n'):
            text.textLine(line)
        c.drawText(text)

        # Draw additional notes
        note_start_y = text.getY() - 25
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_start, note_start_y, "Additional Notes:")
        c.setFont("Helvetica", 11)

        text = c.beginText(x_start, note_start_y - 15)
        text.setFont("Helvetica", 11)
        for line in Additional_note.split('\n'):
            text.textLine(line)
        c.drawText(text)

        # Signature Image (bottom-right)
        signature_y = 100
        signature_x = width - 200
        c.setFont("Helvetica-Bold", 12)
        c.drawString(signature_x, signature_y + 40, "Signature:")

        try:
            signature_img = ImageReader("Clinic_System/build/Signature.png")
            c.drawImage(signature_img, signature_x, signature_y, width=120, height=30, mask='auto')
        except Exception as e:
            print(f"Signature image not found or error: {e}")
            # fallback rectangle if image not found
            c.rect(signature_x, signature_y, 120, 30, stroke=1, fill=0)


        # Footer
        c.setFont("Helvetica", 8)
        c.drawString(50, 30, f"Generated on: {datetime.now().strftime('%d-%m-%Y %I:%M %p')}")

        c.save()
        messagebox.showinfo("Success", f"PDF saved as {file_path}")

#-----  END OF PDF GENERATION CODE -----#
#--- buttons ---#
    # === Global button settings ===
    BUTTON_WIDTH = 150
    BUTTON_HEIGHT = 30
    BUTTON_RADIUS = 8
    BUTTON_FONT = ("Calibri", 18)
    BUTTON_TEXT_COLOR = "white"
    BUTTON_BORDER_WIDTH = 0.5
    SHADOW_COLOR = "black"
    SHADOW_OFFSET = 6
        # Color scheme
    mbc = "#1f6aa5"   # main button color
    hbc = "#155a8a"   # hover color
    dbc = "#f9a825" 
    def create_shadow_button(parent, x, y, width, text, command, fg_color, hover_color, text_color="white", font=BUTTON_FONT, border=BUTTON_BORDER_WIDTH):
        # Shadow
        ctk.CTkFrame(parent, corner_radius=BUTTON_RADIUS, width=width, height=BUTTON_HEIGHT, fg_color=SHADOW_COLOR)\
            .place(x=x + SHADOW_OFFSET, y=y + SHADOW_OFFSET)

        # Button
        ctk.CTkButton(parent, width=width, height=BUTTON_HEIGHT, text=text, command=command,
                    font=font, fg_color=fg_color, text_color=text_color,
                    corner_radius=BUTTON_RADIUS, border_width=border, hover_color=hover_color)\
            .place(x=x, y=y)

    buttons_config = [
    {"x": 650, "y": 15, "text": "Prescription", "command": update_patient, "fg_color": mbc, "hover_color": hbc},
    {"x": 820, "y": 15, "text": "Add Appointment", "command": add_appointment, "fg_color": mbc, "hover_color": hbc},
    {"x": 990, "y": 15, "width": 170, "text": "Cancel Appointment", "command": delete_appointments, "fg_color": "red", "hover_color": "darkred"},
    {"x": 1180, "y": 15, "text": "Mark Scheduled", "command": mark_selected_scheduled, "fg_color": dbc, "hover_color": "#e89c00"},
    {"x": 1350, "y": 15, "text": "Generate PDF", "command": show_patients_details_pdf, "fg_color": "lightgreen", "hover_color": "darkgreen", "text_color": "black"}
]

    for btn in buttons_config:
        create_shadow_button(
            parent=search_frame,
            x=btn["x"],
            y=btn["y"],
            width=btn.get("width", BUTTON_WIDTH),
            text=btn["text"],
            command=btn["command"],
            fg_color=btn["fg_color"],
            hover_color=btn["hover_color"],
            text_color=btn.get("text_color", BUTTON_TEXT_COLOR),
            font=btn.get("font", BUTTON_FONT),
            border=btn.get("border", BUTTON_BORDER_WIDTH)
        )

    # Bind events
    table.bind("<Button-1>", toggle_checkbox)
    table.bind("<<TreeviewSelect>>", show_medicine_details)  # Update medicine details on selection

    # Create Scrollbars
    x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=table.xview)
    y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)

    table.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)

    y_scroll.pack(side="right", fill="y")
    x_scroll.pack(side="bottom", fill="x")
    table.pack(fill="both", expand=True)

    # Create a frame for the medicine details box
    medicine_frame = ttk.Frame(Patientwindow)
    medicine_frame.pack(fill="x", padx=20, pady=10)

    ttk.Label(medicine_frame, text="Selected Patient's Medicines:", font=("Helvetica", 12, "bold")).pack(anchor="w")

    # Create a Text widget for medicine details with scrollbar
    medicine_text = tk.Text(medicine_frame, wrap="word", height=5, font=("Helvetica", 13))
    medicine_text.pack(side="left", fill="x", expand=True)

    medicine_scroll = ttk.Scrollbar(medicine_frame, orient="vertical", command=medicine_text.yview)
    medicine_text.configure(yscrollcommand=medicine_scroll.set)

    medicine_scroll.pack(side="right", fill="y")

# Function to delete selected patients
def delete_appointments():
    """Deletes selected appointments and their related records, but NOT patients."""

    selected_items = [item_id for item_id, checked in checkbox_states.items() if checked]
    if not selected_items:
        messagebox.showerror("Error", "No appointments selected for Cancelation.")
        return

    confirm = messagebox.askyesno("Confirm Cancel", "Are you sure you want to Cancel the selected appointments?")
    if not confirm:
        return

    try:
        mydb = Database_Connections()
        mycursor = mydb.cursor()

        appointment_ids = []
        completed_appointments = []
        
        for item_id in selected_items:
            row_values = table.item(item_id, "values")
            appointment_id = row_values[0]  # Assuming appointment_id is at index 0
            
            # Check current status before adding to cancellation list
            mycursor.execute("SELECT status FROM appointments WHERE appointment_id = %s", (appointment_id,))
            result = mycursor.fetchone()
            
            if result:
                current_status = result[0]
                if current_status.lower() == 'completed':
                    completed_appointments.append(appointment_id)
                else:
                    appointment_ids.append(appointment_id)

        # Show warning if any completed appointments were selected
        if completed_appointments:
            if len(completed_appointments) == len(selected_items):
                messagebox.showwarning("Cannot Cancel", 
                    "All selected appointments are already completed and cannot be cancelled.")
                mydb.close()
                return
            else:
                messagebox.showwarning("Partial Cancellation", 
                    f"{len(completed_appointments)} appointment(s) are completed and cannot be cancelled. "
                    f"Only {len(appointment_ids)} appointment(s) will be cancelled.")

        # Cancel the remaining appointments
        if appointment_ids:
            for appt_id in appointment_ids:
                mycursor.execute("""
                    UPDATE appointments 
                    SET status = 'Cancelled' 
                    WHERE appointment_id = %s
                """, (appt_id,))

            mydb.commit()
            messagebox.showinfo("Cancelled", f"{len(appointment_ids)} appointment(s) cancelled successfully.")
        
        mydb.close()

    except Exception as e:
        messagebox.showerror("Error", str(e))
        if 'mydb' in locals():
            mydb.close()

selected_vars = {}  
def update_patient():
    """Updates patient details based on user input."""
    app_id_to_update = ctk.CTkInputDialog(title="Update Patient", text="Enter the Appointment ID:").get_input()
    if not app_id_to_update:
        messagebox.showerror("Error", "Please enter the Appointment ID.")
        return
    mydb = Database_Connections()
    mycursor = mydb.cursor()

    mycursor.execute("SELECT visit_id FROM visits WHERE appointment_id = %s", (app_id_to_update,))
    visit_result = mycursor.fetchone()
    if not visit_result:
        messagebox.showerror("Error", " No Appointment found for the given appointment ID.")
        return
    
    mycursor.execute("""select concat(first_name," " ,last_name),MAX(TIMESTAMPDIFF(YEAR, p.dob, CURDATE())) AS 'Age',
            MAX(p.gender) AS 'Gender',
            MAX(p.contact_number) AS 'Contact No.',
            MAX(p.blood_group) AS 'Blood Group',MAX(a.appointment_date) AS 'Appointment Date',
            MAX(a.appointment_time) AS 'Time'
            from patients p join appointments a on a.patient_id=p.patient_id
            where a.appointment_id=%s;""", (app_id_to_update,))
    row = mycursor.fetchone()
    if row is None:
        messagebox.showerror("Error", "Patient not found.")
        return
    appointment_date=row[5]
    if appointment_date != date.today():
        messagebox.showwarning("Invalid Date", f"This appointment is scheduled for {appointment_date}, not today.")
        return
        
    width = Patientwindow.winfo_screenwidth()
    height = Patientwindow.winfo_screenheight()
    update_window = ctk.CTk()
    update_window.title("Update Patient Details")
    update_window.geometry(f"{width}x{height}+0+0")
    update_window.configure(fg_color="#4EBEFA")

    inner_frame = ctk.CTkFrame(update_window, fg_color="white", corner_radius=15, width=650, height=1050)
    inner_frame.place(x=width//2 - 325, y=30)

    heading_frame = ctk.CTkFrame(inner_frame, fg_color="#07002B", corner_radius=10, width=250, height=40)
    heading_frame.place(x=200, y=20)

    title_label = ctk.CTkLabel(heading_frame, text="Update Appointment", font=("Arial", 16, "bold"), text_color="white")
    title_label.place(relx=0.5, rely=0.5, anchor="center")

    labels = ["Name", "Age", "Gender", "Contact Number", "Blood Group","Appointment date", "Appointment Time"]
    entries = {}


    data = row
    y_start = 80
    for i, (label_text, value) in enumerate(zip(labels, data)):
        field_label = ctk.CTkLabel(inner_frame, text=label_text + ":", font=("Arial", 14, "bold"), text_color="black")
        field_label.place(x=50, y=y_start + i * 60)

        value_label = ctk.CTkLabel(inner_frame, text=str(value), font=("Arial", 14), text_color="black",
                                   fg_color="#E6F4F1", corner_radius=8, width=280, height=30)
        value_label.place(x=250, y=y_start + i * 60)
        entries[label_text] = value_label

    mycursor.execute("SELECT v.diagnosis FROM visits v WHERE appointment_id = %s;", (app_id_to_update,))
    diagnosiss = mycursor.fetchone()
    diagnosiss = diagnosiss[0] if diagnosiss and diagnosiss[0] is not None else ""


    diagnosis_label=ctk.CTkLabel(inner_frame,text="Diagnosiss",font=("Arial",14,"bold"),text_color="black")
    diagnosis_label.place(x=50,y=y_start+len(labels)*60-10)
    diagnosis_entry=ctk.CTkEntry(inner_frame,placeholder_text="Diagnosis",font=("Arial",14),text_color="black",width=280)
    diagnosis_entry.insert(0, str(diagnosiss) if diagnosiss else "No Diagnosis")
    diagnosis_entry.place(x=250,y=y_start+len(labels)*60-10)

    # Create Notes textbox (after creating the widget)
    notes_label = ctk.CTkLabel(inner_frame, text="Additional Notes", font=("Arial", 14, "bold"), text_color="black")
    notes_label.place(x=50, y=y_start + len(labels) * 60 + 100)
    notes_textbox = ctk.CTkTextbox(inner_frame, height=50, width=280, corner_radius=10, fg_color="#8ca5cd")
    notes_textbox.place(x=250, y=y_start + len(labels) * 60 + 100)

    # Create Medicine textbox
    medicine_label = ctk.CTkLabel(inner_frame, text="Select Medicines", font=("Arial", 14, "bold"), text_color="black")
    medicine_label.place(x=50, y=y_start + len(labels) * 60 + 50)
    medicine_textbox = ctk.CTkTextbox(inner_frame, height=50, width=280, fg_color="#95b89e", state="disabled")
    medicine_textbox.place(x=250, y=y_start + len(labels) * 60 + 30)

    # --- Fetch existing prescriptions ---
    mycursor.execute("SELECT visit_id FROM visits WHERE appointment_id = %s", (app_id_to_update,))
    visit_row = mycursor.fetchone()
    visit_id = visit_row[0] if visit_row else None

    existing_prescription_id = None
    selected_medicines = {}

    if visit_id:
        mycursor.execute("SELECT prescription_id, notes FROM prescriptions WHERE visit_id = %s", (visit_id,))
        presc_row = mycursor.fetchone()
        if presc_row:
            existing_prescription_id, existing_notes = presc_row
            notes_textbox.insert("1.0", existing_notes or "")
        else:
            notes_textbox.insert("1.0", "")

    # Prefill selected_medicines from prescription_items
    if existing_prescription_id:
        mycursor.execute("""
            SELECT m.medicine_name, pi.dosage 
            FROM prescription_items pi 
            JOIN medicines m ON m.medicine_id = pi.medicine_id 
            WHERE pi.prescription_id = %s
        """, (existing_prescription_id,))
        med_rows = mycursor.fetchall()
        for name, dosage in med_rows:
            selected_medicines[name] = dosage

    # Prefill medicine textbox display
    prefill_text = ""
    for med, dose in selected_medicines.items():
        prefill_text += f"{med} ({dose})\n"
    medicine_textbox.configure(state="normal")
    medicine_textbox.insert("1.0", prefill_text.strip())
    medicine_textbox.configure(state="disabled")

    medicine_text = medicine_textbox.get("1.0", "end").strip()
    selected_medicines = {}
    if medicine_text:
        for line in medicine_text.split("\n"):
            line = line.strip()
            if not line:
                continue
            # parse line like "Paracetamol (2 doses/day)"
            match = re.match(r"^(.*?)\s*\((.*?)\)$", line)
            if match:
                med_name = match.group(1).strip()
                dosage = match.group(2).strip()
            else:
                med_name = line.strip()
                dosage = "None"
            selected_medicines[med_name] = dosage
    else:
        selected_medicines = {}
    mycursor.execute("SELECT medicine_name FROM medicines ORDER BY medicine_name")
    medicine_list = [row[0] for row in mycursor.fetchall()]

    def add_medicine():
        medicine_window = ctk.CTkToplevel()
        medicine_window.title("Select Medicines")
        medicine_window.geometry("500x900")
        medicine_window.configure(fg_color="#A7ECAF")
        medicine_textbox.configure(state="normal")

        global selected_vars  # Keep selected_vars to track widgets state
        selected_vars = {}

        dosage_options = ["None", "1 dose/day", "2 doses/day", "3 doses/day", "Before sleep", "After meal"]

        for med in medicine_list:
            # Check if this medicine was previously selected
            is_selected = med in selected_medicines
            dosage_val = selected_medicines.get(med, "None")

            checkbox_var = ctk.BooleanVar(value=is_selected)
            row_frame = ctk.CTkFrame(medicine_window, fg_color="transparent")
            row_frame.pack(fill="x", pady=5, padx=10)

            checkbox = ctk.CTkCheckBox(row_frame, text=med, variable=checkbox_var)
            checkbox.pack(side="left", padx=10)

            dosage_menu = ctk.CTkOptionMenu(row_frame, values=dosage_options, width=180)
            dosage_menu.set(dosage_val)
            dosage_menu.pack(side="right", padx=10)

            selected_vars[med] = {"var": checkbox_var, "dosage": dosage_menu}

        def update_textbox():
            selected_text = ""
            for med, widgets in selected_vars.items():
                if widgets["var"].get():
                    dosage = widgets["dosage"].get().strip()
                    dosage_text = f" ({dosage})" if dosage != "None" else ""
                    selected_text += f"{med}{dosage_text}\n"
            medicine_textbox.delete("1.0", "end")
            medicine_textbox.insert("end", selected_text.strip())
            medicine_textbox.configure(state="disabled")

        def confirm_action():
            # Update selected_medicines dict with current selections
            selected_medicines.clear()
            for med, widgets in selected_vars.items():
                if widgets["var"].get():
                    selected_medicines[med] = widgets["dosage"].get().strip()
            update_textbox()
            medicine_window.destroy()
        clear_button = ctk.CTkButton(medicine_window, text="Clear All", fg_color="red", command=lambda: clear_selections())
        clear_button.pack(pady=10)

        def clear_selections():
            for med, widgets in selected_vars.items():
                widgets["var"].set(False)
                widgets["dosage"].set("None")
        # Confirm button
        confirm_button = ctk.CTkButton(medicine_window, text="Confirm", command=confirm_action)
        confirm_button.pack()


    add_medicine_button = ctk.CTkButton(inner_frame, text="Add Medicine", command=add_medicine,
                                        fg_color="blue", text_color="white", corner_radius=10,
                                        width=120)
    add_medicine_button.place(x=250, y=y_start + len(labels) * 60 + 170)


    def save_changes():
        Diagnosis = diagnosis_entry.get().strip()
        notes_value = notes_textbox.get("1.0", "end").strip()

        # Extract medicine + dosage from textbox
        medicine_lines = medicine_textbox.get("1.0", "end").split("\n")
        medicine_data = []
        for line in medicine_lines:
            line = line.strip()
            if not line:
                continue
            match = re.match(r"^(.*?)\s*\((.*?)\)$", line)
            if match:
                name = match.group(1).strip()
                dose = match.group(2).strip()
            else:
                name = line.strip()
                dose = "None"

            medicine_data.append((name.strip(), dose.strip()))

        try:
            mycursor.execute("UPDATE Appointments SET status = %s WHERE appointment_id = %s", ("Completed", app_id_to_update))
            # 1. Update diagnosis in visits
            mycursor.execute("UPDATE visits SET diagnosis = %s WHERE appointment_id = %s", (Diagnosis, app_id_to_update))

            # 2. Get visit_id from appointment_id
            mycursor.execute("SELECT visit_id FROM visits WHERE appointment_id = %s", (app_id_to_update,))
            visit_result = mycursor.fetchone()
            if not visit_result:
                messagebox.showerror("Error", "Visit not found for appointment.")
                return
            visit_id = visit_result[0]

            # 3. Delete existing prescriptions & prescription_items if present
            mycursor.execute("SELECT prescription_id FROM prescriptions WHERE visit_id = %s", (visit_id,))
            presc = mycursor.fetchone()
            if presc:
                prescription_id = presc[0]
                mycursor.execute("DELETE FROM prescription_items WHERE prescription_id = %s", (prescription_id,))
                mycursor.execute("DELETE FROM prescriptions WHERE prescription_id = %s", (prescription_id,))

            # 4. Insert new prescription
            mycursor.execute("INSERT INTO prescriptions (visit_id, notes) VALUES (%s, %s)", (visit_id, notes_value))
            new_prescription_id = mycursor.lastrowid

            # 5. Insert medicines into prescription_items
            for med_name, dose in medicine_data:
                mycursor.execute("SELECT medicine_id FROM medicines WHERE medicine_name = %s", (med_name,))
                med_row = mycursor.fetchone()
                if med_row:
                    med_id = med_row[0]
                    mycursor.execute(
                    "INSERT INTO prescription_items (prescription_id, medicine_id, dosage) VALUES (%s, %s, %s)",
                    (new_prescription_id, med_id, dose)
                )
                    mycursor.execute("update medicines set stock_quantity = stock_quantity - 5 where medicine_id = %s", (med_id,))


            # 6. Calculate total bill = sum of selected medicines + base fee
            mycursor.execute("""
                SELECT SUM(m.price) FROM medicines m
                JOIN prescription_items pi ON m.medicine_id = pi.medicine_id
                WHERE pi.prescription_id = %s
            """, (new_prescription_id,))
            total = mycursor.fetchone()[0] or 0
            mycursor.execute("Select doctor_charges from doctor_login")
            doctor_charges = mycursor.fetchone()[0]
            final_total = total + doctor_charges  

            # 7. Update billing
            mycursor.execute("SELECT bill_id FROM billing WHERE appointment_id = %s", (app_id_to_update,))
            billing_row = mycursor.fetchone()
            if billing_row:
                mycursor.execute("UPDATE billing SET total_amount = %s,payment_status=%s WHERE appointment_id = %s", (final_total,"Unpaid",app_id_to_update))
            else:
                mycursor.execute("INSERT INTO billing (appointment_id, total_amount,payment_status) VALUES (%s, %s,%s)", (app_id_to_update, final_total,"Unpaid"))
            
            mydb.commit()
            # 8. Update appointment status to 'prescribed'
            mycursor.execute("select bill_id from billing where appointment_id = %s", (app_id_to_update,))
            bill_id = mycursor.fetchone()[0]

            mycursor.execute("Insert into billing_items (bill_id,description,amount) VALUES (%s,%s,%s)",(bill_id,"Medicines",total))
            mycursor.execute("Insert into billing_items (bill_id,description,amount) VALUES (%s,%s,%s)",(bill_id,"Doctor Charges",doctor_charges))

            mydb.commit()
            messagebox.showinfo("Success", "Patient details and prescription updated.", parent=update_window)
            update_window.destroy()
            show_table()

        except pymysql.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}", parent=update_window)


    button_frame = ctk.CTkFrame(inner_frame, fg_color="white",height=80,width=500)
    button_frame.place(x=150, y=720)  

    save_button = ctk.CTkButton(button_frame, text="Save", command=save_changes, fg_color="black", text_color="white", corner_radius=10, width=120)
    save_button.place(x=30,y=0)

    back_button = ctk.CTkButton(button_frame, text="Back", command=update_window.destroy, fg_color="black", text_color="white", corner_radius=10, width=120)
    back_button.place(x=180, y=0)

    update_window.mainloop() 

def get_available_time_slots(appt_date):
    """Returns a dictionary of hour -> (booked count, max)"""
    time_ranges = [
        range(9, 12),     # 9–11 AM
        range(12, 16),    # 12–3 PM
        range(17, 21),    # 5–8 PM
    ]
    max_per_hour = 2
    slot_data = {}

    mydb = Database_Connections()
    cursor = mydb.cursor()

    for time_range in time_ranges:
        for hour in time_range:
            cursor.execute("""
                SELECT COUNT(*) FROM appointments
                WHERE appointment_date = %s AND HOUR(appointment_time) = %s
            """, (appt_date.strftime("%Y-%m-%d"), hour))
            count = cursor.fetchone()[0]
            slot_data[f"{hour:02}"] = (count, max_per_hour)

    return slot_data

def add_appointment():
    def show_slot_popup(selected_date):
        slot_info = get_available_time_slots(selected_date)
        popup = ctk.CTkToplevel()
        popup.title(f"Available Slots - {selected_date.strftime('%Y-%m-%d')}")
        popup.geometry("400x400")
        popup.configure(bg="white")

        ctk.CTkLabel(popup, text=f"Available Slots for {selected_date.strftime('%Y-%m-%d')}",
                    font=("Arial", 18, "bold"), text_color="black").pack(pady=10)

        slot_container = ctk.CTkFrame(popup, fg_color="white")
        slot_container.pack(fill="both", expand=True, padx=10, pady=10)

        row = 0
        col = 0

        for hour, (booked, maxx) in slot_info.items():
            status = f"({booked}/{maxx})"if booked < maxx else "Full"
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

        ctk.CTkButton(popup, text="Close", command=popup.destroy, fg_color="black", text_color="white").pack(pady=10)

    def show_slot_popup_safe():
        try:
            selected_date = calendar.get_date()
            if not selected_date:
                raise ValueError("No date selected")
            show_slot_popup(selected_date)
        except Exception as e:
            messagebox.showerror("Date Error", "Please select a valid appointment date.",parent=add_window)

    def fetch_patient():
        patient_id = patient_id_entry.get().strip()
        if not patient_id:
            messagebox.showerror("Error", "Please enter a Patient ID.",parent=add_window)
            return

        mydb = Database_Connections()
        cursor = mydb.cursor()
        cursor.execute("SELECT first_name, last_name, gender, dob, contact_number, blood_group FROM patients WHERE patient_id = %s", (patient_id,))
        patient = cursor.fetchone()

        if not patient:
            messagebox.showerror("Error", "Patient not found.",parent=add_window)
            return

        name_label.configure(text=f"{patient[0]} {patient[1]}")
        gender_label.configure(text=patient[2])
        dob = datetime.strptime(str(patient[3]), "%Y-%m-%d")
        age_label.configure(text=str(datetime.now().year - dob.year))
        contact_label.configure(text=patient[4])
        blood_label.configure(text=patient[5])

        enable_fields()

    def on_date_selected(event):
        selected_date = calendar.get_date()
        slot_info = get_available_time_slots(selected_date)

        available_hours = [hour for hour, (booked, maxx) in slot_info.items() if booked < maxx]

        if not available_hours:
            messagebox.showinfo("Slots Full", "No available slots for selected date.")
            hour_menu.configure(values=[], state="disabled")
            minute_menu.configure(state="disabled")
            save_button.configure(state="disabled")
        else:
            hour_menu.configure(values=available_hours, state="normal")
            hour_menu.set(available_hours[0])
            minute_menu.configure(state="normal")
            save_button.configure(state="normal")


    def enable_fields():
        calendar.configure(state="normal")

    def save_appointment():
        patient_id = patient_id_entry.get().strip()
        appt_date = calendar.get_date()
        hour = hour_menu.get()
        minute = minute_menu.get()
        appt_time = f"{hour}:{minute}:00"
        appt_type = type_menu.get()

        # Validate patient ID is not empty
        if not patient_id:
            messagebox.showerror("Error", "Patient ID is required.",parent=add_window)
            return

        # Check if appointment date is in the past
        if appt_date < date.today():
            messagebox.showerror("Error", "Appointment date cannot be in the past.")
            return

        # Check if all required fields are filled
        if not all([patient_id, appt_date, hour, minute, appt_type]):
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            formatted_date = appt_date.strftime("%Y-%m-%d")
            datetime.strptime(appt_time, "%H:%M:%S")
        except ValueError:
            messagebox.showerror("Error", "Invalid date/time format.")
            return

        mydb = None
        cursor = None
        
        try:
            mydb = Database_Connections()
            cursor = mydb.cursor()

            # Check if patient exists
            cursor.execute("SELECT patient_id FROM patients WHERE patient_id = %s", (patient_id,))
            if not cursor.fetchone():
                messagebox.showerror("Error", "Patient ID does not exist.")
                return

            # Check for conflicting appointments
            cursor.execute("""
                SELECT * FROM appointments
                WHERE appointment_date = %s AND appointment_time = %s
            """, (formatted_date, appt_time))

            existing = cursor.fetchone()
            if existing:
                messagebox.showerror("Error", "Another appointment already exists at this time.", parent=add_window)
                return

            # Insert new appointment
            cursor.execute("""
                INSERT INTO appointments (patient_id, appointment_date, appointment_time, appointment_type, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (patient_id, formatted_date, appt_time, appt_type, "Scheduled"))
            
            mydb.commit()
            appointment_id = cursor.lastrowid
            
            # Insert corresponding visit record
            cursor.execute("INSERT INTO visits (appointment_id) VALUES (%s)", (appointment_id,))
            mydb.commit()
            
            # Close the add window and show success message
            add_window.destroy()
            messagebox.showinfo("Success", "Appointment added successfully.")
            
        except Exception as e:
            if mydb:
                mydb.rollback()
            messagebox.showerror("Error", f"Database error: {str(e)}")
            
        finally:
            if cursor:
                cursor.close()
            if mydb:
                mydb.close()
        
    add_window = ctk.CTk()
    add_window.title("Add Appointment")
    add_window.configure(fg_color=lbc)
    screen_width = add_window.winfo_screenwidth()
    screen_height = add_window.winfo_screenheight()
    add_window.geometry(f"{screen_width}x{screen_height}+0+0") 


    inner_frame = ctk.CTkFrame(add_window, width=600, height=720, corner_radius=15, fg_color="white")
    inner_frame.place(x=430, y=50)

    heading_frame = ctk.CTkFrame(inner_frame, fg_color=dbc, corner_radius=10, width=250, height=40)
    heading_frame.place(x=180, y=10)
    heading = ctk.CTkLabel(heading_frame, text="Add Appointment", font=("Arial", 24, "bold"), text_color="white")
    heading.place(x=25, y=5)

    # Patient ID
    ctk.CTkLabel(inner_frame, text="Enter Patient ID:", font=("Arial", 16)).place(x=50, y=90)
    patient_id_entry = ctk.CTkEntry(inner_frame, width=200)
    patient_id_entry.place(x=220, y=90)

    ctk.CTkButton(inner_frame, text="Fetch", command=fetch_patient, width=80, fg_color="#007ACC").place(x=440, y=90)

    # Display patient info
    y_offset = 140
    label_font = ("Arial", 14, "bold")

    ctk.CTkLabel(inner_frame, text="Name:", font=label_font).place(x=50, y=y_offset+10)
    name_label = ctk.CTkLabel(inner_frame, text="", font=("Arial", 16))
    name_label.place(x=200, y=y_offset+10)

    ctk.CTkLabel(inner_frame, text="Age:", font=label_font).place(x=50, y=y_offset+50)
    age_label = ctk.CTkLabel(inner_frame, text="", font=("Arial", 16))
    age_label.place(x=200, y=y_offset+50)

    ctk.CTkLabel(inner_frame, text="Gender:", font=label_font).place(x=50, y=y_offset+90)
    gender_label = ctk.CTkLabel(inner_frame, text="", font=("Arial", 16))
    gender_label.place(x=200, y=y_offset+90)

    ctk.CTkLabel(inner_frame, text="Contact:", font=label_font).place(x=50, y=y_offset+130)
    contact_label = ctk.CTkLabel(inner_frame, text="", font=("Arial", 16))
    contact_label.place(x=200, y=y_offset+130)

    ctk.CTkLabel(inner_frame, text="Blood Group:", font=label_font).place(x=50, y=y_offset+170)
    blood_label = ctk.CTkLabel(inner_frame, text="", font=("Arial", 16))
    blood_label.place(x=200, y=y_offset+170)

    # Appointment Details
    ctk.CTkLabel(inner_frame, text="Appointment Date:", font=label_font).place(x=50, y=370)
    calendar = DateEntry(inner_frame,width=15,font=("Georgia", 17),selectmode="day", state="disabled",date_pattern="yyyy-mm-dd",mindate=date.today())
    calendar.place(x=250, y=465)
    calendar.bind("<<DateEntrySelected>>", on_date_selected)

    ctk.CTkButton(
    inner_frame, text="View Available Slots",
    command=show_slot_popup_safe,
    fg_color="#007BFF", width=200
    ).place(x=200, y=435)



    ctk.CTkLabel(inner_frame, text="Time (HH:MM):", font=label_font).place(x=50, y=510)
    hour_menu = ctk.CTkOptionMenu(inner_frame, values=[f"{i:02}" for i in range(0, 24)], state="disabled", width=60)
    hour_menu.set("10")
    hour_menu.place(x=200, y=510)

    minute_menu = ctk.CTkOptionMenu(inner_frame, values=[f"{i:02}" for i in range(0, 60, 5)], state="disabled", width=60)
    minute_menu.set("00")
    minute_menu.place(x=270, y=510)


    ctk.CTkLabel(inner_frame, text="Appointment Type:", font=label_font).place(x=50, y=580)
    type_menu = ctk.CTkOptionMenu(inner_frame, values=["InPerson", "Online"], state="normal", width=150)
    type_menu.set("InPerson")
    type_menu.place(x=200, y=580)

    # Save button
    save_button = ctk.CTkButton(inner_frame, text="Save Appointment", width=180, state="disabled", command=save_appointment, fg_color="#28A745")
    save_button.place(x=200, y=640)

    back_button = ctk.CTkButton(inner_frame, text="Back", command=add_window.destroy, fg_color="black", text_color="white", corner_radius=10, width=120)
    back_button.place(x=230, y=680)
    add_window.mainloop()

def pateintwindowdestroy():
    Patientwindow.destroy()
    
# Function to create the search bar
def create_search_bar(parent):
    global search_frame
    search_frame = ctk.CTkFrame(parent, fg_color="#4EBEFA",height=60,corner_radius=10)
    search_frame.propagate(False)
    search_frame.pack(side="top", fill="x", pady=5)

    search_options = ["Name","Patient Id","Diagnosis", "Blood Group", "Appointment Date","Contact No."]
    selected_option = ctk.StringVar(value="Name") 

    search_label = ctk.CTkLabel(search_frame, text="Search By:", font=("Arial", 12, "bold"))
    search_label.pack(side="left", padx=5)

    search_dropdown = ttk.Combobox(search_frame, textvariable=selected_option, values=search_options, state="readonly",width=10,font=("Segoe UI", 14))
    search_dropdown.pack(side="left", padx=5)

    # Search Entry Field
    search_entry = ctk.CTkEntry(search_frame, font=("Arial", 12), width=140, placeholder_text="Enter search text ")
    search_entry.pack(side="left", padx=10, pady=5)

    def search_action():
        try:
            query = search_entry.get().strip()
            search_by = selected_option.get()

            if not query:
                messagebox.showerror("Error", "Please enter a search term!")
                return

            mydb = Database_Connections()
            mycursor = mydb.cursor()
            base_query = """
                SELECT 
                    a.appointment_id AS 'Appointment ID',
                    MAX(CONCAT(p.first_name, ' ', p.last_name)) AS 'Name',
                    MAX(TIMESTAMPDIFF(YEAR, p.dob, CURDATE())) AS 'Age',
                    MAX(p.gender) AS 'Gender',
                    MAX(p.contact_number) AS 'Contact No.',
                    MAX(p.blood_group) AS 'Blood Group',
                    MAX(v.diagnosis) AS 'Diagnosis',
                    GROUP_CONCAT(DISTINCT m.medicine_name SEPARATOR ', ') AS 'Medicines',
                    GROUP_CONCAT(DISTINCT pr.notes SEPARATOR '; ') AS 'Notes',
                    MAX(a.appointment_date) AS 'Appointment Date',
                    MAX(a.appointment_time) AS 'Time',
                    MAX(b.total_amount) AS 'Bill',
                    a.status
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                LEFT JOIN visits v ON a.appointment_id = v.appointment_id
                LEFT JOIN prescriptions pr ON v.visit_id = pr.visit_id
                LEFT JOIN prescription_items pi ON pr.prescription_id = pi.prescription_id
                LEFT JOIN medicines m ON pi.medicine_id = m.medicine_id
                LEFT JOIN billing b ON a.appointment_id = b.appointment_id
            """
            condition = ""
            param = ('%' + query + '%',)

            if search_by == "Name":
                condition = "WHERE CONCAT(p.first_name, ' ', p.last_name) LIKE %s"
            elif search_by == "Patient Id":
                condition = "WHERE p.patient_id LIKE %s"
            elif search_by == "Diagnosis":
                condition = "WHERE v.diagnosis LIKE %s"
            elif search_by == "Blood Group":
                condition = "WHERE p.blood_group LIKE %s"
            elif search_by == "Appointment Date":
                condition = "WHERE a.appointment_date = %s"
                param = (query,)
            elif search_by == "Contact No.":
                condition = "WHERE p.contact_number = %s"
                param = (query,)
            else:
                messagebox.showerror("Error", "Invalid search option!")
                return

            final_query = f"{base_query} {condition} GROUP BY a.appointment_id"
            mycursor.execute(final_query, param)
            results = mycursor.fetchall()
            mydb.close()

            # Clear Treeview
            for item in table.get_children():
                table.delete(item)

            if results:
                for index, i in enumerate(results):
                    tag = "white" if index % 2 == 0 else "light_green"
                    table.insert('', 'end', values=(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10], i[11],i[12], "❌"), tags=(tag,))
            else:
                messagebox.showinfo("Not Found", f"No records found for {search_by}: {query}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


    # Search Button
    search_button = ctk.CTkButton(search_frame, text="Search",width=5,command=search_action, font=("Arial", 12, "bold"), fg_color="Blue", text_color="white",corner_radius=100)
    search_button.pack(side="left", padx=5, pady=5)

def maximize_window():
    if Patientwindow.winfo_exists():  # Ensure the window still exists
        Patientwindow.state("zoomed")

ctk.set_appearance_mode("light")  # Set light mode appearance
ctk.set_default_color_theme("blue")  # Use green theme
Patientwindow = ctk.CTk()
Patientwindow.title("CLINICLOUD")  # Set window title
Patientwindow.configure(fg_color="light blue")

Patientwindow.after(100, maximize_window)
 # Set background color
create_navigation_bar(Patientwindow)
create_search_bar(Patientwindow)
show_table()

Patientwindow.mainloop()