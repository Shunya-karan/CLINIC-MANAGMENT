import customtkinter as ctk
from tkinter import ttk, messagebox, Toplevel
import pymysql
from PIL import Image, ImageTk
import io

# --- Configuration ---
# Define colors for a consistent theme
DBC = "#007BFF"   # Dark Blue for main background
LBC = "#0056b3" # Lighter Blue for frames and accents
TEXT_COLOR = "#FFFFFF"
ACCENT_COLOR = "white"  # A vibrant cyan for titles and highlights
APPROVE_COLOR = "#00FF88"
APPROVE_HOVER = "#00CC66"
REJECT_COLOR = "#FF4444"
REJECT_HOVER = "#CC0000"
INFO_COLOR = "#4A90E2"
INFO_HOVER = "#357ABD"

# --- Database Connection ---
# Store connection details. In a real app, use a config file.
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "clinic_management"
}

# --- Global Variables ---
consultation_data = []
tree = None

def get_connection():
    """Establishes and returns a database connection."""
    try:
        return pymysql.connect(**DB_CONFIG)
    except pymysql.Error as e:
        messagebox.showerror("Database Connection Error", f"Failed to connect to the database:\n{e}")
        return None

def create_styles(root):
    """Creates and configures ttk styles for the Treeview to match the dark theme."""
    style = ttk.Style(root)
    style.theme_use("default")

    # Configure the Treeview style
    style.configure("Treeview",
                    background=LBC,
                    foreground=TEXT_COLOR,
                    fieldbackground=LBC,
                    borderwidth=0,
                    rowheight=30) # Increase row height for better readability
    
    style.map('Treeview', background=[('selected', ACCENT_COLOR)])

    # Configure the Treeview Heading style
    style.configure("Treeview.Heading",
                    background=DBC,
                    foreground=ACCENT_COLOR,
                    font=('Arial', 12, 'bold'),
                    padding=(10, 10))
    
    style.map("Treeview.Heading",
              background=[('active', LBC)])

def show_paid_patients():
    """Opens a window showing all paid patients with their screenshot viewing options."""
    conn = get_connection()
    if not conn:
        return
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT consultation_id, patient_name, consultation_fee, screenshot 
                FROM consultation_letters 
                WHERE payment_status = 'Paid' 
                ORDER BY consultation_id DESC
            """)
            paid_patients = cursor.fetchall()
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to fetch paid patients:\n{e}")
        return
    finally:
        if conn:
            conn.close()
    
    if not paid_patients:
        messagebox.showinfo("No Data", "No paid patients found.")
        return
    
    # Create the paid patients window
    paid_window = Toplevel()
    paid_window.title("Paid Patients - Screenshots")
    paid_window.configure(bg=DBC)
    paid_window.geometry("800x600")
    paid_window.resizable(True, True)
    
    # Center the window
    paid_window.transient()
    paid_window.grab_set()
    
    # Title
    title_label = ctk.CTkLabel(paid_window, text="💳 Paid Patients - Screenshot Viewer", 
                               font=("Arial", 24, "bold"), 
                               text_color=ACCENT_COLOR)
    title_label.pack(pady=20)
    
    # Create main frame with scrollbar
    main_frame = ctk.CTkFrame(paid_window, fg_color=LBC, corner_radius=10)
    main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    # Create canvas and scrollbar for scrolling
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
    for i, (consultation_id, patient_name, fee, screenshot_blob) in enumerate(paid_patients):
        # Patient frame
        patient_frame = ctk.CTkFrame(scrollable_frame, fg_color=DBC, corner_radius=8)
        patient_frame.pack(fill="x", padx=10, pady=5)
        
        # Patient info frame
        info_frame = ctk.CTkFrame(patient_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=10)
        
        # Patient details
        details_label = ctk.CTkLabel(info_frame, 
                                   text=f"ID: {consultation_id} | Patient: {patient_name} | Fee: ₹{fee}",
                                   font=("Arial", 14, "bold"),
                                   text_color=TEXT_COLOR)
        details_label.pack(side="left")
        
        # Show image button
        if screenshot_blob:
            show_img_btn = ctk.CTkButton(info_frame, text="📷 View Screenshot", 
                                       font=("Arial", 12, "bold"),
                                       fg_color=INFO_COLOR, hover_color=INFO_HOVER,
                                       width=140, height=30,
                                       corner_radius=6,
                                       command=lambda blob=screenshot_blob, name=patient_name: show_screenshot(blob, name))
            show_img_btn.pack(side="right", padx=(10, 0))
        else:
            no_img_label = ctk.CTkLabel(info_frame, text="No Screenshot", 
                                      font=("Arial", 12, "italic"),
                                      text_color="gray")
            no_img_label.pack(side="right", padx=(10, 0))
    
    # Bind mousewheel to canvas
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Close button
    close_btn = ctk.CTkButton(paid_window, text="Close", 
                            font=("Arial", 14, "bold"),
                            fg_color=REJECT_COLOR, hover_color=REJECT_HOVER,
                            width=100, height=35,
                            command=paid_window.destroy)
    close_btn.pack(pady=(0, 20))

def show_screenshot(screenshot_blob, patient_name):
    """Display the screenshot image in a new window."""
    if not screenshot_blob:
        messagebox.showwarning("No Image", "No screenshot available for this patient.")
        return
    
    try:
        # Convert blob to PIL Image
        image_data = io.BytesIO(screenshot_blob)
        pil_image = Image.open(image_data)
        
        # Create image display window
        img_window = Toplevel()
        img_window.title(f"Screenshot - {patient_name}")
        img_window.configure(bg=DBC)
        
        # Calculate window size based on image size (with max limits)
        img_width, img_height = pil_image.size
        max_width, max_height = 800, 600
        
        # Scale image if too large
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
        
        # Center the window
        img_window.transient()
        img_window.grab_set()
        
        # Title label
        title_label = ctk.CTkLabel(img_window, text=f"📸 {patient_name}'s Screenshot", 
                                 font=("Arial", 16, "bold"), 
                                 text_color=ACCENT_COLOR)
        title_label.pack(pady=10)
        
        # Image label
        img_label = ctk.CTkLabel(img_window, image=photo, text="")
        img_label.pack(pady=10)
        
        # Keep a reference to prevent garbage collection
        img_label.image = photo
        
        # Close button
        close_btn = ctk.CTkButton(img_window, text="Close", 
                                font=("Arial", 12, "bold"),
                                fg_color=REJECT_COLOR, hover_color=REJECT_HOVER,
                                width=80, height=30,
                                command=img_window.destroy)
        close_btn.pack(pady=10)
        
    except Exception as e:
        messagebox.showerror("Image Error", f"Failed to display screenshot:\n{e}")

def create_widgets(root):
    """Creates and places all the UI widgets on the screen."""
    global tree
    
    def on_enter(event):
        back_label.configure(text_color="grey") 

    def on_leave(event):
        back_label.configure(text_color="White")  
    
    back_label = ctk.CTkLabel(root, text="🔙", text_color="white", font=("Calibri", 40), cursor="hand2")
    back_label.place(x=5, y=5)

    back_label.bind("<Enter>", on_enter) 
    back_label.bind("<Leave>", on_leave) 
    back_label.bind("<Button-1>", lambda event: root.destroy())
    
    # --- Title Label ---
    title_label = ctk.CTkLabel(root, text="📝 Consultation Letters Review", 
                               font=("Arial", 28, "bold"), 
                               text_color=ACCENT_COLOR)
    title_label.place(relx=0.5, y=40, anchor="center")

    # --- Treeview Frame ---
    tree_frame = ctk.CTkFrame(root, fg_color=LBC, corner_radius=10)
    tree_frame.place(relx=0.5, rely=0.48, relwidth=0.92, relheight=0.70, anchor="center")

    # --- Treeview ---
    columns = ("consultation_id", "appointment_id", "patient_name", "days_requested", 
               "reason", "status", "payment_status", "consultation_type", "consultation_fee")
    
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style="Treeview")

    # Define column headings and properties
    for col in columns:
        tree.heading(col, text=col.replace("_", " ").title())
        width = 150 if col == "reason" else 120
        tree.column(col, anchor="center", width=width, stretch=True)
    
    # --- Scrollbar ---
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    
    # Adjust treeview placement to not overlap the scrollbar
    tree.place(relx=0, rely=0, relwidth=0.985, relheight=1)

    # --- Button Frame ---
    button_frame = ctk.CTkFrame(root, fg_color="transparent")
    button_frame.place(relx=0.5, rely=0.88, anchor="center")

    # --- Action Buttons ---
    approve_btn = ctk.CTkButton(button_frame, text="✔ Approve", font=("Arial", 16, "bold"),
                                fg_color=APPROVE_COLOR, hover_color=APPROVE_HOVER, text_color="black",
                                width=160, height=45, corner_radius=10,
                                command=lambda: update_status("Approved", "Paid"))
    approve_btn.pack(side="left", padx=15, pady=10)

    cancel_btn = ctk.CTkButton(button_frame, text="✖ Reject", font=("Arial", 16, "bold"),
                               fg_color=REJECT_COLOR, hover_color=REJECT_HOVER, text_color="white",
                               width=160, height=45, corner_radius=10,
                               command=lambda: update_status("Rejected", "Unpaid"))
    cancel_btn.pack(side="left", padx=15, pady=10)

    # --- Show Paid Patients Button ---
    paid_patients_btn = ctk.CTkButton(button_frame, text="💳 Show Paid Patients", font=("Arial", 16, "bold"),
                                    fg_color=INFO_COLOR, hover_color=INFO_HOVER, text_color="white",
                                    width=200, height=45, corner_radius=10,
                                    command=show_paid_patients)
    paid_patients_btn.pack(side="left", padx=15, pady=10)

def load_consultation_data():
    """Fetches consultation data from the database."""
    global consultation_data
    conn = get_connection()
    if not conn:
        return
        
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM consultation_letters ORDER BY consultation_id DESC")
            consultation_data = cursor.fetchall()
        refresh_treeview()
    except Exception as e:
        messagebox.showerror("Load Error", f"Failed to load data from the database:\n{e}")
    finally:
        if conn:
            conn.close()

def refresh_treeview():
    """Clears and repopulates the Treeview with the latest data and applies Arial font."""
    if not tree:
        return

    # Apply font style
    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 10))
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    # Clear existing items
    for item in tree.get_children():
        tree.delete(item)

    # Repopulate with new data
    for row in consultation_data:
        tree.insert("", "end", values=row)

def update_status(new_status, payment_status):
    """Updates the status of the selected consultation request in the database."""
    if not tree: return
    selected_item_id = tree.focus()
    if not selected_item_id:
        messagebox.showwarning("No Selection", "Please select a consultation request from the list.")
        return

    item = tree.item(selected_item_id)
    consultation_id = item['values'][0]

    conn = get_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cursor:
            query = "UPDATE consultation_letters SET status=%s, payment_status=%s WHERE consultation_id=%s"
            cursor.execute(query, (new_status, payment_status, consultation_id))
        conn.commit()
        messagebox.showinfo("Success", f"Consultation ID {consultation_id} has been {new_status}.")
        load_consultation_data()  # Reload data to show the change
    except Exception as e:
        messagebox.showerror("Update Error", f"Failed to update status:\n{e}")
    finally:
        if conn:
            conn.close()

# --- Main Application Setup ---
if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Clincloud - Consultation Review")
    app.configure(fg_color=DBC)

    # Set fullscreen geometry
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    app.geometry(f"{screen_width}x{screen_height}+0+0")
    
    # --- UI Creation ---
    create_styles(app)
    create_widgets(app)

    # --- Initial Data Load ---
    app.after(100, load_consultation_data) # Use 'after' to ensure main window is ready

    app.mainloop()