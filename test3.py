import tkinter as tk

root = tk.Tk()
root.geometry("600x400")

# SideBar
sidebar = tk.Frame(root, width=200, bg='gray', height=500, relief='sunken', borderwidth=2)
sidebar.pack(expand=False, fill='y', side='left', anchor='nw')

def show_message(message):
    print(message)

# 在 SideBar 中添加按鈕
button1 = tk.Button(sidebar, text="Button 1", command=)
button1.pack(fill='x')

button2 = tk.Button(sidebar, text="Button 2")
button2.pack(fill='x')

# 主內容區
main_content = tk.Frame(root, bg='white')
main_content.pack(expand=True, fill='both', side='right')

root.mainloop()
