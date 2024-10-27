import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'

import tkinter as tk
from database_manager import init_db
from gui import QuestionApp
from utils import setup_logging, log_error, log_info

if __name__ == "__main__":
    print("Starting application...")
    init_db()  # This will now recreate the table with the correct structure
    root = tk.Tk()
    app = QuestionApp(root)
    root.mainloop()
