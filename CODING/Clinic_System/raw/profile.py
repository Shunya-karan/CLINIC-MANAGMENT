import customtkinter as ctk
from PIL import Image, ImageDraw, ImageOps
from tkinter import messagebox, filedialog
import json
import os
import re
import pymysql
# --- Constants ---
PROFILE_DATA_FILE = "profile_data.json"

# --- Colors ---
# Modern and clean color palette from the user's last provided script
COLOR_PRIMARY = "#067EFF"        # Blue for the main background
COLOR_SECONDARY = "#FFFFFF"      # White for card backgrounds
COLOR_ACCENT = "#5C5C5C"          # Grey for accents and interactive elements
COLOR_ACCENT_HOVER = "#494848"    # Darker Grey for hover effects
COLOR_TEXT = "#000000"            # Black for text for better readability
COLOR_SUCCESS = "#00B894"         # A nice green for save/success buttons
COLOR_SUCCESS_HOVER = "#00896F"   # Darker green for hover

# --- Global Variables ---
profile_data = {}
info_widgets = {}
entries = {}
edit_window = None
new_profile_pic_path = None
app = None
profile_image_label = None
name_label = None
degree_label = None


# --- Data Handling ---
def load_profile_data():
    """Loads profile data from the JSON file."""
    global profile_data
    default_data = {
    "name": "Karan Yadav",
    "age": "42",
    "phone": "7039231124",
    "gender": "Male",
    "experience": "9 Years",
    "degree": "M.B.B.S",
    "dob": "12 - 01 - 1983",
    "address": "ABC Apartments, XYZ Area, Chembur, Mumbai 40072",
    "profile_pic": "C:/Made By me/Clg projects/CODING/doctor-with-his-arms-crossed-white-background_1368-5790.jpg"
}
    try:
        with open(PROFILE_DATA_FILE, "r") as file:
            profile_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        save_profile_data(default_data)
        profile_data = default_data

def save_profile_data(data):
    """Saves profile data to the JSON file."""
    with open(PROFILE_DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# --- Input Validation ---
def validate_inputs():
    """Validates user inputs using regular expressions."""
    # Regex patterns for validation
    patterns = {
        "name": (r"^[a-zA-Z. ]+$", "Name can only contain letters, spaces, and dots."),
        "age": (r"^\d{1,3}$", "Age must be a number (up to 3 digits)."),
        "phone": (r"^\d{10}$|^\d{3}-\d{3}-\d{4}$", "Phone must be 10 digits or in XXX-XXX-XXXX format."),
        "gender": (r"^[a-zA-Z]+$", "Gender can only contain letters."),
        "experience": (r"^\d{1,2} Years$", "Experience must be in the format 'XX Years' (e.g., '15 Years')."),
        "dob": (r"^\d{2} - \d{2} - \d{4}$", "Date of Birth must be in DD - MM - YYYY format."),
        "address": (r"^[a-zA-Z0-9\s.,#-]+$", "Address contains invalid characters."),
        "degree": (r"^[a-zA-Z0-9\s.,()-]+$", "Degree contains invalid characters.")
    }


    for field, entry in entries.items():
        input_value = entry.get().strip()
        # Only validate if there is an input value and a pattern for the field
        if input_value and field in patterns:
            pattern, error_message = patterns[field]
            if not re.match(pattern, input_value):
                messagebox.showerror("Invalid Input", f"Error in '{field.title()}':\n{error_message}", parent=edit_window)
                return False # Validation failed
    return True # All validations passed


# --- UI Helper Functions ---

def get_connection():
    return pymysql.connect(host="localhost", user="root", password="root", database="clinic_management")
def Deactive_doctor_window():
    # messagebox.askyesno(" Confirm Deactivation", "Are you sure you want to deactivate Account?", parent=edit_window)
        def deactivate_account():
            username = entry_username.get()
            password = entry_password.get()

            if not username or not password:
                messagebox.showwarning("Input Error", "All fields are required.")
                return

            try:
                conn = get_connection()
                cursor = conn.cursor()

                # Verify credentials
                cursor.execute("SELECT * FROM doctor_login WHERE username=%s AND password=%s AND is_active='TRUE'", (username, password))
                result = cursor.fetchone()

                if result:
                    cursor.execute("UPDATE doctor_login SET is_active='FALSE' WHERE username=%s", (username,))
                    conn.commit()
                    messagebox.showinfo("Deactivated", "Account deactivated successfully.")
                    window.destroy()
                    root.destroy()
                else:
                    messagebox.showerror("Error", "Invalid credentials or account already deactivated.")

            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

        # Small Toplevel Window
        window = ctk.CTkToplevel()
        window.title("Deactivate Doctor Account")
        window.geometry("300x200")
        window.resizable(False, False)
        window.grab_set()

        # Widgets
        ctk.CTkLabel(window, text="Username:").place(x=30, y=30)
        entry_username = ctk.CTkEntry(window, width=220)
        entry_username.place(x=30, y=55)

        ctk.CTkLabel(window, text="Password:").place(x=30, y=90)
        entry_password = ctk.CTkEntry(window, show="*", width=220)
        entry_password.place(x=30, y=115)

        ctk.CTkButton(window, text="Deactivate", command=deactivate_account).place(x=80, y=150)
    
def create_info_card(parent, label_text, value_text):
    """Helper function to create a styled card for information."""
    # Note: The colors in this function were not matching the main theme.
    # I've updated them to use the main color constants for consistency.
    card_frame = ctk.CTkFrame(parent, fg_color=COLOR_PRIMARY, corner_radius=10)

    label = ctk.CTkLabel(card_frame, text=label_text, font=("Arial", 14, "bold"), text_color="#FFFFFF", anchor="w")
    label.pack(fill="x", padx=15, pady=(10, 2))

    value = ctk.CTkLabel(card_frame, text=value_text, font=("Arial", 16), text_color="#FFFFFF", anchor="w", wraplength=350)
    value.pack(fill="x", padx=15, pady=(0, 10))

    return card_frame, value

def make_image_circular(image_path, size):
    """Crops an image to be circular."""
    try:
        img = Image.open(image_path).convert("RGBA")
    except (FileNotFoundError, AttributeError):
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0,0), (size,size)], fill=COLOR_SECONDARY)
        draw.text((size//2, size//2), "No\nImage", fill=COLOR_TEXT, anchor="mm", font=ctk.CTkFont(family="Arial", size=24))

    img = ImageOps.fit(img, (size, size), Image.Resampling.LANCZOS)
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)

    circular_img = ImageOps.fit(img, (size, size), centering=(0.5, 0.5))
    circular_img.putalpha(mask)

    return circular_img

def update_profile_image():
    """Loads and displays the circular profile image."""
    global profile_image_label
    circular_pil_image = make_image_circular(profile_data.get("profile_pic"), size=200)
    ctk_image = ctk.CTkImage(light_image=circular_pil_image, size=(200, 200))

    if profile_image_label:
        profile_image_label.configure(image=ctk_image)
        profile_image_label.image = ctk_image

def refresh_profile_display():
    """Updates all UI elements with the current profile_data."""
    global name_label, degree_label, info_widgets
    load_profile_data()

    if name_label:
        name_label.configure(text=profile_data.get("name", "N/A"))
    if degree_label:
        degree_label.configure(text=profile_data.get("degree", "N/A"))

    for key, widget in info_widgets.items():
        # The 'age' field needs special formatting
        if key == "age":
            widget.configure(text=f"{profile_data.get(key, 'N/A')} years")
        else:
            widget.configure(text=profile_data.get(key, "N/A"))

    update_profile_image()

def upload_photo():
    """Handles the logic for uploading a new photo."""
    global new_profile_pic_path, edit_window
    file_path = filedialog.askopenfilename(
        title="Select a Profile Picture",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg")],
        parent=edit_window
    )
    if file_path:
        new_profile_pic_path = file_path
        messagebox.showinfo("Photo Selected", "New profile picture selected. Click 'Save Changes' to apply.", parent=edit_window)

def save_profile():
    """Saves the updated profile data from the edit window after validation."""
    global profile_data, entries, new_profile_pic_path, edit_window

    # --- Step 1: Validate all inputs before saving ---
    if not validate_inputs():
        return # Stop the save process if validation fails

    # --- Step 2: If validation passes, proceed to save ---
    for field, entry in entries.items():
        input_value = entry.get().strip()
        if input_value:
            profile_data[field] = input_value

    if new_profile_pic_path:
        profile_data["profile_pic"] = new_profile_pic_path
        new_profile_pic_path = None

    save_profile_data(profile_data)
    if edit_window:
        edit_window.destroy()
    refresh_profile_display()
    messagebox.showinfo("Success", "Profile updated successfully!")

def open_edit_window():
    """Opens the Toplevel window for editing profile details."""
    global edit_window, entries, app
    if edit_window and edit_window.winfo_exists():
        edit_window.focus()
        return

    edit_window = ctk.CTkToplevel(app)
    edit_window.title("Edit Profile")
    edit_window.geometry("500x700")
    edit_window.configure(fg_color=COLOR_PRIMARY)
    edit_window.transient(app)
    edit_window.grab_set()

    edit_main_frame = ctk.CTkScrollableFrame(edit_window, fg_color="transparent")
    edit_main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    heading = ctk.CTkLabel(edit_main_frame, text="Edit Profile Details", font=("Arial", 20, "bold"), text_color="#FFFFFF")
    heading.pack(pady=(0, 20))

    upload_button = ctk.CTkButton(
        edit_main_frame, text="Change Profile Picture", command=upload_photo,
        fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, font=("Arial", 14), text_color="#FFFFFF"
    )
    upload_button.pack(pady=15, padx=20, fill='x')

    entries = {}
    fields = ["name", "degree", "age", "phone", "gender", "experience", "dob", "address"]
    for field in fields:
        frame = ctk.CTkFrame(edit_main_frame, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=8)

        label = ctk.CTkLabel(frame, text=field.replace("_", " ").title(), font=("Arial", 14), anchor="w", text_color="#FFFFFF")
        label.pack(fill="x")

        entry = ctk.CTkEntry(
            frame, placeholder_text=f"Enter {field.replace('_', ' ').title()}",
            width=400, font=("Arial", 14), fg_color=COLOR_SECONDARY,
            border_color=COLOR_ACCENT, text_color="Black"
        )
        entry.insert(0, profile_data.get(field, ""))
        entry.pack(fill="x", pady=(2,0))
        entries[field] = entry

    button_frame = ctk.CTkFrame(edit_main_frame, fg_color="transparent")
    button_frame.pack(pady=30, padx=20, fill="x")
    button_frame.grid_columnconfigure((0,1), weight=1)

    save_button = ctk.CTkButton(
        button_frame, text="Save Changes", command=save_profile,
        fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER, height=40, font=("Arial", 14, "bold")
    )
    save_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

    cancel_button = ctk.CTkButton(
        button_frame, text="Cancel", command=edit_window.destroy,
        fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, height=40, font=("Arial", 14, "bold"), text_color="#FFFFFF"
    )
    cancel_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")

def setup_ui(root):
    """Sets up the main UI of the application."""
    global app, profile_image_label, name_label, degree_label, info_widgets
    app = root

    main_frame = ctk.CTkFrame(app, fg_color="transparent")
    main_frame.pack(padx=20, pady=20, fill="both", expand=True)
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(1, weight=1)

    header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 20))
    header_frame.grid_columnconfigure(1, weight=1)

    back_button = ctk.CTkButton(
        header_frame, text="🔙", command=app.destroy, fg_color="transparent",
        text_color="#FFFFFF", hover_color=COLOR_PRIMARY, font=("Arial", 36)
    )
    back_button.grid(row=0, column=0, sticky="w")

    heading = ctk.CTkLabel(header_frame, text="Doctor Profile", font=("Arial", 32, "bold"), text_color="#FFFFFF")
    heading.grid(row=0, column=1, sticky="ew")

    content_frame = ctk.CTkFrame(main_frame, fg_color=COLOR_SECONDARY, corner_radius=15)
    content_frame.grid(row=1, column=0, sticky="nsew", padx=10)
    content_frame.grid_columnconfigure(0, weight=3)
    content_frame.grid_columnconfigure(1, weight=7)
    content_frame.grid_rowconfigure(0, weight=1)

    left_panel = ctk.CTkFrame(content_frame, fg_color="transparent")
    left_panel.grid(row=0, column=0, sticky="nsew", padx=(30, 15), pady=30)
    left_panel.grid_rowconfigure(1, weight=1)

    profile_image_label = ctk.CTkLabel(left_panel, text="")
    profile_image_label.pack(pady=(20, 15), anchor="center")

    name_label = ctk.CTkLabel(left_panel, text="", font=("Arial", 26, "bold"), text_color=COLOR_TEXT, wraplength=300)
    name_label.pack(pady=5, anchor="center")

    degree_label = ctk.CTkLabel(left_panel, text="", font=("Arial", 16), text_color=COLOR_ACCENT)
    degree_label.pack(pady=(0, 20), anchor="center")

    edit_button = ctk.CTkButton(
        left_panel, text="Edit Profile", command=open_edit_window, fg_color=COLOR_ACCENT,
        hover_color=COLOR_ACCENT_HOVER, text_color="#FFFFFF", height=40,
        corner_radius=8, font=("Arial", 14, "bold")
    )
    edit_button.pack(pady=20, fill="x", padx=20, anchor="center")

    deactive_button = ctk.CTkButton(
        left_panel, text="Deactivate Account", command=Deactive_doctor_window, fg_color="Red",
        hover_color=COLOR_ACCENT_HOVER, text_color="#FFFFFF", height=40,
        corner_radius=8, font=("Arial", 14, "bold")
    )
    deactive_button.pack(pady=5, fill="x", padx=20, anchor="center")

    right_panel = ctk.CTkFrame(content_frame, fg_color="transparent")
    right_panel.grid(row=0, column=1, sticky="nsew", padx=(15, 30), pady=30)
    right_panel.grid_columnconfigure((0, 1), weight=1)

    info_fields = {
        "👤 Gender": "gender", "🎂 Date of Birth": "dob", "📞 Phone": "phone",
        "⏳ Age": "age", "⭐ Experience": "experience", "📍 Clinic Address": "address"
    }

    row, col = 0, 0
    info_widgets = {} # Re-initialize to avoid duplicates on refresh
    for label_text, data_key in info_fields.items():
        frame, value_label = create_info_card(right_panel, label_text, "")
        frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
        info_widgets[data_key] = value_label
        col += 1
        if col > 1:
            col, row = 0, row + 1

    if "address" in info_widgets:
        info_widgets["address"].master.grid_configure(columnspan=2)

    refresh_profile_display()


if __name__ == "__main__":
    if not os.path.exists(PROFILE_DATA_FILE):
        load_profile_data()


    def maximize_window():
        if root.winfo_exists():  # Ensure the window still exists
            root.state("zoomed")

    ctk.set_appearance_mode("light")  # Set light mode appearance
    ctk.set_default_color_theme("blue")  # Use green theme
    root = ctk.CTk()
    root.title("A.K Healthcare")  # Set window title
    root.configure(fg_color=COLOR_PRIMARY)  # Light green
    root.after(100, maximize_window)

    ctk.set_appearance_mode("dark")

    setup_ui(root)
    root.mainloop()
