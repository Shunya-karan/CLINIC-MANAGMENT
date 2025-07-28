import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from PIL import Image
import pymysql
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from tkinter import filedialog
from reportlab.lib.utils import ImageReader
from tkcalendar import DateEntry
from datetime import datetime


dbc = "#07002B"
mbc = "#294B82"
lbc = "#4EBEFA"
hbc = "#1A2750"
sbc = "#87CEEB"

# DATABASE CONNECTION
def Database_Connections():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="clinic_management"
    )

def create_navigation_bar(parent):
    nav_frame = ctk.CTkFrame(parent, height=62, fg_color=("#4EBEFA", "#294B82"), corner_radius=0)
    nav_frame.pack(side="top", fill="x")

    header = ctk.CTkLabel(nav_frame, text="PATIENTS", font=("Algerian", 40), text_color="black")
    header.place(x=670, y=5)
    global large_font
    large_font = ctk.CTkFont(family="Helvetica", size=18)

    def on_refresh_enter(event):
        refresh_label.configure(text_color="grey")
    def on_refresh_leave(event):
        refresh_label.configure(text_color="Black")

    # 🔄 Refresh icon
    refresh_label = ctk.CTkLabel(nav_frame, text="🔄", text_color="Black", font=("Calibri", 40), cursor="hand2")
    refresh_label.place(x=1470, y=5)
    refresh_label.bind("<Enter>", on_refresh_enter)
    refresh_label.bind("<Leave>", on_refresh_leave)
    refresh_label.bind("<Button-1>", lambda event: show_table())

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

#TABLE VIEWING
def show_table():

    """Displays a table with patient information and a selectable checkbox."""
    mydb = Database_Connections()
    mycursor = mydb.cursor()
    mycursor.execute(""" select patient_id,concat(first_name," ",last_name),gender,TIMESTAMPDIFF(YEAR, dob, CURDATE()) as age,contact_number,emergency_contact,email,blood_group,address from patients;
        """ )
    myresult = mycursor.fetchall()

    global table, checkbox_states

    for widget in Patientwindow.winfo_children():
        if isinstance(widget, ttk.Frame):  
            widget.destroy()

    table_frame = ttk.Frame(Patientwindow)
    table_frame.pack(fill="both", expand=True, padx=20, pady=20)

    style = ttk.Style()
    style.configure("Treeview", font=("Helvetica", 12))  #  table text size
    style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))  #  heading font size        

    columns = ("Patient ID", "Name", "Gender", "Age", "Blood Group","Contact No.", "Emergency Contact", 
           "Email","Address")

    table = ttk.Treeview(table_frame, columns=columns, show="headings", style="Custom.Treeview")

    for col in columns:
        table.heading(col, text=col)
        table.column(col, anchor="center", minwidth=100, width=150)
        table.tag_configure("light_green", background="#67C2FB")  
        table.tag_configure("white", background="white") 

 
    for index, i in enumerate(myresult):
        tag = "light_green" if index % 2 == 0 else "white"  # Alternate row colors
        table.insert('', 'end', values=(i[0], i[1], i[2], i[3], i[-2], i[4], i[5], i[6],i[8]), tags=(tag,))

    checkbox_states = {}

    # def toggle_checkbox(event):
    #     """Toggles checkbox icon in the 13th column (✔ / ❌) on click."""
    #     item_id = table.identify_row(event.y)
    #     col_id = table.identify_column(event.x)

    #     if item_id and col_id == "#10":  # column "#13" means 13th visible column (index 12)
    #         values = list(table.item(item_id, "values"))
    #         current_value = values[9]  # index 12 for the 13th column
    #         new_value = "✔" if current_value == "❌" else "❌"
    #         values[9] = new_value
    #         table.item(item_id, values=values)
    #         checkbox_states[item_id] = (new_value == "✔")
    # table.bind("<Button-1>", toggle_checkbox)

    def show_patients_details_pdf():
        selected_item = table.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select Patient")
            return

        # Extract selected patient data
        item_values = table.item(selected_item[0], "values")

        pat_id = item_values[0]
        patient_name = item_values[1]
        patient_gender = item_values[2]
        patient_age = item_values[3]
        blood_group = item_values[4]
        contact_number = item_values[5]
        emergency_contact = item_values[6]
        email = item_values[7]
        address = item_values[8]

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"{patient_name}_{pat_id}.pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not file_path:
            return

        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter

        # Background
        c.setFillColorRGB(0.88, 0.95, 1)
        c.rect(0, 0, width, height, fill=1)

        # Logo
        try:
            logo = ImageReader("Clinic_System/build/clinic-logo.png")
            c.drawImage(logo, 40, height - 100, width=80, height=80, mask='auto')
        except:
            pass

        # Heading
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(colors.darkblue)
        c.drawString(150, height - 60, "")

        c.setFont("Helvetica-Bold", 18)
        c.drawString(150, height - 90, "Patient Details")

        c.setStrokeColor(colors.darkblue)
        c.setLineWidth(1.5)
        c.line(40, height - 100, width - 40, height - 100)

        # Table data
        c.setFont("Helvetica", 12)
        table_data = [
            ["Field", "Value"],
            ["Patient ID", pat_id],
            ["Name", patient_name],
            ["Age", patient_age],
            ["Gender", patient_gender],
            ["Blood Group", blood_group],
            ["Phone", contact_number],
            ["Emergency Contact", emergency_contact],
            ["Email", email],
            ["Address", address],
        ]

        x_start, y_start = 60, height - 140
        row_height, col1_width, col2_width = 25, 160, 370

        # Draw table
        for row_num, row in enumerate(table_data):
            y = y_start - row_num * row_height
            fill = colors.white if row_num == 0 else colors.black
            c.setFillColor(fill)
            c.rect(x_start, y - row_height, col1_width, row_height, stroke=1, fill=row_num == 0)
            c.rect(x_start + col1_width, y - row_height, col2_width, row_height, stroke=1, fill=row_num == 0)

            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold" if row_num == 0 else "Helvetica", 12)
            c.drawString(x_start + 5, y - 17, str(row[0]))
            c.drawString(x_start + col1_width + 5, y - 17, str(row[1]))

        # Signature section
        signature_x, signature_y = width - 200, 100
        c.setFont("Helvetica-Bold", 12)
        c.drawString(signature_x, signature_y + 40, "Signature:")
        try:
            signature_img = ImageReader("Clinic_System/build/Signature.png")
            c.drawImage(signature_img, signature_x, signature_y, width=120, height=30, mask='auto')
        except:
            c.rect(signature_x, signature_y, 120, 30, stroke=1, fill=0)

        # Footer
        c.setFont("Helvetica", 8)
        c.drawString(50, 30, f"Generated on: {datetime.now().strftime('%d-%m-%Y %I:%M %p')}")

        # Fetch appointment history from database
        mydb = Database_Connections()
        mycursor = mydb.cursor()
        mycursor.execute("""
            SELECT a.appointment_date, v.diagnosis 
            FROM appointments a
            JOIN patients p ON p.patient_id = a.patient_id 
            JOIN visits v ON a.appointment_id = v.appointment_id
            WHERE p.patient_id = %s
        """, (pat_id,))  # COMMA is important to make it a tuple
        appt_history = mycursor.fetchall()

        # Draw heading
        appt_history_y = y_start - (len(table_data) + 2) * row_height - 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_start, appt_history_y, "Appointment History:")

        # Draw column headers
        appt_history_y -= 25
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_start + 5, appt_history_y, "Date")
        c.drawString(x_start + 160, appt_history_y, "Diagnosis")

        # Draw history rows
        c.setFont("Helvetica", 11)
        for row in appt_history:
            appt_history_y -= 20
            c.drawString(x_start + 5, appt_history_y, str(row[0]))
            c.drawString(x_start + 160, appt_history_y, str(row[1]))

        c.save()
        messagebox.showinfo("Success", f"PDF saved as {file_path}")

    show_patients_pdf=ctk.CTkButton(search_frame
        , text="GENERATE PDF", command=show_patients_details_pdf,
        font=large_font, fg_color="light green", text_color="black",
        corner_radius=8, border_width=1, height=30,border_color="black"
    )
    show_patients_pdf.place(x=1350,y=19)

    # Create Scrollbars
    x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=table.xview)
    y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)

    table.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)

    y_scroll.pack(side="right", fill="y")
    x_scroll.pack(side="bottom", fill="x")
    table.pack(fill="both", expand=True)

    # Create a frame for the medicine details box
    style = ttk.Style()
    style.configure("Blue.TFrame", background=sbc)  # This is a shade of blue
    medicine_frame = ttk.Frame(Patientwindow, height=50, style="Blue.TFrame")
    medicine_frame.pack(fill="x", padx=20, pady=0)
    medicine_frame.propagate(False)  # Use boolean, not string

    delete_patient_button = ctk.CTkButton(
        medicine_frame, text=" Delete  Patient ", 
        command=lambda: show_deletion_requests_frame(Patientwindow),width=150,
        height=30,font=('arial',20), fg_color="red", corner_radius=8, border_width=1, border_color="black"
    )
    delete_patient_button.place(x=1300, y=0)


def show_deletion_requests_frame(parent_frame):
    """Function to create and display patient deletion requests frame"""
    
    def main_framedestroy():
        main_frame.destroy()

    
    # Create main frame
    main_frame = ctk.CTkFrame(parent_frame, fg_color=dbc)
    main_frame.pack(fill="both", expand=True)

    back_label = ctk.CTkButton(main_frame, text="Close", text_color="White", 
                              fg_color=hbc, hover_color=mbc, font=("Calibri", 40), 
                              cursor="hand2", command=main_framedestroy)
    back_label.place(x=5, y=5)

    # Title
    ctk.CTkLabel(main_frame, text="Patient Account Deletion Requests", 
                font=("Georgia", 25, "bold"), text_color=lbc).pack(pady=20)
    
    # Create scrollable frame for requests
    scrollable_frame = ctk.CTkScrollableFrame(main_frame, width=1150, height=500, 
                                             fg_color=dbc)
    scrollable_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    def load_and_display_requests():
        """Load and display patient deletion requests"""
        # Clear existing widgets
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
            
        # Get requests from database
        try:
            connection = pymysql.connect(host='localhost', user='root', password='root', database='clinic_management')
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT pdr.request_id, pdr.patient_id, pdr.patient_name, 
                       pdr.reason_for_deletion, pdr.request_date, pdr.status,
                       p.gender, p.dob, p.contact_number, p.email
                FROM patient_deletion_requests pdr
                LEFT JOIN patients p ON pdr.patient_id = p.patient_id
                ORDER BY pdr.request_date DESC
            """)
            
            requests = cursor.fetchall()
            connection.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load requests: {str(e)}")
            return
        
        # Display requests
        if requests:
            for i, request in enumerate(requests):
                request_id, patient_id, patient_name, reason, request_date, status, gender, dob, contact, email = request
                
                # Create frame for each request
                request_frame = ctk.CTkFrame(scrollable_frame, corner_radius=10, fg_color=mbc)
                request_frame.pack(fill="x", pady=10, padx=10)
                
                # Status color
                status_color = "#ffc107" if status == "Pending" else "#28a745" if status == "Approved" else "#dc3545"
                
                # Request header
                header_frame = ctk.CTkFrame(request_frame, fg_color=hbc)
                header_frame.pack(fill="x", padx=15, pady=10)
                
                ctk.CTkLabel(header_frame, text=f"Request #{request_id}", 
                            font=("Arial", 16, "bold"), text_color="white").pack(side="left")
                
                ctk.CTkLabel(header_frame, text=f"Status: {status}", 
                            font=("Arial", 14, "bold"), text_color=status_color).pack(side="right")
                
                # Patient info
                info_frame = ctk.CTkFrame(request_frame, fg_color="transparent")
                info_frame.pack(fill="x", padx=15, pady=5)
                
                # Patient details
                left_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
                left_frame.pack(side="left", fill="both", expand=True)
                
                ctk.CTkLabel(left_frame, text=f"Patient: {patient_name} (ID: {patient_id})", 
                            font=("Arial", 14, "bold"), text_color="white", anchor="w").pack(fill="x")
                ctk.CTkLabel(left_frame, text=f"Gender: {gender or 'N/A'} | DOB: {dob or 'N/A'}", 
                            font=("Arial", 12), text_color=lbc, anchor="w").pack(fill="x")
                ctk.CTkLabel(left_frame, text=f"Contact: {contact or 'N/A'} | Email: {email or 'N/A'}", 
                            font=("Arial", 12), text_color=lbc, anchor="w").pack(fill="x")
                ctk.CTkLabel(left_frame, text=f"Request Date: {request_date.strftime('%Y-%m-%d %H:%M')}", 
                            font=("Arial", 12), text_color=lbc, anchor="w").pack(fill="x")
                
                # Reason section
                reason_frame = ctk.CTkFrame(request_frame, fg_color="transparent")
                reason_frame.pack(fill="x", padx=15, pady=5)
                
                ctk.CTkLabel(reason_frame, text="Reason for deletion:", 
                            font=("Arial", 12, "bold"), text_color="white", anchor="w").pack(fill="x")
                
                reason_text = ctk.CTkTextbox(reason_frame, height=60, font=("Arial", 11),
                                           fg_color=dbc, text_color="white")
                reason_text.pack(fill="x", pady=2)
                reason_text.insert("1.0", reason)
                reason_text.configure(state="disabled")
                
                # Buttons (only for pending requests)
                if status == "Pending":
                    button_frame = ctk.CTkFrame(request_frame, fg_color="transparent")
                    button_frame.pack(fill="x", padx=15, pady=10)
                    
                    def approve_deletion(req_id=request_id, pat_id=patient_id, pat_name=patient_name):
                        """Approve a patient deletion request"""
                        result = messagebox.askyesno("Confirm Deletion", 
                                                   f"Are you sure you want to permanently delete patient '{pat_name}' (ID: {pat_id})?\n\n"
                                                   f"This action cannot be undone!")
                        
                        if result:
                            connection = None
                            try:
                                connection = pymysql.connect(host='localhost', user='root', password='root', database='clinic_management')
                                cursor = connection.cursor()
                                
                                # Start transaction
                                connection.begin()
                                
                                # 1. Delete from patient_login_history
                                cursor.execute("DELETE FROM patient_login_history WHERE patient_id = %s", (pat_id,))
                                
                                # 2. Get appointment IDs for this patient
                                cursor.execute("SELECT appointment_id FROM appointments WHERE patient_id = %s", (pat_id,))
                                appointment_rows = cursor.fetchall()
                                
                                # Process each appointment individually
                                for app_row in appointment_rows:
                                    app_id = app_row[0]
                                    
                                    # Get visit IDs for this appointment
                                    cursor.execute("SELECT visit_id FROM visits WHERE appointment_id = %s", (app_id,))
                                    visit_rows = cursor.fetchall()
                                    
                                    # Process each visit
                                    for visit_row in visit_rows:
                                        visit_id = visit_row[0]
                                        
                                        # Delete leave_letters for this visit
                                        cursor.execute("DELETE FROM leave_letters WHERE visit_id = %s", (visit_id,))
                                        
                                        # Get prescription IDs for this visit
                                        cursor.execute("SELECT prescription_id FROM prescriptions WHERE visit_id = %s", (visit_id,))
                                        prescription_rows = cursor.fetchall()
                                        
                                        # Delete prescription items and prescriptions
                                        for pres_row in prescription_rows:
                                            pres_id = pres_row[0]
                                            cursor.execute("DELETE FROM prescription_items WHERE prescription_id = %s", (pres_id,))
                                        
                                        # Delete prescriptions for this visit
                                        cursor.execute("DELETE FROM prescriptions WHERE visit_id = %s", (visit_id,))
                                    
                                    # Delete visits for this appointment
                                    cursor.execute("DELETE FROM visits WHERE appointment_id = %s", (app_id,))
                                    
                                    # Delete billing items for this appointment
                                    cursor.execute("SELECT bill_id FROM billing WHERE appointment_id = %s", (app_id,))
                                    bill_rows = cursor.fetchall()
                                    
                                    for bill_row in bill_rows:
                                        bill_id = bill_row[0]
                                        cursor.execute("DELETE FROM billing_items WHERE bill_id = %s", (bill_id,))
                                    
                                    # Delete billing for this appointment
                                    cursor.execute("DELETE FROM billing WHERE appointment_id = %s", (app_id,))
                                
                                # Delete all appointments for this patient
                                cursor.execute("DELETE FROM appointments WHERE patient_id = %s", (pat_id,))
                                
                                # Delete the patient record
                                cursor.execute("DELETE FROM patients WHERE patient_id = %s", (pat_id,))
                                
                                # Update request status to 'Approved' with timestamp and reviewer info
                                cursor.execute("""
                                    UPDATE patient_deletion_requests 
                                    SET status = %s, reviewed_at = CURRENT_TIMESTAMP, reviewed_by = %s, review_comments = %s
                                    WHERE request_id = %s
                                """, ('Approved', 'Admin', 'Patient deletion approved and executed', req_id))
                                
                                # Commit transaction
                                connection.commit()
                                
                                messagebox.showinfo("Success", f"Patient '{pat_name}' and all related records have been successfully deleted.")
                                load_and_display_requests()  # Refresh
                                
                            except Exception as e:
                                if connection:
                                    connection.rollback()
                                messagebox.showerror("Error", f"Failed to approve deletion: {str(e)}")
                                print(f"Detailed error: {e}")  # For debugging
                            finally:
                                if connection:
                                    connection.close()
                    
                    def reject_deletion(req_id=request_id):
                        """Reject a patient deletion request"""
                        # Create a popup for rejection reason
                        rejection_window = ctk.CTkToplevel()
                        rejection_window.title("Reject Deletion Request")
                        rejection_window.geometry("400x300")
                        rejection_window.transient()
                        rejection_window.grab_set()
                        
                        ctk.CTkLabel(rejection_window, text="Rejection Reason:", 
                                    font=("Arial", 14, "bold")).pack(pady=10)
                        
                        reason_textbox = ctk.CTkTextbox(rejection_window, height=100, width=350)
                        reason_textbox.pack(pady=10, padx=20)
                        
                        def submit_rejection():
                            rejection_reason = reason_textbox.get("1.0", "end").strip()
                            if not rejection_reason:
                                messagebox.showerror("Error", "Please provide a reason for rejection.")
                                return
                            
                            try:
                                connection = pymysql.connect(host='localhost', user='root', password='root', database='clinic_management')
                                cursor = connection.cursor()
                                
                                cursor.execute("""
                                    UPDATE patient_deletion_requests 
                                    SET status = %s, reviewed_at = CURRENT_TIMESTAMP, reviewed_by = %s, review_comments = %s
                                    WHERE request_id = %s
                                """, ('Rejected', 'Admin', rejection_reason, req_id))
                                
                                connection.commit()
                                connection.close()
                                
                                messagebox.showinfo("Success", "Deletion request has been rejected.")
                                rejection_window.destroy()
                                load_and_display_requests()  # Refresh
                                
                            except Exception as e:
                                messagebox.showerror("Error", f"Failed to reject deletion: {str(e)}")
                        
                        button_frame = ctk.CTkFrame(rejection_window, fg_color="transparent")
                        button_frame.pack(pady=20)
                        
                        ctk.CTkButton(button_frame, text="Submit", command=submit_rejection,
                                     fg_color="#dc3545", hover_color="#c82333").pack(side="left", padx=10)
                        ctk.CTkButton(button_frame, text="Cancel", command=rejection_window.destroy,
                                     fg_color="#6c757d", hover_color="#545b62").pack(side="right", padx=10)
                    
                    # Add approve and reject buttons
                    ctk.CTkButton(button_frame, text="Approve", command=approve_deletion,
                                 fg_color="#28a745", hover_color="#218838").pack(side="left", padx=5)
                    ctk.CTkButton(button_frame, text="Reject", command=reject_deletion,
                                 fg_color="#dc3545", hover_color="#c82333").pack(side="left", padx=5)
        else:
            # No requests found
            ctk.CTkLabel(scrollable_frame, text="No deletion requests found.", 
                        font=("Arial", 16), text_color=lbc).pack(pady=50)
    
    # Load and display requests on startup
    load_and_display_requests()
    
    # Refresh button
    ctk.CTkButton(main_frame, text="🔄 Refresh", command=load_and_display_requests,
                 fg_color=lbc, hover_color=mbc, text_color="white", width=100).pack(pady=5)
    
    return main_frame

def insert_patient():
    mydb = Database_Connections()
    if mydb is None:
        return
    mycursor = mydb.cursor()

    width = Patientwindow.winfo_screenwidth()
    height = Patientwindow.winfo_screenheight()
    insert_window = ctk.CTk()
    insert_window.title("Add Patient Details")
    insert_window.geometry(f"{width}x{height}+0+0")
    insert_window.configure(fg_color="#4EBEFA")

    inner_frame = ctk.CTkFrame(insert_window, fg_color="white", corner_radius=15, width=550, height=750)
    inner_frame.place(x=width//2 - 250, y=20)

    heading_frame = ctk.CTkFrame(inner_frame, fg_color="#294B82", corner_radius=10, width=250, height=40)
    heading_frame.place(x=165, y=20)

    title_label = ctk.CTkLabel(heading_frame, text="Add Patient", font=("Arial", 16, "bold"), text_color="white")
    title_label.place(relx=0.5, rely=0.5, anchor="center")

    # --- Name ---
    name_label = ctk.CTkLabel(inner_frame, text="Name", font=("Arial", 14, "bold"), text_color="black")
    name_label.place(x=30, y=100)
    name_entry = ctk.CTkEntry(inner_frame, font=("Arial", 14), width=280, corner_radius=5, text_color="gray")
    name_entry.insert(0, "Enter full name")
    name_entry.place(x=190, y=100)

    # --- Gender (Dropdown) ---
    gender_label = ctk.CTkLabel(inner_frame, text="Gender", font=("Arial", 14, "bold"), text_color="black")
    gender_label.place(x=30, y=170)
    gender_options = ["Male", "Female", "Other"]
    gender_dropdown = ctk.CTkOptionMenu(inner_frame, values=gender_options, width=280)
    gender_dropdown.set("Select Gender")
    gender_dropdown.place(x=190, y=170)


    # --- Date of Birth ---
    dob_label = ctk.CTkLabel(inner_frame, text="Date of Birth", font=("Arial", 14, "bold"), text_color="black")
    dob_label.place(x=30, y=240)
    dob_entry = DateEntry(inner_frame, width=15, font=("Georgia", 17), date_pattern="yyyy-mm-dd", corner_radius=5, text_color="gray")
    dob_entry.place(x=240, y=295)

    # --- Blood Group (Dropdown) ---
    blood_label = ctk.CTkLabel(inner_frame, text="Blood Group", font=("Arial", 14, "bold"), text_color="black")
    blood_label.place(x=30, y=310)
    blood_options = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    blood_dropdown = ctk.CTkOptionMenu(inner_frame, values=blood_options, width=280)
    blood_dropdown.set("Select Blood Group")
    blood_dropdown.place(x=190, y=310)

    # --- Contact Number ---
    contact_label = ctk.CTkLabel(inner_frame, text="Contact Number", font=("Arial", 14, "bold"), text_color="black")
    contact_label.place(x=30, y=380)
    contact_entry = ctk.CTkEntry(inner_frame, font=("Arial", 14), width=280, corner_radius=5, text_color="gray")
    contact_entry.insert(0, "Enter 10-digit number")
    contact_entry.place(x=190, y=380)

    # --- Emergency Contact ---
    emergency_label = ctk.CTkLabel(inner_frame, text="Emergency Contact", font=("Arial", 14, "bold"), text_color="black")
    emergency_label.place(x=30, y=450)
    emergency_entry = ctk.CTkEntry(inner_frame, font=("Arial", 14), width=280, corner_radius=5, text_color="gray")
    emergency_entry.insert(0, "Enter emergency contact number")
    emergency_entry.place(x=190, y=450)

    # --- Email ---
    email_label = ctk.CTkLabel(inner_frame, text="Email", font=("Arial", 14, "bold"), text_color="black")
    email_label.place(x=30, y=510)
    email_entry = ctk.CTkEntry(inner_frame, font=("Arial", 14), width=280, corner_radius=5, text_color="gray")
    email_entry.insert(0, "Enter email address")
    email_entry.place(x=190, y=510)

    # --- Address ---
    address_label = ctk.CTkLabel(inner_frame, text="Address", font=("Arial", 14, "bold"), text_color="black")
    address_label.place(x=30, y=580)
    address_entry = ctk.CTkTextbox(inner_frame, height=80, width=280, corner_radius=5, fg_color="#8ca5cd")
    address_entry.place(x=190, y=580)

    # Placeholder logic (optional)
    def on_entry_focus_in(event, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.configure(text_color="black")

    def on_entry_focus_out(event, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.configure(text_color="gray")

    for entry, text in [
        (name_entry, "Enter full name"),
        (contact_entry, "Enter 10-digit number"),
        (emergency_entry, "Enter emergency contact number"),
        (email_entry, "Enter email address"),
    ]:
        entry.bind("<FocusIn>", lambda e, ent=entry, ph=text: on_entry_focus_in(e, ent, ph))
        entry.bind("<FocusOut>", lambda e, ent=entry, ph=text: on_entry_focus_out(e, ent, ph))

    def save_changes():
        updated_values = {
            "Name": name_entry.get(),
            "Gender": gender_dropdown.get(),
            "DOB": dob_entry.get(),
            "Blood Group": blood_dropdown.get(),
            "Contact Number": contact_entry.get(),
            "Emergency Contact": emergency_entry.get(),
            "Email": email_entry.get(),
            "Address": address_entry.get("1.0", "end").strip(),
        }
        
        # Regex patterns
        phone_pattern = r"^\d{10}$"
        email_regex = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")
        
        # Validate all fields first
        if not updated_values["Name"] or updated_values["Name"] == "Enter full name":
            messagebox.showerror("Error", "Please enter Name!", parent=insert_window)
            return
        if len(updated_values["Name"].split()) != 2:
             messagebox.showerror("Error", "Please enter full name (First and Last)",parent=insert_window)
             return

        if updated_values["Gender"] == "Select Gender":
            messagebox.showerror("Error", "Please select Gender!", parent=insert_window)
            return
        
        if not updated_values["DOB"]:
            messagebox.showerror("Error", "Please select Date of Birth!", parent=insert_window)
            return
        
        if updated_values["Blood Group"] == "Select Blood Group":
            messagebox.showerror("Error", "Please select Blood Group!", parent=insert_window)
            return
        
        if (not updated_values["Contact Number"] or 
            updated_values["Contact Number"] == "Enter 10-digit number" or 
            not re.match(phone_pattern, updated_values["Contact Number"])):
            messagebox.showerror("Error", "Please enter a valid 10-digit Contact Number!", parent=insert_window)
            return
        
        if not updated_values["Email"] or not email_regex.match(updated_values["Email"]):
            messagebox.showerror("Error", "Please enter a valid Email!", parent=insert_window)
            return
        
        # If all validations pass, insert into database
        try:
            full_name = updated_values["Name"].strip().split()
            first_name = full_name[0]
            last_name = " ".join(full_name[1:]) if len(full_name) > 1 else ""

            sql = """
                INSERT INTO Patients (
                    first_name, last_name, dob, gender,
                    contact_number, blood_group, emergency_contact, email, address
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                first_name,
                last_name,
                updated_values["DOB"],
                updated_values["Gender"],
                updated_values["Contact Number"],
                updated_values["Blood Group"],
                updated_values["Emergency Contact"],
                updated_values["Email"],
                updated_values["Address"],
            )
            mycursor.execute(sql, values)
            mydb.commit()

            messagebox.showinfo("Success", "Patient details inserted successfully.", parent=insert_window)
            insert_window.destroy()
            show_table()  # Refresh table if you have this defined

        except pymysql.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}", parent=insert_window)
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}", parent=insert_window)



    button_frame = ctk.CTkFrame(inner_frame, fg_color="white", height=90, width=500)
    button_frame.place(x=30, y=690)

    save_button = ctk.CTkButton(button_frame, text="Save", command=save_changes, fg_color="#07002B", text_color="white", corner_radius=10, width=120)
    save_button.place(x=90, y=10)

    back_button = ctk.CTkButton(button_frame, text="Back", command=insert_window.destroy, fg_color="black", text_color="white", corner_radius=10, width=120)
    back_button.place(x=250, y=10)

    insert_window.mainloop()

selected_vars = {}  
def update_patient():
    """Updates patient details based on user input."""
    pat_id_to_update = ctk.CTkInputDialog(title="Update Patient", text="Enter the Patient ID:").get_input()
    if not pat_id_to_update:
        messagebox.showerror("Error", "Please enter the Patient ID.")
        return

    mydb = Database_Connections()
    mycursor = mydb.cursor()
    mycursor.execute("""select concat(first_name," ",last_name),gender, dob,contact_number,emergency_contact,email,blood_group,address from patients where patient_id=%s;
        """ , (pat_id_to_update,))
    row = mycursor.fetchone()
    if row is None:
        messagebox.showerror("Error", "Patient not found.")
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

    title_label = ctk.CTkLabel(heading_frame, text="Update Patient", font=("Arial", 16, "bold"), text_color="white")
    title_label.place(relx=0.5, rely=0.5, anchor="center")


    data = row
    # --- Name ---
    name_label = ctk.CTkLabel(inner_frame, text="Name", font=("Arial", 14, "bold"), text_color="black")
    name_label.place(x=30, y=100)
    name_entry = ctk.CTkEntry(inner_frame, font=("Arial", 14), width=280, corner_radius=5, text_color="Black")
    if data[0] is not None:
        name_entry.insert(0, str(data[0]))
    else:
        name_entry.configure(placeholder_text="Enter Name")
    name_entry.place(x=190, y=100)

    # --- Gender (Dropdown) ---
    gender_label = ctk.CTkLabel(inner_frame, text="Gender", font=("Arial", 14, "bold"), text_color="black")
    gender_label.place(x=30, y=170)
    gender_options = ["Male", "Female", "Other"]
    gender_dropdown = ctk.CTkOptionMenu(inner_frame,values=gender_options, width=280)
    gender_dropdown.set(data[1] if data[1] is not None else "Select Gender")
    gender_dropdown.place(x=190, y=170)


    # --- Date of Birth ---
    dob_label = ctk.CTkLabel(inner_frame, text="Date of Birth", font=("Arial", 14, "bold"), text_color="black")
    dob_label.place(x=30, y=240)
    dob_entry = DateEntry(inner_frame, width=15, font=("Georgia", 17), date_pattern="yyyy-mm-dd", corner_radius=5, text_color="black")
    dob_entry.set_date(data[2]if data[2] is not None else "")
    dob_entry.place(x=240, y=295)

    # --- Blood Group (Dropdown) ---
    blood_label = ctk.CTkLabel(inner_frame, text="Blood Group", font=("Arial", 14, "bold"), text_color="black")
    blood_label.place(x=30, y=310)
    blood_options = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    blood_dropdown = ctk.CTkOptionMenu(inner_frame, values=blood_options, width=280)
    blood_dropdown.set(data[-2] if data[4] is not None else "Blood Group")
    blood_dropdown.place(x=190, y=310)

    # --- Contact Number ---
    contact_label = ctk.CTkLabel(inner_frame, text="Contact Number", font=("Arial", 14, "bold"), text_color="black")
    contact_label.place(x=30, y=380)
    contact_entry = ctk.CTkEntry(inner_frame, font=("Arial", 14), width=280, corner_radius=5, text_color="Black")
    if data[3] is not None:
        contact_entry.insert(0, str(data[3]))
    else:
        contact_entry.configure(placeholder_text="Enter Contact Number")
    contact_entry.place(x=190, y=380)

    # --- Emergency Contact ---
    emergency_label = ctk.CTkLabel(inner_frame, text="Emergency Contact", font=("Arial", 14, "bold"), text_color="black")
    emergency_label.place(x=30, y=450)
    emergency_entry = ctk.CTkEntry(inner_frame, font=("Arial", 14), width=280, corner_radius=5, text_color="Black")
    if data[4] is not None:
        emergency_entry.insert(0, str(data[4]))
    else:
        emergency_entry.configure(placeholder_text="Enter Emergency Contact")
    emergency_entry.place(x=190, y=450)

    # --- Email ---
    email_label = ctk.CTkLabel(inner_frame, text="Email", font=("Arial", 14, "bold"), text_color="black")
    email_label.place(x=30, y=510)
    email_entry = ctk.CTkEntry(inner_frame, font=("Arial", 14), width=280, corner_radius=5, text_color="Black")
    if data[5] is not None:
        email_entry.insert(0, str(data[5]))
    else:
        email_entry.configure(placeholder_text="Enter Email")
    email_entry.place(x=190, y=510)

    # --- Address ---
    address_label = ctk.CTkLabel(inner_frame, text="Address", font=("Arial", 14, "bold"), text_color="black")
    address_label.place(x=30, y=580)
    address_entry = ctk.CTkTextbox(inner_frame, height=80, width=280, corner_radius=5, fg_color="#8ca5cd")
    address_entry.insert("1.0", data[-1] if data[-1] is not None else "")
    address_entry.place(x=190, y=580)


    def save_changes():
        try:
            pattern = r"^\d{10}$"
            emailrgx = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")

            # --- Name ---
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Please enter your name",parent=update_window)
                return
            if len(name.split()) != 2:
                messagebox.showerror("Error", "Please enter full name (First and Last)",parent=update_window)
                return
            first_name, last_name = name.split()

            # --- Date of Birth ---
            dob = dob_entry.get_date()
            if not dob:
                messagebox.showerror("Error", "Please enter your date of birth",parent=update_window)
                return

            # --- Blood Group ---
            blood = blood_dropdown.get()
            if not blood:
                messagebox.showerror("Error", "Please select your blood group",parent=update_window)
                return

            # --- Contact Number ---
            contact = contact_entry.get().strip()
            if not re.match(pattern, contact):
                messagebox.showerror("Error", "Please enter a valid 10-digit contact number",parent=update_window)
                return

            # --- Emergency Contact ---
            emergency = emergency_entry.get().strip()
            if not re.match(pattern, emergency):
                messagebox.showerror("Error", "Please enter a valid 10-digit emergency contact number",parent=update_window)
                return

            # --- Email ---
            email = email_entry.get().strip()
            if not emailrgx.match(email):
                messagebox.showerror("Error", "Please enter a valid email",parent=update_window)
                return

            # --- Address ---
            address = address_entry.get("1.0", "end-1c").strip()
            if not address:
                messagebox.showerror("Error", "Please enter your address",parent=update_window)
                return

            # --- Gender ---
            gender = gender_dropdown.get()
            if not gender:
                messagebox.showerror("Error", "Please select your gender",parent=update_window)
                return

            # --- Save to Database ---
            mycursor.execute("""
                UPDATE patients 
                SET first_name=%s, last_name=%s, dob=%s, blood_group=%s, gender=%s, 
                    contact_number=%s, emergency_contact=%s, address=%s, email=%s 
                WHERE patient_id=%s
            """, (first_name, last_name, dob, blood, gender, contact, emergency, address, email, pat_id_to_update))

            mydb.commit()
            messagebox.showinfo("Success", "Patient details updated successfully.", parent=update_window)
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


def pateintwindowdestroy():
    Patientwindow.destroy()
    
# Function to create the search bar
def create_search_bar(parent):
    global search_frame
    search_frame = ctk.CTkFrame(parent, fg_color="#4EBEFA",height=70 ,corner_radius=10)
    search_frame.pack_propagate(False)
    search_frame.pack(side="top", fill="x", pady=5)

    search_options = ["Name","Patient Id","Blood Group","Contact No."]
    selected_option = ctk.StringVar(value="Name") 

    search_label = ctk.CTkLabel(search_frame, text="Search By:", font=("Arial", 12, "bold"),height=25)
    search_label.pack(side="left", padx=5)

    search_dropdown = ttk.Combobox(search_frame, textvariable=selected_option, values=search_options, state="readonly",width=20,font=("Segoe UI", 14))
    search_dropdown.pack(side="left", padx=5)

        # Button frame placed explicitly to the left of refresh icon
    button_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
    button_frame.place(x=995, y=17)  # Adjust X as needed to avoid overlap

    # Add Patients & Prescription
    buttons = [
        ("Add Patients", insert_patient),  
        ("Update", update_patient)
    ]
    for text, command in buttons:
        button = ctk.CTkButton(
            button_frame, text=text, font=("arial" ,12 , "bold"),height=35,
            fg_color="darkblue", text_color="white", hover_color="lightblue",
            corner_radius=8, border_width=1, border_color="black", command=command
        )
        button.pack(side="left",padx = 15,pady=3)

    # Search Entry Field
    search_entry = ctk.CTkEntry(search_frame, font=("Arial", 12), width=200, placeholder_text="Enter search text...")
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
                SELECT p.patient_id, CONCAT(p.first_name, " ", p.last_name), p.gender,
                    TIMESTAMPDIFF(YEAR, p.dob, CURDATE()) AS age,
                    p.contact_number, p.emergency_contact, p.email,
                    p.blood_group, p.address
                FROM patients p
            """

            condition = ""
            param = ('%' + query + '%',)

            if search_by == "Name":
                condition = "WHERE CONCAT(p.first_name, ' ', p.last_name) LIKE %s"
            elif search_by == "Patient Id":
                condition = "WHERE p.patient_id LIKE %s"
            elif search_by == "Blood Group":
                condition = "WHERE p.blood_group LIKE %s"
            elif search_by == "Contact No.":
                condition = "WHERE p.contact_number = %s"
                param = (query,)
            else:
                messagebox.showerror("Error", "Invalid search option!")
                return

            final_query = f"{base_query} {condition}"
            mycursor.execute(final_query, param)
            results = mycursor.fetchall()
            mydb.close()

            # Clear existing entries
            for item in table.get_children():
                table.delete(item)

            if results:
                for index, i in enumerate(results):
                    tag = "white" if index % 2 == 0 else "light_green"
                    table.insert(
                        '', 'end',
                        values=(i[0], i[1], i[2], i[3], i[7], i[4], i[5], i[6], i[8], "❌"),
                        tags=(tag,)
                    )
            else:
                messagebox.showinfo("Not Found", f"No records found for {search_by}: {query}")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    # Search Button
    search_button = ctk.CTkButton(search_frame, text="Search", command=search_action, font=("Arial", 12, "bold"), fg_color="Blue", text_color="white")
    search_button.pack(side="left", padx=5, pady=5)


def maximize_window():
    if Patientwindow.winfo_exists():  # Ensure the window still exists
        Patientwindow.state("zoomed")

ctk.set_appearance_mode("light")  # Set light mode appearance
ctk.set_default_color_theme("blue")  # Use green theme
Patientwindow = ctk.CTk()
Patientwindow.title("CLINICLOUD")  # Set window title
Patientwindow.configure(fg_color=sbc)  # Light green

Patientwindow.after(100, maximize_window)
 # Set background color
create_navigation_bar(Patientwindow)
create_search_bar(Patientwindow)
show_table()

Patientwindow.mainloop()