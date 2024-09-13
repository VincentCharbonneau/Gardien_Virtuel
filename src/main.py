#Begin of a simple GUI for the Gardien Virtuel project
#not finished yet


import tkinter
import customtkinter
from streamData import *


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")


app = customtkinter.CTk()
app.geometry("720x480")
app.title("Gardien Virtuel")
app.iconbitmap("ressource/GVicon.ico")


my_label = customtkinter.CTkLabel(app, text="Gardien Virtuel")
my_label.pack(padx=10, pady=10) # pack the label into the window

startButton = customtkinter.CTkButton(app, text="Start", command=lambda: [app.destroy(), main()])
startButton.pack(padx=20, pady=20)

stopButton = customtkinter.CTkButton(app, text="Quit", command=app.quit)
stopButton.pack(padx=10, pady=10)



app.mainloop()