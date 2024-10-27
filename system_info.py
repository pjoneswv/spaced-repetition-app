import sys
import tkinter as tk
import platform
import os

os.environ['TK_SILENCE_DEPRECATION'] = '1'  # Silence the deprecation warning

print(f"Python version: {sys.version}")
print(f"Tkinter version: {tk.TkVersion}")
print(f"Operating System: {platform.system()} {platform.release()}")
print(f"Display info:")
root = tk.Tk()
print(f"  Screen width: {root.winfo_screenwidth()} pixels")
print(f"  Screen height: {root.winfo_screenheight()} pixels")
print(f"  Available screen width: {root.winfo_vrootwidth()} pixels")
print(f"  Available screen height: {root.winfo_vrootheight()} pixels")
print(f"  Color depth: {root.winfo_depth()} bits per pixel")

# Create a visible window
root.geometry("300x200+50+50")
root.title("Test Window")
label = tk.Label(root, text="Can you see this window?")
label.pack()
print("A test window has been created. Can you see it?")
print("If you can see the window, close it to continue.")
root.mainloop()
print("Test window closed.")
