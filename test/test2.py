import os
import tkinter as tk
from tkinter import filedialog

def open_file_dialog():
    filename = filedialog.askopenfilename()
    print(f'Selected file: {filename}')
    # You can add code here to handle the file as needed

def is_excel_file(filename):
    # Check the file extension
    return os.path.splitext(filename)[1] in ['.xls', '.xlsx']


def main():
    root = tk.Tk()
    root.title("File Selector")

    # Set the window size to Width x Height
    root.geometry('400x200')  # Width = 400, Height = 200

    
    open_button = tk.Button(root, text="Open File", command=open_file_dialog)
    open_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    confirm_button = tk.Button(root, text="Confirm", command=root.quit)
    confirm_button.pack(side=tk.RIGHT, padx=5, pady=5)
    
    root.mainloop()

main()  # Run the GUI application

