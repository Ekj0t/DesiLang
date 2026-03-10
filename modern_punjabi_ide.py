import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, font
import re
import core_punjabi  # Ensure core_punjabi.py is in the folder

# --- Configuration: One Dark Pro Theme ---
COLORS = {
    "bg": "#282C34",          # Editor Background
    "sidebar": "#21252B",     # Sidebar Background
    "fg": "#ABB2BF",          # Text Color
    "keyword": "#C678DD",     # Purple (je, nahi_ta)
    "function": "#61AFEF",    # Blue (likho)
    "string": "#98C379",      # Green (Strings)
    "number": "#D19A66",      # Orange (Numbers)
    "comment": "#5C6370",     # Grey (Comments)
    "accent": "#528BFF",      # Button Blue
    "folder": "#E5C07B",      # Gold for Open Folder
    "terminal_bg": "#1E1E1E"  # Terminal Background
}

class ModernIDE(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("DesiCode Studio ⚡")
        self.geometry("1100x750")
        ctk.set_appearance_mode("Dark")
        
        # --- ROOT GRID LAYOUT ---
        # Row 0: Top Section (Sidebar + Editor) - Expands
        # Row 1: Bottom Section (Terminal) - Fixed Height
        self.grid_rowconfigure(0, weight=1) 
        self.grid_rowconfigure(1, weight=0) 
        self.grid_columnconfigure(0, weight=1) 

        # =================================================
        # SECTION 1: TOP CONTAINER (Holds Sidebar & Editor)
        # =================================================
        self.top_container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.top_container.grid(row=0, column=0, sticky="nsew")
        
        # Grid inside Top Container
        self.top_container.grid_columnconfigure(0, weight=0) # Sidebar (Fixed)
        self.top_container.grid_columnconfigure(1, weight=1) # Editor (Expands)
        self.top_container.grid_rowconfigure(0, weight=1)

        # 1A. SIDEBAR (Left)
        self.sidebar = ctk.CTkFrame(self.top_container, width=70, corner_radius=0, fg_color=COLORS["sidebar"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False) # Force fixed width
        
        self.create_sidebar_buttons()

        # 1B. EDITOR AREA (Right)
        self.editor_frame = ctk.CTkFrame(self.top_container, corner_radius=0, fg_color=COLORS["bg"])
        self.editor_frame.grid(row=0, column=1, sticky="nsew")

        # Line Numbers (Gutter)
        self.line_numbers = tk.Text(self.editor_frame, width=4, padx=5, pady=5, 
                                   bg=COLORS["sidebar"], fg=COLORS["comment"], 
                                   bd=0, font=("Consolas", 14), state="disabled")
        self.line_numbers.pack(side="left", fill="y")

        # Main Text Editor
        self.code_font = font.Font(family="Consolas", size=14)
        self.editor = tk.Text(self.editor_frame, wrap="none", bg=COLORS["bg"], 
                             fg=COLORS["fg"], insertbackground="white", 
                             bd=0, font=self.code_font, undo=True)
        self.editor.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        self.scrollbar = ctk.CTkScrollbar(self.editor_frame, command=self.editor.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.editor.config(yscrollcommand=self.on_scroll)


        # =================================================
        # SECTION 2: TERMINAL (Full Bottom Width)
        # =================================================
        self.terminal_frame = ctk.CTkFrame(self, height=200, corner_radius=0, fg_color=COLORS["terminal_bg"])
        self.terminal_frame.grid(row=1, column=0, sticky="ew") # Spans entire window width
        self.terminal_frame.pack_propagate(False) # Enforce height

        # Terminal Label Bar
        lbl_bar = ctk.CTkFrame(self.terminal_frame, height=25, fg_color="#181818", corner_radius=0)
        lbl_bar.pack(fill="x", side="top")
        
        lbl = ctk.CTkLabel(lbl_bar, text="  TERMINAL >_", font=("Consolas", 11, "bold"), text_color="#888")
        lbl.pack(anchor="w")

        # Terminal Textbox
        self.terminal = ctk.CTkTextbox(self.terminal_frame, font=("Consolas", 12), 
                                      fg_color=COLORS["terminal_bg"], text_color=COLORS["string"],
                                      activate_scrollbars=True)
        self.terminal.pack(fill="both", expand=True, padx=5, pady=5)
        self.terminal.configure(state="disabled")

        # --- BINDINGS & SETUP ---
        self.editor.bind("<KeyRelease>", self.on_key_release)
        self.editor.bind("<Control-MouseWheel>", self.zoom)
        self.setup_tags()

    def create_sidebar_buttons(self):
        # Run Button
        self.btn_run = ctk.CTkButton(self.sidebar, text="▶", width=40, height=40,
                                    fg_color=COLORS["string"], hover_color="green",
                                    font=("Arial", 24), command=self.run_code)
        self.btn_run.pack(pady=(20, 15), padx=10)
        
        # Open Button (Replaces Clear)
        self.btn_open = ctk.CTkButton(self.sidebar, text="📂", width=40, height=40,
                                     fg_color=COLORS["folder"], hover_color="#D19A66",
                                     font=("Arial", 20), command=self.open_file)
        self.btn_open.pack(pady=10, padx=10)

        # Save Button
        self.btn_save = ctk.CTkButton(self.sidebar, text="💾", width=40, height=40,
                                     fg_color=COLORS["accent"], hover_color="blue",
                                     font=("Arial", 20), command=self.save_file)
        self.btn_save.pack(pady=10, padx=10)

    # --- LOGIC FUNCTIONS ---
    def setup_tags(self):
        self.editor.tag_config("keyword", foreground=COLORS["keyword"])
        self.editor.tag_config("function", foreground=COLORS["function"])
        self.editor.tag_config("string", foreground=COLORS["string"])
        self.editor.tag_config("number", foreground=COLORS["number"])
        self.editor.tag_config("comment", foreground=COLORS["comment"])

    def highlight_syntax(self):
        # Clear tags
        for tag in ["keyword", "function", "string", "number", "comment"]:
            self.editor.tag_remove(tag, "1.0", tk.END)

        # Keywords
        keywords = ['je', 'nahi_ta', 'jad_tak', 'waaste', 'wich', 'roko', 
                    'challo', 'wapas', 'jamat', 'kamm', 'koshish', 'fadd_lo', 
                    'sahi', 'galat', 'kuch_ni']
        for w in keywords: self.apply_regex_color(rf"\b{w}\b", "keyword")

        # Functions
        funcs = ['likho', 'dasso', 'ginti']
        for w in funcs: self.apply_regex_color(rf"\b{w}\b", "function")

        # Regex patterns
        self.apply_regex_color(r"(\".*?\"|\'.*?\')", "string")
        self.apply_regex_color(r"\b\d+\b", "number")
        self.apply_regex_color(r"#.*", "comment")

    def apply_regex_color(self, pattern, tag):
        text = self.editor.get("1.0", tk.END)
        for match in re.finditer(pattern, text):
            self.editor.tag_add(tag, f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

    def on_key_release(self, event=None):
        self.highlight_syntax()
        self.update_line_numbers()

    def on_scroll(self, *args):
        self.scrollbar.set(*args)
        self.line_numbers.yview_moveto(args[0])

    def update_line_numbers(self):
        line_count = self.editor.get("1.0", tk.END).count('\n')
        line_numbers_string = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", line_numbers_string)
        self.line_numbers.config(state="disabled")

    def run_code(self):
        code = self.editor.get("1.0", tk.END)
        self.terminal.configure(state="normal")
        self.terminal.delete("1.0", tk.END)
        try:
            result = core_punjabi.execute_punjabi(code)
            self.terminal.insert(tk.END, result)
        except Exception as e:
            self.terminal.insert(tk.END, f"Error: {e}")
        self.terminal.configure(state="disabled")

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Punjabi Files", "*.pb"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                code = file.read()
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", code)
                self.update_line_numbers()
                self.highlight_syntax()

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pb", filetypes=[("Punjabi Files", "*.pb")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.editor.get("1.0", tk.END))

    def zoom(self, event):
        return "break"

if __name__ == "__main__":
    app = ModernIDE()
    app.mainloop()