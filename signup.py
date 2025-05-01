from tkinter import *
import tkinter as tk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error
from PIL import ImageTk, Image
import os

window = Tk()
window.title("Sign Up")
window.config(bg="skyblue")

rw, rh = 550, 450 
sw = window.winfo_screenwidth()
sh = window.winfo_screenheight()
wpos = int((sw - rw) / 2)
hpos = int((sh - rh) / 2)
window.geometry(f"{rw}x{rh}+{wpos}+{hpos}")
window.resizable(False, False)

'''
#   Set a background image if available
try:
    bg_image = ImageTk.PhotoImage(file="Image\\Signup.jpg")
    bg_label = Label(window, image=bg_image)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except Exception as e:
    print("Background image not found or error:", e)
'''

# Create a frame for the signup form and center it in the window
form_frame = Frame(window, bg="skyblue")
form_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

title_label = Label(form_frame, text="SIGN UP", font=("Comic Sans MS", 20, "bold"), bg="skyblue")
title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

# First Name Label and Entry
first_label = Label(form_frame, text="First Name:", font=("Comic Sans MS", 14, "bold"), bg="skyblue")
first_label.grid(row=1, column=0, sticky=E, padx=10, pady=10)
first_var = StringVar()
first_entry = Entry(form_frame, textvariable=first_var, font=("Comic Sans MS", 12))
first_entry.grid(row=1, column=1, padx=10, pady=10)

# Last Name Label and Entry
last_label = Label(form_frame, text="Last Name:", font=("Comic Sans MS", 14, "bold"), bg="skyblue")
last_label.grid(row=2, column=0, sticky=E, padx=10, pady=10)
last_var = StringVar()
last_entry = Entry(form_frame, textvariable=last_var, font=("Comic Sans MS", 12))
last_entry.grid(row=2, column=1, padx=10, pady=10)

# Username Label and Entry
username_label = Label(form_frame, text="Username:", font=("Comic Sans MS", 14, "bold"), bg="skyblue")
username_label.grid(row=3, column=0, sticky=E, padx=10, pady=10)
username_var = StringVar()
username_entry = Entry(form_frame, textvariable=username_var, font=("Comic Sans MS", 12))
username_entry.grid(row=3, column=1, padx=10, pady=10)

# Password Label and Entry
password_label = Label(form_frame, text="Password:", font=("Comic Sans MS", 14, "bold"), bg="skyblue")
password_label.grid(row=4, column=0, sticky=E, padx=10, pady=10)
password_var = StringVar()
password_entry = Entry(form_frame, textvariable=password_var, font=("Comic Sans MS", 12), show="*")
password_entry.grid(row=4, column=1, padx=10, pady=10)

def signup():
    first_name = first_var.get()
    last_name = last_var.get()
    username = username_var.get()
    password = password_var.get()

    if not (first_name and last_name and username and password):
        messagebox.showerror("Error", "All fields are required!")
        return

    connection = None 
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            charset="utf8",
            database="booklens",
            
            use_unicode=True
        )

        if connection.is_connected():
            cursor = connection.cursor()
            insert_query = """
            INSERT INTO user_detail (first_name, last_name, username, password)
            VALUES (%s, %s, %s, %s)
            """
            data = (first_name, last_name, username, password)
            cursor.execute(insert_query, data)
            connection.commit()
            messagebox.showinfo("Success", "Signup successful!")

            first_var.set("")
            last_var.set("")
            username_var.set("")
            password_var.set("")
            
    except Error as err:
        messagebox.showerror("Error", f"Error: {err}")
    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()
            window.destroy()
            os.system("python login.py")

def goto_login():
    window.destroy()
    os.system("python login.py")

signup_button = Button(form_frame, text="Sign Up", font=("Comic Sans MS", 12, "bold"), command=signup)
signup_button.grid(row=5, column=0, pady=20, padx=10)

cancel_button = Button(form_frame, text="Cancel", font=("Comic Sans MS", 12, "bold"), command=window.destroy)
cancel_button.grid(row=5, column=1, pady=20, padx=10)

login_frame = Frame(form_frame, bg="skyblue")
login_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0))

account_label = Label(login_frame, text="Already have an account?", font=("Comic Sans MS", 12), bg="skyblue")
account_label.pack(side=LEFT)

login_button = Button(login_frame, text="Login", font=("Comic Sans MS", 12, "underline"), bg="skyblue", 
                      fg="blue", bd=0, cursor="hand2", command=goto_login)
login_button.pack(side=LEFT, padx=(5, 0))

window.mainloop()
