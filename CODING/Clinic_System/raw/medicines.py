from tkinter import *
from tkinter import ttk, messagebox
import customtkinter as ctk
import pymysql
from tkcalendar import DateEntry
import re
from datetime import datetime

# Modern Color Scheme
COLORS = {
    'primary': "#4EBEFA",       # Teal
    'secondary': '#48CAE4',     # Light blue
    'accent': '#90E0EF',        # Very light blue
    'dark': '#023047',          # Dark blue
    'light': '#CAF0F8',         # Very light cyan
    'white': '#FFFFFF',
    'success': '#06D6A0',       # Green
    'warning': '#FFD60A',       # Yellow
    'danger': '#EF476F',        # Red
    'text': '#343A40'           # Dark gray
}

class HealthcareManagementSystem:
    def __init__(self):
        self.conn = None # Initialize connection to None
        self.setup_main_window()
        self.setup_database() # Establish connection
        self.create_header()
        self.create_main_content()
        self.root.mainloop() # Start the Tkinter event loop
    
    def setup_main_window(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.configure(fg_color=COLORS['white'])
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0") 
        # Make window resizable and maximize
        # self.root.state('zoomed')
    
    def setup_database(self):
        """Database connectivity function"""
        try:
            self.conn = pymysql.connect(
                host="localhost",
                user="root",
                password="root",
                database="clinic_management"
            )
            # Optional: Test connection
            # with self.conn.cursor() as cursor:
            #     cursor.execute("SELECT 1")
            # print("Database connected successfully!")
            return self.conn
        except pymysql.MySQLError as e:
            print("Error connecting to database:", e)
            messagebox.showerror("Database Error", f"Error connecting to database:\n{e}")
            self.conn = None # Ensure conn is None if connection fails
            return None
    
    def get_db_connection(self):
        """Ensures a valid database connection is available."""
        if self.conn is None or not self.conn.open:
            self.setup_database()
        return self.conn

    def create_header(self):
        """Create modern header with navigation"""
        header_frame = ctk.CTkFrame(self.root, height=80, fg_color=COLORS['primary'])
        header_frame.pack(fill=X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        back_button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        back_button_frame.place(x=2,y=5)       
        back_button = ctk.CTkButton(
                back_button_frame, text="🔙", command=self.root.destroy, fg_color="transparent",
                text_color="#0C0C0C", hover_color="grey", font=("Arial", 56)
            )
        back_button.grid(row=0, column=0, sticky="w")
        # Left side - Logo and title
        left_header = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_header.place(x=680,y=5)
        global title_label 
        title_label = ctk.CTkLabel(
            left_header, 
            text="",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="black"
        )
        title_label.pack(side=LEFT, pady=15)
        
        # Right side - Navigation buttons
        right_header = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_header.pack(side=RIGHT, fill=Y, padx=20)
        
        nav_buttons = [
            ("📋 Medicines", self.show_medicines_tab),
            ("🏢 Suppliers", self.show_suppliers_tab),
        ]
        
        self.nav_buttons = {}
        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                right_header,
                text=text,
                command=command,
                width=120,
                height=40,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=COLORS['secondary'],
                hover_color=COLORS['accent'],
                text_color=COLORS['dark']
            )
            btn.pack(side=LEFT, padx=5, pady=15)
            self.nav_buttons[text] = btn
    
    def create_main_content(self):
        """Create main content area"""
        self.main_frame = ctk.CTkFrame(self.root, fg_color=COLORS['white'])
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Show medicines tab by default
        self.current_tab = None # Initialize to None so the first call triggers content creation
        self.show_medicines_tab()
    
    def clear_main_frame(self):
        """Clear the main content frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_medicines_tab(self):
        """Display medicines management interface"""
        if self.current_tab == "medicines":
            return
            
        self.current_tab = "medicines"
        self.clear_main_frame()
        
        # Update nav button colors
        self.update_nav_buttons("📋 Medicines")
        
        # Create medicines interface
        self.create_medicines_interface()
    
    def show_suppliers_tab(self):
        """Display suppliers management interface"""
        if self.current_tab == "suppliers":
            return
            
        self.current_tab = "suppliers"
        self.clear_main_frame()
        
        # Update nav button colors
        self.update_nav_buttons("🏢 Suppliers")
        
        # Create suppliers interface
        self.create_suppliers_interface()
    

    def update_nav_buttons(self, active_button):
        """Update navigation button colors"""
        for text, btn in self.nav_buttons.items():
            if text == active_button:
                btn.configure(fg_color=COLORS['accent'], text_color=COLORS['dark'])
            else:
                btn.configure(fg_color=COLORS['secondary'], text_color=COLORS['dark'])
    
    def create_medicines_interface(self):
        """Create medicines management interface"""
        # Top section with search and filters
        title_label.configure(text="🏥Medicines")
        top_section = ctk.CTkFrame(self.main_frame, height=80, fg_color=COLORS['light'])
        top_section.pack(fill=X, padx=10, pady=(10, 5))
        top_section.pack_propagate(False)
        
        # Search functionality
        search_frame = ctk.CTkFrame(top_section, fg_color="transparent")
        search_frame.pack(side=LEFT, fill=Y, padx=10)
        
        ctk.CTkLabel(search_frame, text="🔍 Search:", font=ctk.CTkFont(size=14, weight="bold")).pack(side=LEFT, padx=(0, 5))
        self.search_entry = ctk.CTkEntry(search_frame, width=200, placeholder_text="Search medicines...")
        self.search_entry.pack(side=LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_medicines)
        
        # Action buttons
        action_frame = ctk.CTkFrame(top_section, fg_color="transparent")
        action_frame.pack(side=RIGHT, fill=Y, padx=10)
        
        buttons = [
            ("➕ Add Medicine", self.add_medicine_dialog, COLORS['success']),
            ("✏️ Update", self.update_medicine_dialog, COLORS['primary']),
            ("🗑️ Delete", self.delete_medicine_dialog, COLORS['danger']),
            ("⚠️ Expiring Soon", self.show_expiring_medicines, COLORS['warning']),
            ("🔄 Refresh", self.refresh_medicines, COLORS['secondary'])
        ]
        
        for text, command, color in buttons:
            btn = ctk.CTkButton(
                action_frame,
                text=text,
                command=command,
                width=120,
                height=35,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=color,
                hover_color=color,
                text_color=COLORS['white'] if color != COLORS['warning'] else COLORS['dark']
            )
            btn.pack(side=LEFT, padx=2)
        
        # Medicine list
        list_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS['white'])
        list_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview with modern styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", 
                        background=COLORS['white'], 
                        foreground=COLORS['text'], 
                        rowheight=30, 
                        fieldbackground=COLORS['white'],
                        borderwidth=0,
                        font=('Segoe UI', 10))
        style.map("Treeview", 
                  background=[("selected", COLORS['primary'])],
                  foreground=[("selected", COLORS['white'])])
        style.configure("Treeview.Heading", 
                        font=('Segoe UI', 11, 'bold'),
                        background=COLORS['secondary'],
                        foreground=COLORS['dark'])
        
        # Treeview for medicines
        self.medicine_tree = ttk.Treeview(
            list_frame,
            columns=("id", "name", "brand", "chemical", "supplier", "stock", "expiry", "price", "cost"),
            show='headings',
            height=20
        )
        
        # Define headings
        headings = [
            ("id", "ID", 60),
            ("name", "Medicine Name", 150),
            ("brand", "Brand", 120),
            ("chemical", "Chemical Component", 180),
            ("supplier", "Supplier ID", 100),
            ("stock", "Stock", 80),
            ("expiry", "Expiry Date", 120),
            ("price", "Selling Price", 100),
            ("cost", "Cost Price", 100)
        ]
        
        for col, heading, width in headings:
            self.medicine_tree.heading(col, text=heading, anchor="center")
            self.medicine_tree.column(col, width=width, anchor="center")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.medicine_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient="horizontal", command=self.medicine_tree.xview)
        self.medicine_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.medicine_tree.pack(side=LEFT, fill=BOTH, expand=True)
        v_scrollbar.pack(side=RIGHT, fill=Y)
        h_scrollbar.pack(side=BOTTOM, fill=X)
        
        # Load medicines
        self.load_medicines()
    
    def create_suppliers_interface(self):
        """Create suppliers management interface"""
        # Top section with search and filters
        title_label.configure(text="🏢 Suppliers")
        top_section = ctk.CTkFrame(self.main_frame, height=80, fg_color=COLORS['light'])
        top_section.pack(fill=X, padx=10, pady=(10, 5))
        top_section.pack_propagate(False)
        
        # Search functionality
        search_frame = ctk.CTkFrame(top_section, fg_color="transparent")
        search_frame.pack(side=LEFT, fill=Y, padx=10)
        
        ctk.CTkLabel(search_frame, text="🔍 Search:", font=ctk.CTkFont(size=14, weight="bold")).pack(side=LEFT, padx=(0, 5))
        self.supplier_search_entry = ctk.CTkEntry(search_frame, width=200, placeholder_text="Search suppliers...")
        self.supplier_search_entry.pack(side=LEFT, padx=5)
        self.supplier_search_entry.bind('<KeyRelease>', self.search_suppliers)
        
        # Action buttons
        action_frame = ctk.CTkFrame(top_section, fg_color="transparent")
        action_frame.pack(side=RIGHT, fill=Y, padx=10)
        
        buttons = [
            ("➕ Add Supplier", self.add_supplier_dialog, COLORS['success']),
            ("✏️ Update", self.update_supplier_dialog, COLORS['primary']),
            ("🗑️ Delete", self.delete_supplier_dialog, COLORS['danger']),
            ("🔄 Refresh", self.refresh_suppliers, COLORS['secondary'])
        ]
        
        for text, command, color in buttons:
            btn = ctk.CTkButton(
                action_frame,
                text=text,
                command=command,
                width=120,
                height=35,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=color,
                hover_color=color,
                text_color=COLORS['white']
            )
            btn.pack(side=LEFT, padx=2)
        
        # Supplier list
        list_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS['white'])
        list_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        # Treeview for suppliers
        self.supplier_tree = ttk.Treeview(
            list_frame,
            columns=("id", "name", "contact_person", "phone", "email", "address", "created_at"),
            show='headings',
            height=20
        )
        
        # Define headings
        headings = [
            ("id", "ID", 60),
            ("name", "Supplier Name", 180),
            ("contact_person", "Contact Person", 150),
            ("phone", "Phone", 120),
            ("email", "Email", 200),
            ("address", "Address", 250),
            ("created_at", "Created At", 120)
        ]
        
        for col, heading, width in headings:
            self.supplier_tree.heading(col, text=heading, anchor="center")
            self.supplier_tree.column(col, width=width, anchor="center")
        
        # Scrollbars for suppliers
        v_scrollbar_sup = ttk.Scrollbar(list_frame, orient="vertical", command=self.supplier_tree.yview)
        h_scrollbar_sup = ttk.Scrollbar(list_frame, orient="horizontal", command=self.supplier_tree.xview)
        self.supplier_tree.configure(yscrollcommand=v_scrollbar_sup.set, xscrollcommand=h_scrollbar_sup.set)
        
        # Pack supplier treeview and scrollbars
        self.supplier_tree.pack(side=LEFT, fill=BOTH, expand=True)
        v_scrollbar_sup.pack(side=RIGHT, fill=Y)
        h_scrollbar_sup.pack(side=BOTTOM, fill=X)
        
        # Load suppliers
        self.load_suppliers()
    
    def load_medicines(self):
        """Load medicines from database"""
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                # Ensure the query matches your actual table columns including cost_price
                cursor.execute("SELECT medicine_id, medicine_name, brand_name, chemical_component, supplier_id, stock_quantity, expiry_date, price, cost_price FROM medicines ORDER BY medicine_id")
                results = cursor.fetchall()
                
                # Clear existing items
                for item in self.medicine_tree.get_children():
                    self.medicine_tree.delete(item)
                
                # Insert new items
                for row in results:
                    # Convert expiry_date to string if it's a datetime object
                    row_list = list(row)
                    if isinstance(row_list[6], (datetime,)): # expiry_date is at index 6
                        row_list[6] = row_list[6].strftime("%Y-%m-%d")
                    self.medicine_tree.insert('', 'end', values=row_list)
                
        except pymysql.MySQLError as e:
            messagebox.showerror("Database Error", f"Failed to load medicines: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while loading medicines: {e}")
        finally:
            if conn and conn.open:
                conn.close() # Close connection after use

    def load_suppliers(self):
        """Load suppliers from database"""
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM suppliers ORDER BY supplier_id")
                results = cursor.fetchall()
                
                # Clear existing items
                for item in self.supplier_tree.get_children():
                    self.supplier_tree.delete(item)
                
                # Insert new items
                for row in results:
                    row_list = list(row)
                    if row_list[6]:  # created_at field is at index 6
                        row_list[6] = row_list[6].strftime("%Y-%m-%d %H:%M")
                    self.supplier_tree.insert('', 'end', values=row_list)
                
        except pymysql.MySQLError as e:
            messagebox.showerror("Database Error", f"Failed to load suppliers: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while loading suppliers: {e}")
        finally:
            if conn and conn.open:
                conn.close() # Close connection after use
    
    def search_medicines(self, event=None):
        """Search medicines in the treeview"""
        search_term = self.search_entry.get().lower()
        
        # Clear current selection
        for item in self.medicine_tree.get_children():
            self.medicine_tree.delete(item)
        
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                if search_term:
                    query = """
                    SELECT medicine_id, medicine_name, brand_name, chemical_component, supplier_id, stock_quantity, expiry_date, price, cost_price FROM medicines 
                    WHERE LOWER(medicine_name) LIKE %s 
                    OR LOWER(brand_name) LIKE %s 
                    OR LOWER(chemical_component) LIKE %s
                    ORDER BY medicine_id
                    """
                    search_pattern = f"%{search_term}%"
                    cursor.execute(query, (search_pattern, search_pattern, search_pattern))
                else:
                    cursor.execute("SELECT medicine_id, medicine_name, brand_name, chemical_component, supplier_id, stock_quantity, expiry_date, price, cost_price FROM medicines ORDER BY medicine_id")
                
                results = cursor.fetchall()
                for row in results:
                    row_list = list(row)
                    if isinstance(row_list[6], (datetime,)): # expiry_date is at index 6
                        row_list[6] = row_list[6].strftime("%Y-%m-%d")
                    self.medicine_tree.insert('', 'end', values=row_list)
                
        except pymysql.MySQLError as e:
            messagebox.showerror("Database Error", f"Search failed: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred during medicine search: {e}")
        finally:
            if conn and conn.open:
                conn.close()# Close connection after use
    
    def search_suppliers(self, event=None):
        """Search suppliers in the treeview"""
        search_term = self.supplier_search_entry.get().lower()
        
        # Clear current selection
        for item in self.supplier_tree.get_children():
            self.supplier_tree.delete(item)
        
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                if search_term:
                    query = """
                    SELECT * FROM suppliers 
                    WHERE LOWER(supplier_name) LIKE %s 
                    OR LOWER(contact_person) LIKE %s 
                    OR LOWER(email) LIKE %s
                    ORDER BY supplier_id
                    """
                    search_pattern = f"%{search_term}%"
                    cursor.execute(query, (search_pattern, search_pattern, search_pattern))
                else:
                    cursor.execute("SELECT * FROM suppliers ORDER BY supplier_id")
                
                results = cursor.fetchall()
                for row in results:
                    row_list = list(row)
                    if row_list[6]:  # created_at field
                        row_list[6] = row_list[6].strftime("%Y-%m-%d %H:%M")
                    self.supplier_tree.insert('', 'end', values=row_list)
                
        except pymysql.MySQLError as e:
            messagebox.showerror("Database Error", f"Search failed: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred during supplier search: {e}")
        finally:
            if conn and conn.open:
                conn.close()# Close connection after use
    
    def refresh_medicines(self):
        """Refresh medicines list"""
        self.search_entry.delete(0, END)
        self.load_medicines()
        messagebox.showinfo("Success", "Medicines list refreshed!")
    
    def refresh_suppliers(self):
        """Refresh suppliers list"""
        self.supplier_search_entry.delete(0, END)
        self.load_suppliers()
        messagebox.showinfo("Success", "Suppliers list refreshed!")
    
    def show_expiring_medicines(self):
        """Show medicines expiring in next 5 months"""
        conn = self.get_db_connection()
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT medicine_id, medicine_name, brand_name, chemical_component, supplier_id, stock_quantity, expiry_date, price, cost_price FROM medicines 
                    WHERE expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 5 MONTH)
                    ORDER BY expiry_date
                """)
                results = cursor.fetchall()
                
                # Clear and populate
                for item in self.medicine_tree.get_children():
                    self.medicine_tree.delete(item)
                
                if results:
                    for row in results:
                        row_list = list(row)
                        if isinstance(row_list[6], (datetime,)): # expiry_date is at index 6
                            row_list[6] = row_list[6].strftime("%Y-%m-%d")
                        self.medicine_tree.insert('', 'end', values=row_list)
                    messagebox.showwarning("Expiring Medicines", f"Found {len(results)} medicines expiring in next 5 months!")
                else:
                    messagebox.showinfo("Good News!", "No medicines are expiring in the next 5 months.")
                
        except pymysql.MySQLError as e:
            messagebox.showerror("Database Error", f"Failed to check expiring medicines: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while checking expiring medicines: {e}")
        finally:
            if conn and conn.open:
                conn.close() # Close connection after use
    
    def is_valid_price(self, price_str):
        """Helper function to validate price input."""
        try:
            float(price_str)
            return True
        except ValueError:
            return False

    def add_medicine_dialog(self):
        """Open add medicine dialog"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add New Medicine")
        dialog.geometry("600x700")
        dialog.configure(fg_color=COLORS['white'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f"600x700+{x}+{y}")
        
        # Header
        header = ctk.CTkLabel(
            dialog,
            text="➕ Add New Medicine",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['primary']
        )
        header.pack(pady=(20, 30))
        
        # Form frame
        form_frame = ctk.CTkScrollableFrame(dialog, width=550, height=500)
        form_frame.pack(padx=20, pady=10, fill=BOTH, expand=True)
        
        # Form fields
        entries = {}
        fields = [
            ("Medicine Name*", "medicine_name"),
            ("Brand Name", "brand_name"),
            ("Chemical Component*", "chemical_component"),
            ("Supplier ID", "supplier_id"),
            ("Stock Quantity*", "stock_quantity"),
            ("Selling Price*", "price"),
            ("Cost Price", "cost_price")
        ]
        
        for label_text, key in fields:
            # Label
            label = ctk.CTkLabel(form_frame, text=label_text, font=ctk.CTkFont(size=14, weight="bold"))
            label.pack(anchor=W, padx=10, pady=(15, 5))
            
            # Entry
            entry = ctk.CTkEntry(form_frame, width=500, height=35, font=ctk.CTkFont(size=12))
            entry.pack(padx=10, pady=(0, 5))
            entries[key] = entry
        
        # Expiry date
        expiry_label = ctk.CTkLabel(form_frame, text="Expiry Date*", font=ctk.CTkFont(size=14, weight="bold"))
        expiry_label.pack(anchor=W, padx=10, pady=(15, 5))
        
        expiry_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        expiry_frame.pack(padx=10, pady=(0, 2))
        
        expiry_date_cal = DateEntry( # Renamed to avoid conflict with function parameter
            expiry_frame, 
            width=30, 
            background=COLORS['primary'],
            foreground='white', 
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            font=('Segoe UI', 12)
        )
        expiry_date_cal.pack(anchor=W)
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        def submit_medicine():

                medicine_name = entries["medicine_name"].get().strip()
                brand_name = entries["brand_name"].get().strip()
                chemical_component = entries["chemical_component"].get().strip()
                supplier_id = entries["supplier_id"].get().strip()
                stock_quantity = entries["stock_quantity"].get().strip()
                price = entries["price"].get().strip()
                cost_price = entries["cost_price"].get().strip()
                expiry_date_val = expiry_date_cal.get_date().strftime("%Y-%m-%d")
                
                # Validations
                if not medicine_name:
                    messagebox.showerror("Error", "Medicine Name is required.")
                    return
                if not chemical_component:
                    messagebox.showerror("Error", "Chemical Component is required.")
                    return
                if not stock_quantity or not stock_quantity.isdigit():
                    messagebox.showerror("Error", "Valid Stock Quantity (integer) is required.")
                    return
                if not price or not self.is_valid_price(price):
                    messagebox.showerror("Error", "Valid Selling Price (numeric) is required.")
                    return
                if cost_price and not self.is_valid_price(cost_price):
                    messagebox.showerror("Error", "Enter valid Cost Price (numeric).")
                    return
                if supplier_id and not supplier_id.isdigit():
                    messagebox.showerror("Error", "Supplier ID must be a number.")
                    return
                
                # Convert values
                price = float(price)
                cost_price = float(cost_price) if cost_price else None
                stock_quantity = int(stock_quantity)
                supplier_id = int(supplier_id) if supplier_id else None
                
                # Insert into database
                conn = self.get_db_connection()
                if not conn:
                    return

                try:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO medicines 
                            (medicine_name, brand_name, chemical_component, supplier_id, stock_quantity, expiry_date, price, cost_price) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (medicine_name, brand_name, chemical_component, supplier_id, stock_quantity, expiry_date_val, price, cost_price))
                        
                        conn.commit()
                        messagebox.showinfo("Success", "Medicine added successfully!")
                        dialog.destroy()
                        self.load_medicines()
                except pymysql.Error as e:
                    messagebox.showerror("Database Error", f"Failed to add medicine: {e}")
                except Exception as e:
                    messagebox.showerror("Error", f"An unexpected error occurred: {e}")
                finally:
                    if conn and conn.open:
                        conn.close()
 
        
        submit_btn = ctk.CTkButton(
            button_frame,
            text="✅ Add Medicine",
            command=submit_medicine,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['success'],
            hover_color=COLORS['success']
        )
        submit_btn.pack(side=LEFT, padx=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=dialog.destroy,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['danger'],
            hover_color=COLORS['danger']
        )
        cancel_btn.pack(side=LEFT, padx=10)
    
    def update_medicine_dialog(self):
        """Open update medicine dialog"""
        selected = self.medicine_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a medicine to update.")
            return
            
        # Get selected medicine data
        values = self.medicine_tree.item(selected[0], 'values')
        medicine_id = values[0]
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Update Medicine")
        dialog.geometry("600x750")
        dialog.configure(fg_color=COLORS['white'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (750 // 2)
        dialog.geometry(f"600x750+{x}+{y}")
        
        # Header
        header = ctk.CTkLabel(
            dialog,
            text=f"✏️ Update Medicine (ID: {medicine_id})",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['primary']
        )
        header.pack(pady=(20, 30))
        
        # Form frame
        form_frame = ctk.CTkScrollableFrame(dialog, width=550, height=550)
        form_frame.pack(padx=20, pady=10, fill=BOTH, expand=True)
        
        # Form fields with pre-filled values
        entries = {}
        fields = [
            ("Medicine Name*", "medicine_name", values[1]),
            ("Brand Name", "brand_name", values[2]),
            ("Chemical Component*", "chemical_component", values[3]),
            ("Supplier ID", "supplier_id", values[4]),
            ("Stock Quantity*", "stock_quantity", values[5]),
            ("Selling Price*", "price", values[7]), # Selling price is at index 7
            ("Cost Price", "cost_price", values[8]) # Cost price is at index 8
        ]
        
        for label_text, key, default_value in fields:
            # Label
            label = ctk.CTkLabel(form_frame, text=label_text, font=ctk.CTkFont(size=14, weight="bold"))
            label.pack(anchor=W, padx=10, pady=(15, 5))
            
            # Entry
            entry = ctk.CTkEntry(form_frame, width=500, height=35, font=ctk.CTkFont(size=12))
            entry.insert(0, str(default_value) if default_value is not None else "")
            entry.pack(padx=10, pady=(0, 5))
            entries[key] = entry
        
        # Expiry date
        expiry_label = ctk.CTkLabel(form_frame, text="Expiry Date*", font=ctk.CTkFont(size=14, weight="bold"))
        expiry_label.pack(anchor=W, padx=10, pady=(15, 5))
        
        expiry_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        expiry_frame.pack(padx=10, pady=(0, 3))
        
        # Pre-fill expiry date
        initial_expiry_date = datetime.strptime(values[6], "%Y-%m-%d").date() if values[6] else datetime.now().date()
        expiry_date_cal = DateEntry(
            expiry_frame, 
            width=30, 
            background=COLORS['primary'],
            foreground='white', 
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            font=('Segoe UI', 12),
            year=initial_expiry_date.year,
            month=initial_expiry_date.month,
            day=initial_expiry_date.day
        )
        expiry_date_cal.pack(anchor=W)
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        def submit_update_medicine():
                # Get values
                medicine_name = entries["medicine_name"].get().strip()
                brand_name = entries["brand_name"].get().strip()
                chemical_component = entries["chemical_component"].get().strip()
                supplier_id = entries["supplier_id"].get().strip()
                stock_quantity = entries["stock_quantity"].get().strip()
                price = entries["price"].get().strip()
                cost_price = entries["cost_price"].get().strip()
                expiry_date_val = expiry_date_cal.get_date().strftime("%Y-%m-%d")
                
                # Validations (similar to add_medicine_dialog)
                if not medicine_name:
                    messagebox.showerror("Error", "Medicine Name is required.")
                    return
                if not chemical_component:
                    messagebox.showerror("Error", "Chemical Component is required.")
                    return
                if not stock_quantity or not stock_quantity.isdigit():
                    messagebox.showerror("Error", "Valid Stock Quantity (integer) is required.")
                    return
                if not price or not self.is_valid_price(price):
                    messagebox.showerror("Error", "Valid Selling Price (numeric) is required.")
                    return
                if cost_price and not self.is_valid_price(cost_price):
                    messagebox.showerror("Error", "Enter valid Cost Price (numeric).")
                    return
                if supplier_id and not supplier_id.isdigit():
                    messagebox.showerror("Error", "Supplier ID must be a number.")
                    return
                
                # Convert values
                price = float(price)
                cost_price = float(cost_price) if cost_price else None
                stock_quantity = int(stock_quantity)
                supplier_id = int(supplier_id) if supplier_id else None
                
                # Update database
                conn = self.get_db_connection()
                if not conn:
                    return

                try:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            UPDATE medicines SET 
                            medicine_name = %s, 
                            brand_name = %s, 
                            chemical_component = %s, 
                            supplier_id = %s, 
                            stock_quantity = %s, 
                            expiry_date = %s, 
                            price = %s,
                            cost_price = %s
                            WHERE medicine_id = %s
                        """, (medicine_name, brand_name, chemical_component, supplier_id, stock_quantity, expiry_date_val, price, cost_price, medicine_id))
                        
                        conn.commit()
                        messagebox.showinfo("Success", "Medicine updated successfully!")
                        dialog.destroy()
                        self.load_medicines()
                except pymysql.Error as e:
                    messagebox.showerror("Database Error", f"Failed to update medicine: {e}")
                except Exception as e:
                    messagebox.showerror("Error", f"An unexpected error occurred: {e}")
                finally:
                    if conn and conn.open:
                        conn.close()
                
        update_btn = ctk.CTkButton(
            button_frame,
            text="✅ Update Medicine",
            command=submit_update_medicine,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary']
        )
        update_btn.pack(side=LEFT, padx=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=dialog.destroy,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['danger'],
            hover_color=COLORS['danger']
        )
        cancel_btn.pack(side=LEFT, padx=10)

    def delete_medicine_dialog(self):
        """Open delete medicine confirmation dialog"""
        selected = self.medicine_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a medicine to delete.")
            return
        
        medicine_id = self.medicine_tree.item(selected[0], 'values')[0]
        medicine_name = self.medicine_tree.item(selected[0], 'values')[1]
        
        confirm = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete medicine: {medicine_name} (ID: {medicine_id})?\nThis action cannot be undone."
        )
        
        if confirm:
            conn = self.get_db_connection()
            if not conn:
                return

            try:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM medicines WHERE medicine_id = %s", (medicine_id,))
                    conn.commit()
                    messagebox.showinfo("Success", f"Medicine '{medicine_name}' deleted successfully!")
                    self.load_medicines()
            except pymysql.Error as e:
                messagebox.showerror("Database Error", f"Failed to delete medicine: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            finally:
                if conn and conn.open:
                    conn.close()

    def add_supplier_dialog(self):
        """Open add supplier dialog"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add New Supplier")
        dialog.geometry("600x650")
        dialog.configure(fg_color=COLORS['white'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (650 // 2)
        dialog.geometry(f"600x650+{x}+{y}")
        
        # Header
        header = ctk.CTkLabel(
            dialog,
            text="➕ Add New Supplier",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['primary']
        )
        header.pack(pady=(20, 30))
        
        # Form frame
        form_frame = ctk.CTkScrollableFrame(dialog, width=550, height=450)
        form_frame.pack(padx=20, pady=10, fill=BOTH, expand=True)
        
        # Form fields
        entries = {}
        fields = [
            ("Supplier Name*", "supplier_name"),
            ("Contact Person", "contact_person"),
            ("Phone Number", "phone_number"),
            ("Email", "email"),
            ("Address", "address")
        ]
        
        for label_text, key in fields:
            label = ctk.CTkLabel(form_frame, text=label_text, font=ctk.CTkFont(size=14, weight="bold"))
            label.pack(anchor=W, padx=10, pady=(15, 5))
            
            if key == "address":
                entry = ctk.CTkTextbox(form_frame, width=500, height=80, font=ctk.CTkFont(size=12))
            else:
                entry = ctk.CTkEntry(form_frame, width=500, height=35, font=ctk.CTkFont(size=12))
            entry.pack(padx=10, pady=(0, 5))
            entries[key] = entry
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        def submit_supplier():

                supplier_name = entries["supplier_name"].get().strip()
                contact_person = entries["contact_person"].get().strip()
                phone_number = entries["phone_number"].get().strip()
                email = entries["email"].get().strip()
                address = entries["address"].get("1.0", "end-1c").strip() # For CTkTextbox
                
                # Validations
                if not supplier_name:
                    messagebox.showerror("Error", "Supplier Name is required.")
                    return
                if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    messagebox.showerror("Error", "Invalid Email format.")
                    return
                if phone_number and not re.match(r"^\+?[0-9\s\-()]{7,20}$", phone_number): # Basic phone regex
                    messagebox.showerror("Error", "Invalid Phone Number format.")
                    return
                
                conn = self.get_db_connection()
                if not conn:
                    return

                try:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO suppliers 
                            (supplier_name, contact_person, phone_number, email, address) 
                            VALUES (%s, %s, %s, %s, %s)
                        """, (supplier_name, contact_person, phone_number, email, address))
                        
                        conn.commit()
                        messagebox.showinfo("Success", "Supplier added successfully!")
                        dialog.destroy()
                        self.load_suppliers()
                except pymysql.Error as e:
                    messagebox.showerror("Database Error", f"Failed to add supplier: {e}")
                except Exception as e:
                    messagebox.showerror("Error", f"An unexpected error occurred: {e}")
                finally:
                    if conn and conn.open:
                        conn.close()
                
               
        
        submit_btn = ctk.CTkButton(
            button_frame,
            text="✅ Add Supplier",
            command=submit_supplier,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['success'],
            hover_color=COLORS['success']
        )
        submit_btn.pack(side=LEFT, padx=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=dialog.destroy,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['danger'],
            hover_color=COLORS['danger']
        )
        cancel_btn.pack(side=LEFT, padx=10)

    def update_supplier_dialog(self):
        """Open update supplier dialog"""
        selected = self.supplier_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a supplier to update.")
            return
            
        values = self.supplier_tree.item(selected[0], 'values')
        supplier_id = values[0]
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Update Supplier")
        dialog.geometry("600x700")
        dialog.configure(fg_color=COLORS['white'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f"600x700+{x}+{y}")
        
        # Header
        header = ctk.CTkLabel(
            dialog,
            text=f"✏️ Update Supplier (ID: {supplier_id})",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['primary']
        )
        header.pack(pady=(20, 30))
        
        # Form frame
        form_frame = ctk.CTkScrollableFrame(dialog, width=550, height=500)
        form_frame.pack(padx=20, pady=10, fill=BOTH, expand=True)
        
        # Form fields with pre-filled values
        entries = {}
        fields = [
            ("Supplier Name*", "supplier_name", values[1]),
            ("Contact Person", "contact_person", values[2]),
            ("Phone Number", "phone_number", values[3]),
            ("Email", "email", values[4]),
            ("Address", "address", values[5])
        ]
        
        for label_text, key, default_value in fields:
            label = ctk.CTkLabel(form_frame, text=label_text, font=ctk.CTkFont(size=14, weight="bold"))
            label.pack(anchor=W, padx=10, pady=(15, 5))
            
            if key == "address":
                entry = ctk.CTkTextbox(form_frame, width=500, height=80, font=ctk.CTkFont(size=12))
                entry.insert("1.0", str(default_value) if default_value is not None else "")
            else:
                entry = ctk.CTkEntry(form_frame, width=500, height=35, font=ctk.CTkFont(size=12))
                entry.insert(0, str(default_value) if default_value is not None else "")
            entry.pack(padx=10, pady=(0, 5))
            entries[key] = entry
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        def submit_update_supplier():
                supplier_name = entries["supplier_name"].get().strip()
                contact_person = entries["contact_person"].get().strip()
                phone_number = entries["phone_number"].get().strip()
                email = entries["email"].get().strip()
                address = entries["address"].get("1.0", "end-1c").strip()
                
                # Validations (similar to add_supplier_dialog)
                if not supplier_name:
                    messagebox.showerror("Error", "Supplier Name is required.")
                    return
                if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    messagebox.showerror("Error", "Invalid Email format.")
                    return
                if phone_number and not re.match(r"^\+?[0-9\s\-()]{7,20}$", phone_number):
                    messagebox.showerror("Error", "Invalid Phone Number format.")
                    return
                
                conn = self.get_db_connection()
                if not conn:
                    return

                try:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            UPDATE suppliers SET 
                            supplier_name = %s, 
                            contact_person = %s, 
                            phone_number = %s, 
                            email = %s, 
                            address = %s
                            WHERE supplier_id = %s
                        """, (supplier_name, contact_person, phone_number, email, address, supplier_id))
                        
                        conn.commit()
                        messagebox.showinfo("Success", "Supplier updated successfully!")
                        dialog.destroy()
                        self.load_suppliers()
                except pymysql.Error as e:
                    messagebox.showerror("Database Error", f"Failed to update supplier: {e}")
                except Exception as e:
                    messagebox.showerror("Error", f"An unexpected error occurred: {e}")
                finally:
                    if conn and conn.open:
                        conn.close()
            
        update_btn = ctk.CTkButton(
            button_frame,
            text="✅ Update Supplier",
            command=submit_update_supplier,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary']
        )
        update_btn.pack(side=LEFT, padx=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=dialog.destroy,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['danger'],
            hover_color=COLORS['danger']
        )
        cancel_btn.pack(side=LEFT, padx=10)

    def delete_supplier_dialog(self):
        """Open delete supplier confirmation dialog"""
        selected = self.supplier_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a supplier to delete.")
            return
        
        supplier_id = self.supplier_tree.item(selected[0], 'values')[0]
        supplier_name = self.supplier_tree.item(selected[0], 'values')[1]
        
        confirm = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete supplier: {supplier_name} (ID: {supplier_id})?\nThis action cannot be undone."
        )
        
        if confirm:
            conn = self.get_db_connection()
            if not conn:
                return

            try:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM suppliers WHERE supplier_id = %s", (supplier_id,))
                    conn.commit()
                    messagebox.showinfo("Success", f"Supplier '{supplier_name}' deleted successfully!")
                    self.load_suppliers()
            except pymysql.IntegrityError as e:
                # This specific error (1451) occurs if there are foreign key constraints preventing deletion
                if e.args[0] == 1451:
                    messagebox.showerror("Deletion Error", 
                                         f"Cannot delete supplier '{supplier_name}' (ID: {supplier_id}).\n"
                                         "There are medicines associated with this supplier.\n"
                                         "Please reassign or delete associated medicines first.")
                else:
                    messagebox.showerror("Database Error", f"Failed to delete supplier: {e}")
            except pymysql.Error as e:
                messagebox.showerror("Database Error", f"Failed to delete supplier: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            finally:
                if conn and conn.open:
                    conn.close()

if __name__ == "__main__":
    app = HealthcareManagementSystem()

