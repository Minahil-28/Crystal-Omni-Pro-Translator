import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading, os, pyperclip, datetime, shutil
from ai_service import AITranslator 
from auth import AuthSystem
from PIL import Image, ImageTk
import json
RTL_MARK = "\u202B"
POP_MARK = "\u202C"


# THEME DEFINITIONS
DARK_THEME = {
    'name': 'dark',
    'bg_main': '#090011',
    'glass_surface': '#1A0B2E',
    'glass_border': '#9D4EDD',
    'text_main': '#F8F9FA',
    'text_accent': '#E0AAFF',
    'accent_btn': '#7B2CBF',
    'search_bg': '#240046',
    'btn_secondary': '#5a189a'
}

LIGHT_THEME = {
    'name': 'light',
    'bg_main': '#F3F0F7',
    'glass_surface': '#FFFFFF',
    'glass_border': '#7B2CBF',
    'text_main': '#1A0B2E',
    'text_accent': '#5A189A',
    'accent_btn': '#9D4EDD',
    'search_bg': '#E0AAFF',
    'btn_secondary': '#D8B4FE'
}

class RoundedFrame(tk.Canvas):
    """Circular rounded corners component."""
    def __init__(self, parent, bg_color, border_color, radius=35, **kwargs):
        super().__init__(parent, highlightthickness=0, bg=parent['bg'], **kwargs)
        self.radius = radius
        self.bg_color = bg_color
        self.border_color = border_color
        self.bind("<Configure>", self._draw)

    def _draw(self, event=None):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        r = self.radius
        self.create_oval(0, 0, r*2, r*2, fill=self.bg_color, outline=self.border_color, width=2)
        self.create_oval(w-r*2, 0, w, r*2, fill=self.bg_color, outline=self.border_color, width=2)
        self.create_oval(0, h-r*2, r*2, h, fill=self.bg_color, outline=self.border_color, width=2)
        self.create_oval(w-r*2, h-r*2, w, h, fill=self.bg_color, outline=self.border_color, width=2)
        self.create_rectangle(r, 0, w-r, h, fill=self.bg_color, outline="")
        self.create_rectangle(0, r, w, h-r, fill=self.bg_color, outline="")
        self.create_line(r, 1, w-r, 1, fill=self.border_color, width=2)
        self.create_line(r, h-1, w-r, h-1, fill=self.border_color, width=2)
        self.create_line(1, r, 1, h-r, fill=self.border_color, width=2)
        self.create_line(w-1, r, w-1, h-r, fill=self.border_color, width=2)

class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crystal Omni-Translator Pro")
        self.root.geometry("1180x900") 
        self.current_theme = DARK_THEME
        self.translator = AITranslator()
        self.char_limit = 500
        self.last_audio_path = None
        self.typing_timer = None
        self.last_ai_response = ""
        
        # 1. Initialize the Auth system FIRST
        self.auth = AuthSystem(self.root, self.current_theme, self.setup_ui)
        
        # 2. Show the Splash screen (which eventually calls Auth, then setup_ui)
        self.show_splash()

    def show_splash(self):
        """Displays a premium full-screen glassy splash screen with background image."""
        self.root.configure(bg=DARK_THEME['bg_main'])
        
        # Get actual window dimensions
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # If window size is too small (on first load), use default
        if width < 100:
            width = 1180
        if height < 100:
            height = 900
        
        # 1. Full-screen glassy container with smooth rounded edges
        self.splash_frame = RoundedFrame(
            self.root, 
            bg_color=DARK_THEME['glass_surface'], 
            border_color=DARK_THEME['glass_border'], 
            radius=40, 
            width=width, 
            height=height
        )
        self.splash_frame.place(x=0, y=0, width=width, height=height)

        # 2. Canvas dimensions match the frame
        cw, ch = width - 4, height - 4

        # 3. Create the Canvas first
        splash_canvas = tk.Canvas(
            self.splash_frame, 
            width=cw, 
            height=ch, 
            bg=DARK_THEME['glass_surface'], 
            highlightthickness=0
        )
        splash_canvas.place(relx=0.5, rely=0.5, anchor='center')

        # 4. Load and display background image
        has_image = False
        try:
            # Load the image (PIL is already imported at the top)
            img_open = Image.open("splash5_bg.jpg")
            # Resize image to fill the entire canvas area
            img_resized = img_open.resize((cw, ch), Image.Resampling.LANCZOS)
            self.splash_img_ref = ImageTk.PhotoImage(img_resized)
            has_image = True
            
            # Draw the background image
            splash_canvas.create_image(cw/2, ch/2, image=self.splash_img_ref, anchor='center')
            print("✓ Splash background image loaded successfully!")
        except FileNotFoundError:
            print("✗ splash_bg.jpg not found in current directory")
            print(f"Current directory: {os.getcwd()}")
            # Fallback: Create gradient background
            for i in range(5):
                opacity_color = f"#{int(26 + i*5):02x}{int(11 + i*3):02x}{int(46 + i*8):02x}"
                splash_canvas.create_rectangle(
                    0, i*ch//5, cw, (i+1)*ch//5, 
                    fill=opacity_color, outline=""
                )
        except Exception as e:
            print(f"✗ Error loading image: {e}")
            # Fallback gradient
            for i in range(5):
                opacity_color = f"#{int(26 + i*5):02x}{int(11 + i*3):02x}{int(46 + i*8):02x}"
                splash_canvas.create_rectangle(
                    0, i*ch//5, cw, (i+1)*ch//5, 
                    fill=opacity_color, outline=""
                )

        # 5. DRAW TEXT CENTERED ON TOP (with shadow effect for better visibility)
        cx, cy = cw/2, ch/2
        
        # Text shadow for better readability
        shadow_offset = 2
        
        # Diamond Icon with shadow
        splash_canvas.create_text(
            cx+shadow_offset, cy-100+shadow_offset, text="💎", font=('Inter', 90), 
            fill='#000000'
        )
        splash_canvas.create_text(
            cx, cy-100, text="💎", font=('Inter', 90), 
            fill=DARK_THEME['glass_border']
        )
        
        # Main Title with shadow
        splash_canvas.create_text(
            cx+shadow_offset, cy+shadow_offset, text="CRYSTAL", font=('Inter', 70, 'bold'), 
            fill='#000000'
        )
        splash_canvas.create_text(
            cx, cy, text="CRYSTAL", font=('Inter', 70, 'bold'), 
            fill=DARK_THEME['text_main']
        )
        
        # Subtitle with shadow
        splash_canvas.create_text(
            cx+shadow_offset, cy+80+shadow_offset, text="OMNI-PRO TRANSLATOR", font=('Segoe UI', 16), 
            fill='#000000'
        )
        splash_canvas.create_text(
            cx, cy+80, text="OMNI-PRO TRANSLATOR", font=('Segoe UI', 16), 
            fill=DARK_THEME['text_accent']
        )
        
        # Loading status with shadow
        splash_canvas.create_text(
            cx+shadow_offset, cy+150+shadow_offset, text="Initializing OMNI-PRO System...", font=('Segoe UI', 12), 
            fill='#000000'
        )
        splash_canvas.create_text(
            cx, cy+150, text="Initializing OMNI-PRO System...", font=('Segoe UI', 12), 
            fill='#9D4EDD'
        )

        # Transition to Auth after 3 seconds
        self.root.after(3000, self.start_authentication)

    def start_authentication(self):
        """Initializes the Auth System after splash."""
        self.splash_frame.destroy()
        # Initialize Auth and show the Enter System / Start screen
        self.auth = AuthSystem(self.root, self.current_theme, self.setup_ui)
        self.auth.show_start()

    def toggle_theme(self):
        self.current_theme = LIGHT_THEME if self.current_theme['name'] == 'dark' else DARK_THEME
        self.setup_ui()
    
    def show_context_menu(self, event):
        """Displays the Cut/Copy/Paste menu at the mouse position."""
        self.context_menu.post(event.x_root, event.y_root)

    def custom_paste(self):
        """Pastes text and manually triggers the character counter and AI analysis."""
        try:
            # Get text from clipboard and insert it
            pasted_text = self.root.clipboard_get()
            self.input_text.insert(tk.INSERT, pasted_text)
            
            # Trigger the typing event manually so the 'Chars/Words' count updates immediately
            self.on_typing_event(None)
        except tk.TclError:
            pass # Handle cases where clipboard is empty

    def setup_ui(self):
        for widget in self.root.winfo_children(): widget.destroy()
        theme = self.current_theme
        self.root.configure(bg=theme['bg_main'])

        # --- HEADER ---
        # --- UPDATED HEADER WITH LOGOUT ---
        header = tk.Frame(self.root, bg=theme['bg_main'], pady=20)
        header.pack(fill='x', padx=40)
        
        tk.Label(header, text="CRYSTAL", font=('Inter', 28, 'bold'), 
                 bg=theme['bg_main'], fg=theme['text_main']).pack(side='left')
        tk.Label(header, text="OMNI-PRO", font=('Inter', 12), 
                 bg=theme['bg_main'], fg=theme['text_accent']).pack(side='left', padx=15, pady=(12,0))
        
        # Logout Button
        tk.Button(header, text="LOG OUT 🔓", font=('Segoe UI', 8, 'bold'), 
                  bg='#3C096C', fg='white', relief='flat', padx=15, 
                  command=self.auth.show_start).pack(side='right')
        
        tk.Button(header, text="TOGGLE THEME 🌓", font=('Segoe UI', 8, 'bold'), 
                  bg=theme['btn_secondary'], fg=theme['text_main'], relief='flat', 
                  padx=15, command=self.toggle_theme).pack(side='right', padx=10)
        
        tk.Button(header, text="WIPE ALL", font=('Segoe UI', 8, 'bold'), 
                  bg='#ff1744', fg='white', relief='flat', padx=15, 
                  command=self.wipe_all).pack(side='right')
        # Inside setup_ui() in the header section
        tk.Button(header, text="HISTORY 📜", font=('Segoe UI', 8, 'bold'), 
                 bg=theme['btn_secondary'], fg=theme['text_main'], relief='flat', 
                padx=15, command=self.show_history_window).pack(side='right', padx=10)

        # --- SIDE-BY-SIDE PANELS ---
        content_box = tk.Frame(self.root, bg=theme['bg_main'])
        content_box.pack(fill='both', expand=True, padx=40, pady=5)

        # LEFT SIDE: CHAT
        chat_card = RoundedFrame(content_box, theme['glass_surface'], theme['glass_border'])
        chat_card.place(relx=0, rely=0, relwidth=0.58, relheight=1)
        
        chat_head = tk.Frame(chat_card, bg=theme['glass_surface'], pady=10)
        chat_head.place(relx=0.05, rely=0.02, relwidth=0.9)
        tk.Label(chat_head, text="💬 CHAT LOG", font=('Segoe UI', 8, 'bold'), bg=theme['glass_surface'], fg=theme['text_accent']).pack(side='left')
        
        self.search_chat_var = tk.StringVar()
        tk.Entry(chat_head, textvariable=self.search_chat_var, font=('Segoe UI', 9), bg=theme['search_bg'], fg='white', insertbackground='white', borderwidth=0, width=18).pack(side='left', padx=20)
        self.search_chat_var.trace_add("write", lambda *a: self.filter_chat())

        tk.Button(chat_head, text="📋 COPY", font=('Segoe UI', 7, 'bold'), bg=theme['btn_secondary'], fg='white', relief='flat', command=self.copy_ai_response).pack(side='right', padx=2)
        tk.Button(chat_head, text="💾 SAVE", font=('Segoe UI', 7, 'bold'), bg=theme['btn_secondary'], fg='white', relief='flat', command=self.save_chat).pack(side='right', padx=2)

        self.chat_display = scrolledtext.ScrolledText(chat_card, wrap=tk.WORD, state='disabled', font=('Segoe UI', 10), bg=theme['glass_surface'], fg=theme['text_main'], relief='flat', padx=15, pady=10)
        self.chat_display.place(relx=0.05, rely=0.12, relwidth=0.9, relheight=0.83)

        # RIGHT SIDE: ANALYSIS
        # In main.py inside setup_ui()
        
        hist_card = RoundedFrame(content_box, theme['glass_surface'], theme['glass_border'])
        hist_card.place(relx=0.61, rely=0, relwidth=0.39, relheight=1)

        hist_head = tk.Frame(hist_card, bg=theme['glass_surface'], pady=10)
        hist_head.place(relx=0.05, rely=0.02, relwidth=0.9)
        tk.Label(hist_head, text="🔍 ANALYSIS", font=('Segoe UI', 8, 'bold'), bg=theme['glass_surface'], fg=theme['text_accent']).pack(side='left')
        
        self.search_hist_var = tk.StringVar()
        tk.Entry(hist_head, textvariable=self.search_hist_var, font=('Segoe UI', 9), bg=theme['search_bg'], fg='white', insertbackground='white', borderwidth=0, width=12).pack(side='left', padx=10)
        self.search_hist_var.trace_add("write", lambda *a: self.filter_history())

        tk.Button(hist_head, text="📋 COPY", font=('Segoe UI', 6, 'bold'), bg=theme['btn_secondary'], fg='white', relief='flat', command=self.copy_analysis_text).pack(side='right', padx=2)
        tk.Button(hist_head, text="💾 SAVE", font=('Segoe UI', 6, 'bold'), bg=theme['btn_secondary'], fg='white', relief='flat', command=self.save_history).pack(side='right', padx=2)
        tk.Button(hist_head, text="CLEAR", font=('Segoe UI', 6, 'bold'), bg=theme['btn_secondary'], fg='white', relief='flat', command=self.clear_history).pack(side='right', padx=2)

        self.analysis_box = scrolledtext.ScrolledText(hist_card, font=('Consolas', 9), bg=theme['glass_surface'], fg='#cbd5e1', relief='flat', padx=15, pady=10)
        self.analysis_box.place(relx=0.05, rely=0.12, relwidth=0.9, relheight=0.83)
        self.analysis_box.tag_configure("rtl", justify='right')

        # --- DOCK CONTROLS ---
        dock = tk.Frame(self.root, bg=theme['glass_surface'], pady=20, padx=40)
        dock.pack(side='bottom', fill='x')

        lang_row = tk.Frame(dock, bg=theme['glass_surface'])
        lang_row.pack(fill='x', pady=(0, 10))
        langs = self.translator.get_supported_languages()
        self.src_lang, self.tgt_lang = tk.StringVar(value="Auto-Detect"), tk.StringVar(value="Urdu")
        ttk.Combobox(lang_row, textvariable=self.src_lang, values=langs, state="readonly", width=14).pack(side='left')
        tk.Label(lang_row, text="→", bg=theme['glass_surface'], fg=theme['text_accent'], font=('Arial', 12, 'bold')).pack(side='left', padx=20)
        ttk.Combobox(lang_row, textvariable=self.tgt_lang, values=langs, state="readonly", width=14).pack(side='left')
        
        self.auto_play = tk.BooleanVar(value=True)
        tk.Checkbutton(lang_row, text="AUTO-PLAY", variable=self.auto_play, font=('Segoe UI', 7, 'bold'), bg=theme['glass_surface'], fg='gray', selectcolor=theme['bg_main']).pack(side='right')

        # Input Card (Horizontal tools)
        input_card = RoundedFrame(dock, theme['bg_main'], theme['glass_border'], radius=15, height=80)
        input_card.pack(fill='x', pady=5)
        input_inner = tk.Frame(input_card, bg=theme['bg_main'])
        input_inner.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        tool_dock = tk.Frame(input_inner, bg=theme['bg_main'], padx=5)
        tool_dock.pack(side='left')
        tk.Button(tool_dock, text="🎤", font=('Segoe UI', 14), bg=theme['bg_main'], fg=theme['text_accent'], relief='flat', command=self.use_mic).pack(side='left', padx=5)
        tk.Button(tool_dock, text="📷", font=('Segoe UI', 14), bg=theme['bg_main'], fg=theme['text_accent'], relief='flat', command=self.use_image).pack(side='left', padx=5)
        
        self.input_text = tk.Text(input_inner, font=('Segoe UI', 11), bg=theme['bg_main'], fg=theme['text_main'], insertbackground='white', relief='flat', padx=15, pady=10)
        self.input_text.pack(side='left', fill='both', expand=True)
        self.input_text.bind("<KeyRelease>", self.on_typing_event)
        tk.Button(input_inner, text="✖", font=('Segoe UI', 14), bg=theme['bg_main'], fg='#ff1744', relief='flat', command=self.clear_input_only).pack(side='right', padx=15)

        # --- INSIDE setup_ui() after self.input_text is created ---

        # 1. Create a Right-Click Menu
        self.context_menu = tk.Menu(self.root, tearoff=0, bg=theme['glass_surface'], fg=theme['text_main'])
        self.context_menu.add_command(label="Cut", command=lambda: self.input_text.event_generate("<<Cut>>"))
        self.context_menu.add_command(label="Copy", command=lambda: self.input_text.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="Paste", command=self.custom_paste) # Use a custom paste to trigger word count
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Select All", command=lambda: self.input_text.tag_add("sel", "1.0", "end"))

        # 2. Bind Right-Click (Button-3 for Windows/Linux, Button-2 for macOS)
        self.input_text.bind("<Button-3>", self.show_context_menu)

        # 3. Force Ctrl+V to work specifically if it's currently blocked
        self.input_text.bind("<Control-v>", lambda e: self.custom_paste())

      # --- MODIFIED STATS ROW (VOLUME REMOVED) ---
        stats_row = tk.Frame(dock, bg=theme['glass_surface'])
        stats_row.pack(fill='x', pady=5)
        
        # Only the character and word counter remains here now
        self.counter_lbl = tk.Label(stats_row, text="Chars: 0 | Words: 0", 
                                    font=('Segoe UI', 8), bg=theme['glass_surface'], fg='gray')
        self.counter_lbl.pack(side='right')

        # Action Row
       # --- ACTION ROW (REPLACED VOICE TONE WITH VOLUME) ---
        btn_row = tk.Frame(dock, bg=theme['glass_surface'])
        btn_row.pack(fill='x', pady=(10, 0))

        # Main Process Button
        self.btn_translate = tk.Button(btn_row, text="⚡ PROCESS TRANSLATION", font=('Inter', 11, 'bold'), 
                                      bg=theme['accent_btn'], fg='white', relief='flat', pady=12, command=self.translate)
        self.btn_translate.pack(side='left', fill='x', expand=True)

        # VOLUME SLIDER PLACED HERE (REPLACING VOICE DROPDOWN)
        tk.Label(btn_row, text="VOL", font=('Segoe UI', 7, 'bold'), bg=theme['glass_surface'], fg='gray').pack(side='left', padx=(15, 0))
        self.vol_slider = ttk.Scale(btn_row, from_=0, to=1, orient='horizontal', length=100, command=self.translator.set_volume)
        self.vol_slider.set(0.7)
        self.vol_slider.pack(side='left', padx=10)

        # Audio Action Buttons
        tk.Button(btn_row, text="📥", font=('Segoe UI', 12), bg='#22c55e', fg='white', relief='flat', command=self.download_audio).pack(side='left', padx=3)
        tk.Button(btn_row, text="⏹", font=('Segoe UI', 12), bg='#ef4444', fg='white', relief='flat', command=self.translator.stop_audio).pack(side='left', padx=3)
        tk.Button(btn_row, text="🔊", font=('Segoe UI', 12), bg=theme['glass_border'], fg='white', relief='flat', command=self.play_last_audio).pack(side='left', padx=3)

        self.root.bind("<Return>", lambda e: self.translate())

    # --- LOGIC METHODS (PRESERVED) ---
    def filter_chat(self):
        q = self.search_chat_var.get().lower()
        self.chat_display.tag_remove('m', '1.0', tk.END)
        if q:
            idx = '1.0'
            while 1:
                idx = self.chat_display.search(q, idx, nocase=1, stopindex=tk.END)
                if not idx: break
                lastidx = f"{idx}+{len(q)}c"
                self.chat_display.tag_add('m', idx, lastidx)
                idx = lastidx
            self.chat_display.tag_config('m', background='#7b2cbf', foreground='white')

    def filter_history(self):
        q = self.search_hist_var.get().lower()
        self.analysis_box.tag_remove('m', '1.0', tk.END)
        if q:
            idx = '1.0'
            while 1:
                idx = self.analysis_box.search(q, idx, nocase=1, stopindex=tk.END)
                if not idx: break
                lastidx = f"{idx}+{len(q)}c"
                self.analysis_box.tag_add('m', idx, lastidx)
                idx = lastidx
            self.analysis_box.tag_config('m', background='#7b2cbf', foreground='white')

    def on_typing_event(self, event):
        t = self.input_text.get('1.0', 'end-1c')
        self.counter_lbl.config(text=f"Chars: {len(t)} | Words: {len(t.split())}")
        if self.typing_timer: self.root.after_cancel(self.typing_timer)
        # Increase delay to 3 seconds to save your API quota
        self.typing_timer = self.root.after(3000, self.auto_check_grammar)

    def auto_check_grammar(self):
        t = self.input_text.get('1.0', 'end-1c').strip()
        if 3 <= len(t) <= self.char_limit:
            threading.Thread(target=self.proc_analysis, args=(t,), daemon=True).start()

    



    # def proc_analysis(self, text):
    #     lang = self.tgt_lang.get() 
    #     data = self.translator.get_detailed_analysis(text, lang)
        
    #     def update():
    #         self.analysis_box.config(state='normal')
    #         if "Awaiting" in self.analysis_box.get("1.0", "end"): 
    #             self.analysis_box.delete('1.0', 'end')
            
    #         # Determine if we should use the RTL tag
    #         current_tag = "rtl" if lang == "Urdu" else ""

    #         report_header = f"--- [{datetime.datetime.now().strftime('%H:%M')}] ---\n"
    #         report_body = (
    #             f"🎯 KEY: {data.get('target_word', text).upper()}\n"
    #             f"📖 DEF: {data.get('definition', 'N/A')}\n"
    #             f"🔗 SYN: {', '.join(data.get('synonyms', []))}\n"
    #             f"🚫 ANT: {', '.join(data.get('antonyms', []))}\n\n"
    #         )
            
    #         # Apply the tag only to the body of the text
    #         self.analysis_box.insert('end', report_header)
    #         self.analysis_box.insert('end', report_body, current_tag)
            
    #         self.analysis_box.config(state='disabled')
    #         self.analysis_box.see('end')
        
    #     self.root.after(0, update)

    def proc_analysis(self, text):
        lang = self.tgt_lang.get()
        data = self.translator.get_detailed_analysis(text, lang)

        def update():
            self.analysis_box.config(state='normal')

            if "Awaiting" in self.analysis_box.get("1.0", "end"):
                self.analysis_box.delete('1.0', 'end')

            is_urdu = lang.lower() == "urdu"

            report_header = f"--- [{datetime.datetime.now().strftime('%H:%M')}] ---\n"

            body = (
                f"🎯 KEY: {data.get('target_word', text)}\n"
                f"📖 DEF: {data.get('definition', 'N/A')}\n"
                f"🔗 SYN: {', '.join(data.get('synonyms', []))}\n"
                f"🚫 ANT: {', '.join(data.get('antonyms', []))}\n\n"
            )

            # 🔥 FORCE RTL USING UNICODE MARKERS
            if is_urdu:
                body = RTL_MARK + body + POP_MARK

            self.analysis_box.insert('end', report_header)
            self.analysis_box.insert('end', body, "rtl" if is_urdu else None)

            self.analysis_box.config(state='disabled')
            self.analysis_box.see('end')

        self.root.after(0, update)
    

    # def show_history_window(self):
    #     """Opens a specialized window to view past translation history."""
    #     history_win = tk.Toplevel(self.root)
    #     history_win.title("Translation History")
    #     history_win.geometry("600x500")
    #     history_win.configure(bg=self.current_theme['bg_main'])

    #     hist_box = scrolledtext.ScrolledText(
    #         history_win, 
    #         font=('Segoe UI', 10), 
    #         bg=self.current_theme['glass_surface'], 
    #         fg=self.current_theme['text_main'],
    #         padx=10, pady=10
    #     )
    #     hist_box.pack(fill='both', expand=True, padx=20, pady=20)

    #     # Load from file
    #     if os.path.exists("translation_history.json"):
    #         with open("translation_history.json", "r", encoding="utf-8") as f:
    #             data = json.load(f)
    #             for item in reversed(data): # Show newest first
    #                 entry = f"[{item['timestamp']}]\nSRC: {item['source']}\nTRN: {item['translation']}\n{'-'*40}\n"
    #                 hist_box.insert('end', entry)
    #     else:
    #         hist_box.insert('end', "No history found.")
        
    #     hist_box.config(state='disabled')

    def show_history_window(self):
        """Displays history in a scrollable list with individual delete buttons."""
        history_win = tk.Toplevel(self.root)
        history_win.title("📜 Translation History")
        history_win.geometry("700x700")
        history_win.configure(bg=self.current_theme['bg_main'])

        # 1. Container and Canvas for scrolling
        container = tk.Frame(history_win, bg=self.current_theme['bg_main'])
        container.pack(fill='both', expand=True, padx=20, pady=20)

        canvas = tk.Canvas(container, bg=self.current_theme['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        # This is the frame where cards are placed
        scrollable_frame = tk.Frame(canvas, bg=self.current_theme['bg_main'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 2. Logic to delete an entry
        def delete_entry(index):
            history_file = "translation_history.json"
            if os.path.exists(history_file):
                with open(history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Delete by index
                if 0 <= index < len(data):
                    del data[index]
                
                with open(history_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                refresh_list() # Reload the view

        # 3. Logic to refresh the UI list
        def refresh_list():
            # Clear existing cards
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            history_file = "translation_history.json"
            if os.path.exists(history_file):
                try:
                    with open(history_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    if not data:
                        tk.Label(scrollable_frame, text="History is empty.", 
                                bg=self.current_theme['bg_main'], fg="gray").pack(pady=20)
                        return

                    # Display items (Newest at the top)
                    for i, item in enumerate(reversed(data)):
                        # Calculate original index for deletion
                        actual_index = len(data) - 1 - i
                        
                        card = tk.Frame(scrollable_frame, bg=self.current_theme['glass_surface'], 
                                        highlightbackground=self.current_theme['glass_border'], 
                                        highlightthickness=1, pady=10, padx=10)
                        card.pack(fill='x', pady=5, padx=5)

                        content = f"📅 {item.get('timestamp')}\nIN: {item.get('source')}\nOUT: {item.get('translation')}"
                        tk.Label(card, text=content, justify='left', anchor='w', 
                                bg=self.current_theme['glass_surface'], 
                                fg=self.current_theme['text_main'], font=('Segoe UI', 9)).pack(side='left', fill='x', expand=True)

                        tk.Button(card, text="🗑️", bg="#ef4444", fg="white", relief='flat',
                                command=lambda idx=actual_index: delete_entry(idx)).pack(side='right', padx=10)
                
                except Exception as e:
                    tk.Label(scrollable_frame, text=f"Error: {e}", bg="red", fg="white").pack()
            else:
                tk.Label(scrollable_frame, text="No history file found.", 
                        bg=self.current_theme['bg_main'], fg="gray").pack(pady=20)

        # Start the list
        refresh_list()

    # def translate(self):
    #     """Processes translation and triggers analysis for the ORIGINAL INPUT word."""
    #     text = self.input_text.get('1.0', 'end-1c').strip()
    #     if text:
    #         sl, tl = self.src_lang.get(), self.tgt_lang.get()
            
    #         # 1. Get translation from AI
    #         # 🔥 NEW: Resolve metaphor first
    #         try:
    #             trans = self.translator.ai_translate_with_metaphor(text, sl, tl)
    #         except Exception:
    #             # fallback if API fails
    #             trans = self.translator.translate(text, sl, tl)

    #         self.last_ai_response = trans
            
    #         # 2. Add messages to Chat Log
    #         self.add_message(f"YOU ({sl})", text)
    #         self.add_message(f"AI ({tl})", trans)
            
    #         # 3. Handle Audio
    #         self.last_audio_path = self.translator.generate_audio(trans, tl)
            
    #         # --- THE FIX: PASS 'text' (Your Input) INSTEAD OF 'trans' ---
    #         # This forces the Analysis panel to check YOUR word's grammar
    #         import threading
    #         threading.Thread(target=self.proc_analysis, args=(text,), daemon=True).start()
            
    #         self.clear_input_only()

    def translate(self):
        """Processes translation and triggers audio auto-play if enabled."""
        text = self.input_text.get('1.0', 'end-1c').strip()
        if text:
            sl, tl = self.src_lang.get(), self.tgt_lang.get()
            
            
            try:
                trans = self.translator.ai_translate_with_metaphor(text, sl, tl)
            except Exception:
                trans = self.translator.translate(text, sl, tl)

            analysis_data = self.translator.get_detailed_analysis(text, self.tgt_lang.get())
            self.translator.save_to_history(text, trans, analysis_data)

            self.last_ai_response = trans
            self.add_message(f"YOU ({sl})", text)
            self.add_message(f"AI ({tl})", trans)
            
            # --- AUDIO GENERATION ---
            self.last_audio_path = self.translator.generate_audio(trans, tl)
            
            # 🔥 THE FIX: Check the AUTO-PLAY checkbox value
            if self.auto_play.get() and self.last_audio_path:
                self.play_last_audio()
            
            # --- ANALYSIS TRIGGER ---
            threading.Thread(target=self.proc_analysis, args=(text,), daemon=True).start()
            self.clear_input_only()

    def add_message(self, sender, text):
        self.chat_display.config(state='normal')
        tag = 'u' if "YOU" in sender else 'a'
        self.chat_display.tag_config('u', foreground=self.current_theme['text_accent'], font=('Segoe UI', 9, 'bold'))
        self.chat_display.insert('end', f"\n{sender}:\n", tag); self.chat_display.insert('end', f"{text}\n")
        self.chat_display.config(state='disabled'); self.chat_display.see('end')

    def clear_input_only(self): self.input_text.delete('1.0', 'end'); self.counter_lbl.config(text="Chars: 0 | Words: 0")
    def clear_history(self): self.analysis_box.config(state='normal'); self.analysis_box.delete('1.0', 'end'); self.analysis_box.config(state='disabled')
    def copy_ai_response(self): pyperclip.copy(self.last_ai_response)
    def copy_analysis_text(self): pyperclip.copy(self.analysis_box.get("1.0", "end-1c"))
    def wipe_all(self): self.chat_display.config(state='normal'); self.chat_display.delete('1.0', 'end'); self.chat_display.config(state='disabled'); self.clear_history()
    def download_audio(self):
        if self.last_audio_path:
            p = filedialog.asksaveasfilename(defaultextension=".wav", initialfile=f"Crystal_Audio_{datetime.date.today()}")
            if p: shutil.copy(self.last_audio_path, p)
    def play_last_audio(self):
        if self.last_audio_path: self.translator.play_audio_file(self.last_audio_path)
    def save_chat(self):
        c = self.chat_display.get("1.0", "end-1c").strip()
        if c:
            p = filedialog.asksaveasfilename(defaultextension=".txt")
            if p:
                with open(p, "w", encoding="utf-8") as f: f.write(c)
    def save_history(self):
        c = self.analysis_box.get("1.0", "end-1c").strip()
        if c:
            p = filedialog.asksaveasfilename(defaultextension=".txt")
            if p:
                with open(p, "w", encoding="utf-8") as f: f.write(c)
    def use_mic(self): self.input_text.insert('end', self.translator.speech_to_text())
    def use_image(self): path = filedialog.askopenfilename(); self.input_text.insert('end', self.translator.image_to_text(path))

if __name__ == "__main__":
    root = tk.Tk(); app = TranslatorApp(root); root.mainloop()