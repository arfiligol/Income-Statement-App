import tkinter as tk

def show_frame(frame):
    frame.tkraise()

root = tk.Tk()
root.geometry('400x400')

frame1 = tk.Frame(root)
frame2 = tk.Frame(root)
for frame in (frame1, frame2):
    frame.grid(row=0, column=0, sticky='news')

# 定義 Frame 1 的內容
label1 = tk.Label(frame1, text="This is Frame 1")
label1.pack()
button1 = tk.Button(frame1, text="Go to Frame 2", command=lambda: show_frame(frame2))
button1.pack()

# 定義 Frame 2 的內容
label2 = tk.Label(frame2, text="This is Frame 2")
label2.pack()
button2 = tk.Button(frame2, text="Go to Frame 1", command=lambda: show_frame(frame1))
button2.pack()

show_frame(frame1)  # Show frame 1 first

root.mainloop()
