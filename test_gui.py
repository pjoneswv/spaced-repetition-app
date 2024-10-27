import tkinter as tk
import os

os.environ['TK_SILENCE_DEPRECATION'] = '1'  # Silence the deprecation warning

def create_window():
    root = tk.Tk()
    root.geometry("500x400+50+50")  # Set size and position
    root.title("Test Window")
    root.configure(bg='yellow')  # Set background color to yellow
    label = tk.Label(root, text="If you can see this, Tkinter is working!", font=("Arial", 16), bg='yellow')
    label.pack(expand=True)
    print("Test window created. You should see a YELLOW window on your screen.")
    root.lift()  # Try to bring window to front
    root.attributes('-topmost', True)  # Make window stay on top
    root.after_idle(root.attributes, '-topmost', False)  # But then allow it to go behind other windows afterwards
    root.mainloop()

if __name__ == "__main__":
    print("Starting test GUI...")
    create_window()
    print("Test GUI closed.")
