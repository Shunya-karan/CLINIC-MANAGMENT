import customtkinter as ctk
import time
import threading
import subprocess
from customtkinter import CTkImage
from PIL import Image
import math

# Function to open a new file
def open_new_file():
    subprocess.Popen(["python", "Clinic_System/raw/signup_login.py"]) 

# Set modern appearance
ctk.set_appearance_mode("light")  
ctk.set_default_color_theme("blue") 

# Create main window
loading_window = ctk.CTk()
loading_window.title("A.K Healthcare - Loading")
loading_window.geometry("970x550")
loading_window.resizable(False, False)

# Center the window on screen
loading_window.update_idletasks()
width = loading_window.winfo_width()
height = loading_window.winfo_height()
x = (loading_window.winfo_screenwidth() // 2) - (width // 2)
y = (loading_window.winfo_screenheight() // 2) - (height // 2)
loading_window.geometry(f'{width}x{height}+{x}+{y}')

# Light Blue and Dark Blue color scheme
COLORS = {
    'primary': '#0F172A',      # Very dark blue
    'secondary': '#1E40AF',    # Dark blue
    'accent': '#3B82F6',       # Medium blue
    'light_blue': '#DBEAFE',   # Very light blue
    'background': '#EFF6FF',   # Light blue background
    'surface': '#FFFFFF',      # White
    'text_primary': '#1E3A8A', # Dark blue text
    'text_secondary': '#3B82F6', # Medium blue text
    'success': '#2563EB'       # Blue success
}

# Main background
main_bg = ctk.CTkFrame(loading_window, fg_color=COLORS['background'], width=1200, height=700, corner_radius=0)
main_bg.place(x=0, y=0)

# Central card container with light blue background
card_container = ctk.CTkFrame(
    main_bg, 
    width=800, 
    height=500, 
    fg_color=COLORS['surface'],
    corner_radius=20,
    border_width=2,
    border_color=COLORS['accent']
)
card_container.place(relx=0.5, rely=0.5, anchor='center')

# Header section with dark blue gradient
header_frame = ctk.CTkFrame(
    card_container,
    width=780,
    height=120,
    fg_color=COLORS['secondary'],
    corner_radius=15
)
header_frame.place(x=10, y=10)

# Logo container with light blue background
logo_container = ctk.CTkFrame(
    header_frame,
    width=80,
    height=80,
    fg_color=COLORS['light_blue'],
    corner_radius=40
)
logo_container.place(x=30, y=20)

# Load logo (with error handling)
try:
    logo_image = Image.open("Clinic_System/build/clinic-logo.png")
    logo_ctk_image = CTkImage(light_image=logo_image, size=(50, 50))
    logo_label = ctk.CTkLabel(logo_container, image=logo_ctk_image, text="")
    logo_label.place(relx=0.5, rely=0.5, anchor='center')
except:
    # Fallback if logo not found
    logo_label = ctk.CTkLabel(
        logo_container, 
        text="CLINICLOUD", 
        font=("Arial", 20, "bold"),
        text_color=COLORS['secondary']
    )
    logo_label.place(relx=0.5, rely=0.5, anchor='center')

# Company name and tagline
company_name = ctk.CTkLabel(
    header_frame,
    text="CLINICLOUD",
    font=("Segoe UI", 36, "bold"),
    text_color=COLORS['surface']
)
company_name.place(x=130, y=25)

tagline = ctk.CTkLabel(
    header_frame,
    text="Advanced Medical Solutions",
    font=("Segoe UI", 14),
    text_color=COLORS['light_blue']
)
tagline.place(x=130, y=70)

# Loading section
loading_frame = ctk.CTkFrame(
    card_container,
    width=780,
    height=350,
    fg_color="transparent"
)
loading_frame.place(x=10, y=140)

# Modern loading spinner container
spinner_frame = ctk.CTkFrame(
    loading_frame,
    width=120,
    height=120,
    fg_color="transparent"
)
spinner_frame.place(relx=0.5, rely=0.3, anchor='center')

# Create spinner label once
spinner_label = ctk.CTkLabel(
    spinner_frame,
    text="◐",
    font=("Arial", 48),
    text_color=COLORS['accent']
)
spinner_label.place(relx=0.5, rely=0.5, anchor='center')

# Loading status
status_label = ctk.CTkLabel(
    loading_frame,
    text="Initializing System...",
    font=("Segoe UI", 18, "bold"),
    text_color=COLORS['text_primary']
)
status_label.place(relx=0.5, rely=0.6, anchor='center')

# Animated dots
dots_label = ctk.CTkLabel(
    loading_frame,
    text="",
    font=("Segoe UI", 16),
    text_color=COLORS['accent']
)
dots_label.place(relx=0.5, rely=0.68, anchor='center')

# Modern progress bar with light blue background
progress_container = ctk.CTkFrame(
    loading_frame,
    width=600,
    height=40,
    fg_color=COLORS['light_blue'],
    corner_radius=20
)
progress_container.place(relx=0.5, rely=0.8, anchor='center')

progress_bar = ctk.CTkProgressBar(
    progress_container,
    width=580,
    height=20,
    fg_color=COLORS['light_blue'],
    progress_color=COLORS['secondary'],
    corner_radius=10
)
progress_bar.place(relx=0.5, rely=0.5, anchor='center')
progress_bar.set(0)

# Progress percentage
progress_text = ctk.CTkLabel(
    loading_frame,
    text="0%",
    font=("Segoe UI", 12, "bold"),
    text_color=COLORS['text_secondary']
)
progress_text.place(relx=0.5, rely=0.9, anchor='center')

# Loading messages for different stages
loading_messages = [
    "Initializing System...",
    "Loading Healthcare Modules...",
    "Connecting to Database...",
    "Preparing User Interface...",
    "Finalizing Setup...",
    "Ready to Launch!"
]

# Global variables
progress = 0
current_message = 0
spinner_angle = 0
running = True  # Flag to control animations

# Animated loading dots
def animate_dots():
    dots = 0
    while progress < 1 and running:
        try:
            dots_text = "●" * (dots + 1) + "○" * (3 - dots)
            if running:
                dots_label.configure(text=dots_text)
            dots = (dots + 1) % 3
            time.sleep(0.06)
        except:
            break

# Spinning loader animation
def animate_spinner():
    global spinner_angle
    while progress < 1 and running:
        try:
            # Create a simple rotating effect with text
            spinner_chars = ["◐", "◓", "◑", "◒"]
            char_index = (int(spinner_angle / 90)) % 4
            
            if running:
                spinner_label.configure(text=spinner_chars[char_index])
            
            spinner_angle = (spinner_angle + 10) % 360
            time.sleep(0.04)
        except:
            break

# Progress bar update with smooth animation
def update_progress():
    global progress, current_message, running
    
    for i in range(101):
        if not running:
            break
            
        progress = i / 100
        try:
            progress_bar.set(progress)
            progress_text.configure(text=f"{i}%")
            
            # Update loading message based on progress
            message_index = min(int(progress * len(loading_messages)), len(loading_messages) - 1)
            if message_index != current_message:
                current_message = message_index
                status_label.configure(text=loading_messages[current_message])
        except:
            break
        
        # Variable sleep for more realistic loading
        if i < 30:
            time.sleep(0.005)  # Fast start
        elif i < 70:
            time.sleep(0.008)  # Slower middle
        elif i < 95:
            time.sleep(0.02)  # Even slower near end
        else:
            time.sleep(0.006)   # Dramatic pause before completion
    
    # Success message
    try:
        if running:
            status_label.configure(text="Launch Successful! Opening Application...")
            time.sleep(1)
            
            # Fade out effect (optional)
            loading_window.attributes('-alpha', 0.8)
            time.sleep(0.06)
            loading_window.attributes('-alpha', 0.6)
            time.sleep(0.06)
            loading_window.attributes('-alpha', 0.4)
            time.sleep(0.06)
            
            running = False  # Stop all animations
            open_new_file()
            loading_window.destroy()
    except:
        pass

# Professional version info
version_label = ctk.CTkLabel(
    main_bg,
    text="Version 2.1.0 | © 2025 CLINCCLOUD Healthcare Systems",
    font=("Segoe UI", 10),
    text_color=COLORS['text_secondary']
)
version_label.place(relx=0.5, rely=0.95, anchor='center')

# Start all animations in separate threads
threading.Thread(target=update_progress, daemon=True).start()
threading.Thread(target=animate_dots, daemon=True).start()
threading.Thread(target=animate_spinner, daemon=True).start()

# Window close handler
def on_closing():
    global running
    running = False
    time.sleep(0.01)  # Give threads time to stop
    loading_window.destroy()

# Set the window close protocol
loading_window.protocol("WM_DELETE_WINDOW", on_closing)

# Make window appear on top initially
loading_window.lift()
loading_window.focus_force()

# Start the application
loading_window.mainloop()