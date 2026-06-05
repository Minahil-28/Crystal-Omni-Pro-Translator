import tkinter as tk
from tkinter import messagebox
import json
import os
from PIL import Image, ImageTk

class AuthSystem:
    def __init__(self, root, theme, on_success):
        self.root = root
        self.theme = theme
        self.on_success = on_success
        self.db_file = "users.json"
        self._ensure_db()

    def _ensure_db(self):
        if not os.path.exists(self.db_file):
            with open(self.db_file, "w") as f: 
                json.dump({"admin": "1234"}, f)

    def show_start(self):
        """Shows the initial 'Enter System' screen with full background."""
        self._clear()
        
        # Get window dimensions
        self.root.update_idletasks()
        width = self.root.winfo_width() if self.root.winfo_width() > 100 else 1180
        height = self.root.winfo_height() if self.root.winfo_height() > 100 else 900
        
        # Import RoundedFrame from main
        from main import RoundedFrame
        
        # Create full-screen glassy container
        start_frame = RoundedFrame(
            self.root,
            bg_color=self.theme['glass_surface'],
            border_color=self.theme['glass_border'],
            radius=40,
            width=width,
            height=height
        )
        start_frame.place(x=0, y=0, width=width, height=height)
        
        # Create canvas for background and content
        cw, ch = width - 4, height - 4
        start_canvas = tk.Canvas(
            start_frame,
            width=cw,
            height=ch,
            bg=self.theme['glass_surface'],
            highlightthickness=0
        )
        start_canvas.place(relx=0.5, rely=0.5, anchor='center')
        
        # Load background image
        try:
            img_open = Image.open("splash_bg.jpg")  # You can use splash_bg.jpg or create start_bg.jpg
            img_resized = img_open.resize((cw, ch), Image.Resampling.LANCZOS)
            self.start_img_ref = ImageTk.PhotoImage(img_resized)
            start_canvas.create_image(cw/2, ch/2, image=self.start_img_ref, anchor='center')
            print("✓ Start screen background loaded!")
        except Exception as e:
            print(f"Start background not found: {e}")
            # Gradient fallback
            for i in range(5):
                opacity_color = f"#{int(26 + i*5):02x}{int(11 + i*3):02x}{int(46 + i*8):02x}"
                start_canvas.create_rectangle(0, i*ch//5, cw, (i+1)*ch//5, fill=opacity_color, outline="")
        
        # Text with shadows
        cx, cy = cw/2, ch/2
        
        # Title shadow
        start_canvas.create_text(cx+3, cy-100+3, text="CRYSTAL", font=('Inter', 80, 'bold'), fill='#000000')
        start_canvas.create_text(cx, cy-100, text="CRYSTAL", font=('Inter', 80, 'bold'), fill=self.theme['text_main'])
        
        # Subtitle shadow
        start_canvas.create_text(cx+2, cy-20+2, text="OMNI-PRO TRANSLATOR", font=('Inter', 18), fill='#000000')
        start_canvas.create_text(cx, cy-20, text="OMNI-PRO TRANSLATOR", font=('Inter', 18), fill=self.theme['text_accent'])
        
        # Button on canvas
        btn_y = cy + 80
        # Button background (rounded rectangle effect)
        start_canvas.create_rectangle(
            cx-120, btn_y-25, cx+120, btn_y+25,
            fill=self.theme['accent_btn'], outline=self.theme['glass_border'], width=2
        )
        # Button text
        btn_text = start_canvas.create_text(
            cx, btn_y, text="ENTER SYSTEM", font=('Segoe UI', 14, 'bold'), fill='white'
        )
        
        # Make button clickable
        def on_button_click(event):
            self.show_auth_screen("login")
        
        start_canvas.tag_bind(btn_text, "<Button-1>", on_button_click)
        start_canvas.tag_bind(btn_text, "<Enter>", lambda e: start_canvas.config(cursor="hand2"))
        start_canvas.tag_bind(btn_text, "<Leave>", lambda e: start_canvas.config(cursor=""))

    def show_auth_screen(self, mode="login"):
        """Shows login or signup screen with FULL SCREEN background image."""
        self._clear()
        from main import RoundedFrame
        
        # Get full window dimensions
        self.root.update_idletasks()
        win_width = self.root.winfo_width() if self.root.winfo_width() > 100 else 1180
        win_height = self.root.winfo_height() if self.root.winfo_height() > 100 else 900
        
        # Create FULL SCREEN background frame
        bg_frame = RoundedFrame(
            self.root,
            bg_color=self.theme['glass_surface'],
            border_color=self.theme['glass_border'],
            radius=40,
            width=win_width,
            height=win_height
        )
        bg_frame.place(x=0, y=0, width=win_width, height=win_height)
        
        # Canvas for FULL background image
        cw, ch = win_width - 4, win_height - 4
        bg_canvas = tk.Canvas(
            bg_frame,
            width=cw,
            height=ch,
            bg=self.theme['glass_surface'],
            highlightthickness=0
        )
        bg_canvas.place(relx=0.5, rely=0.5, anchor='center')
        
        # Load FULL SCREEN background image
        try:
            img_name = "splash1_bg.jpg" if mode == "login" else "splash1_bg.jpg"
            img_open = Image.open(img_name)
            img_resized = img_open.resize((cw, ch), Image.Resampling.LANCZOS)
            self.auth_img_ref = ImageTk.PhotoImage(img_resized)
            bg_canvas.create_image(cw/2, ch/2, image=self.auth_img_ref, anchor='center')
            print(f"✓ {mode} background loaded!")
        except Exception as e:
            print(f"{mode} background not found: {e}. Using gradient.")
            # Gradient fallback
            for i in range(5):
                opacity_color = f"#{int(26 + i*5):02x}{int(11 + i*3):02x}{int(46 + i*8):02x}"
                bg_canvas.create_rectangle(0, i*ch//5, cw, (i+1)*ch//5, fill=opacity_color, outline="")
        
        # Now create the FORM CARD on top of the background
        card_width, card_height = 500, 600
        card = RoundedFrame(
            self.root, 
            self.theme['glass_surface'], 
            self.theme['glass_border'], 
            radius=35, 
            width=card_width, 
            height=card_height
        )
        card.place(relx=0.5, rely=0.5, anchor='center')
        
        # Inner frame for form elements with semi-transparent background
        inner = tk.Frame(card, bg=self.theme['glass_surface'])
        inner.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.75)
        
        # Form container
        form_frame = tk.Frame(inner, bg=self.theme['glass_surface'])
        form_frame.pack(expand=True, fill='both', pady=20)
        
        title = "LOGIN" if mode == "login" else "SIGN UP"
        tk.Label(
            form_frame, 
            text=title, 
            font=('Inter', 26, 'bold'), 
            bg=self.theme['glass_surface'], 
            fg=self.theme['text_main']
        ).pack(pady=(10, 30))
        
        u_lbl = "USERNAME" if mode == "login" else "CHOOSE USERNAME"
        p_lbl = "PASSWORD" if mode == "login" else "CHOOSE PASSWORD"
        
        self.u_ent = self._styled_ent(form_frame, u_lbl)
        self.p_ent = self._styled_ent(form_frame, p_lbl, True)

        btn_text = "LOG IN" if mode == "login" else "CREATE ACCOUNT"
        btn_cmd = self._verify if mode == "login" else self._save_user
        btn_color = self.theme['accent_btn'] if mode == "login" else "#9a22c5"
        
        tk.Button(
            form_frame, 
            text=btn_text, 
            font=('Segoe UI', 12, 'bold'), 
            bg=btn_color, 
            fg='white', 
            relief='flat', 
            pady=12, 
            command=btn_cmd
        ).pack(fill='x', pady=15)
        
        toggle_text = "NEW USER? SIGN UP" if mode == "login" else "ALREADY REGISTERED? LOGIN"
        toggle_cmd = lambda: self.show_auth_screen("signup") if mode == "login" else self.show_auth_screen("login")
        
        tk.Button(
            form_frame, 
            text=toggle_text, 
            font=('Segoe UI', 9, 'bold'), 
            bg=self.theme['glass_surface'], 
            fg=self.theme['text_accent'], 
            relief='flat', 
            command=toggle_cmd
        ).pack(pady=10)

    def _styled_ent(self, p, label, is_pass=False):
        tk.Label(
            p, 
            text=label, 
            font=('Segoe UI', 9, 'bold'), 
            bg=self.theme['glass_surface'], 
            fg=self.theme['text_accent']
        ).pack(anchor='w', pady=(10, 5))
        
        ent = tk.Entry(
            p, 
            font=('Segoe UI', 12), 
            bg=self.theme['search_bg'], 
            fg='white', 
            borderwidth=0, 
            insertbackground='white', 
            show="*" if is_pass else ""
        )
        ent.pack(fill='x', pady=(0, 10), ipady=10)
        return ent

    def _verify(self):
        with open(self.db_file, "r") as f: 
            users = json.load(f)
        if users.get(self.u_ent.get()) == self.p_ent.get(): 
            self.on_success()
        else: 
            messagebox.showerror("Error", "Invalid credentials")

    def _save_user(self):
        u, p = self.u_ent.get(), self.p_ent.get()
        if not u or not p: 
            return messagebox.showwarning("Warning", "Fields empty")
        with open(self.db_file, "r") as f: 
            data = json.load(f)
        if u in data: 
            return messagebox.showerror("Error", "User exists")
        data[u] = p
        with open(self.db_file, "w") as f: 
            json.dump(data, f)
        
        messagebox.showinfo("Success", "Account created! Welcome.")
        self.on_success()

    def _clear(self):
        for w in self.root.winfo_children(): 
            w.destroy()