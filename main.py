import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'

import tkinter as tk
from tkinter import filedialog, ttk
from database_manager import init_db, clear_and_reload_database
from pdf_parser import parse_pdf
from gui import QuestionApp
from utils import setup_logging, log_error, log_info

class StartupWindow:
    def __init__(self, master):
        self.master = master
        master.title("Question App Setup")
        
        # Create main container
        self.main_frame = ttk.Frame(master, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Welcome message
        self.welcome_label = ttk.Label(
            self.main_frame,
            text="Welcome to the Question Practice App!\nPlease select your question PDF to begin.",
            justify="center",
            padding="10"
        )
        self.welcome_label.pack(pady=20)
        
        # Upload button
        self.upload_button = ttk.Button(
            self.main_frame,
            text="Upload PDF",
            command=self.upload_pdf
        )
        self.upload_button.pack(pady=10)
        
        # Status label
        self.status_label = ttk.Label(
            self.main_frame,
            text="",
            wraplength=300,
            justify="center"
        )
        self.status_label.pack(pady=10)
        
    def upload_pdf(self):
        """Handle PDF upload and processing"""
        # Open file dialog
        pdf_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if pdf_path:
            self.status_label.config(text="Processing PDF... Please wait.")
            self.upload_button.config(state=tk.DISABLED)
            self.master.update()
            
            # Initialize database
            if init_db():
                # Clear and reload database with new PDF
                if clear_and_reload_database(pdf_path):
                    self.status_label.config(text="PDF processed successfully! Starting quiz...")
                    self.master.after(1000, self.start_quiz)
                else:
                    self.status_label.config(text="Error processing PDF. Please try again.")
                    self.upload_button.config(state=tk.NORMAL)
            else:
                self.status_label.config(text="Database initialization failed. Please try again.")
                self.upload_button.config(state=tk.NORMAL)
    
    def start_quiz(self):
        """Start the main quiz application"""
        # Destroy startup window
        self.master.destroy()
        
        # Create main quiz window
        quiz_root = tk.Tk()
        quiz_app = QuestionApp(quiz_root)
        quiz_root.mainloop()

if __name__ == "__main__":
    # Start with the upload window
    root = tk.Tk()
    app = StartupWindow(root)
    root.mainloop()
