from tkinter import *
import tkinter as tk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error
import os

window = Tk()
window.title("Login")
window.configure(bg="skyblue")

main_frame = Frame(window, bg="skyblue")
main_frame.pack(padx=20, pady=20)

title_label = Label(main_frame, text="LOGIN", font=("Comic Sans MS", 20, "bold"), bg="skyblue")
title_label.pack(pady=10)

def login():
    """Checks the username and password from the MySQL database."""
    username = username_var.get()
    password = password_var.get()

    if not (username and password):
        messagebox.showerror("Error", "Please enter both username and password!")
        return

    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            charset="utf8",
            database="booklens"
        )
        if connection.is_connected():
            cursor = connection.cursor()
            query = "SELECT * FROM user_detail WHERE username=%s AND password=%s"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            if result:
                messagebox.showinfo("Success", "Login successful!")
                window.destroy()
                os.system(f"python Dashboard.py {username}")
            else:
                messagebox.showerror("Error", "Invalid username or password!")
    except Error as err:
        messagebox.showerror("Error", f"Error: {err}")
    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()
           
def goto_signup():
    window.destroy()
    os.system("python signup.py")

def forget_password():
    messagebox.showinfo("Forgot Password", "Please contact support or implement a recovery option- findmybook18@gmail.com.")

def cancel_app():
    window.destroy()

form_frame = Frame(main_frame, bg="skyblue")
form_frame.pack(pady=10)

username_label = Label(form_frame, text="Username:", font=("Comic Sans MS", 14, "bold"), bg="skyblue")
username_label.grid(row=0, column=0, padx=5, pady=5, sticky=E)

username_var = StringVar()
username_entry = Entry(form_frame, textvariable=username_var, font=("Comic Sans MS", 12))
username_entry.grid(row=0, column=1, padx=5, pady=5)

password_label = Label(form_frame, text="Password:", font=("Comic Sans MS", 14, "bold"), bg="skyblue")
password_label.grid(row=1, column=0, padx=5, pady=5, sticky=E)

password_var = StringVar()
password_entry = Entry(form_frame, textvariable=password_var, font=("Comic Sans MS", 12), show="*")
password_entry.grid(row=1, column=1, padx=5, pady=5)

button_frame = Frame(main_frame, bg="skyblue")
button_frame.pack(pady=10)

login_button = Button(button_frame, text="Login", font=("Comic Sans MS", 12, "bold"), command=login)
login_button.grid(row=0, column=0, padx=10)

cancel_button = Button(button_frame, text="Cancel", font=("Comic Sans MS", 12, "bold"), command=cancel_app)
cancel_button.grid(row=0, column=1, padx=10)

links_frame = Frame(main_frame, bg="skyblue")
links_frame.pack(pady=10)

signup_label = Label(links_frame, text="Don't have an account?", font=("Comic Sans MS", 12), bg="skyblue")
signup_label.pack(side=LEFT)

signup_button = Button(links_frame, text="Signup", font=("Comic Sans MS", 12, "underline"), 
                       bg="skyblue", fg="blue", bd=0, cursor="hand2", command=goto_signup)
signup_button.pack(side=LEFT, padx=(5, 20))

forget_button = Button(links_frame, text="Forgot Password", font=("Comic Sans MS", 12, "underline"),
                       bg="skyblue", fg="blue", bd=0, cursor="hand2", command=forget_password)
forget_button.pack(side=LEFT, padx=5)

window.update_idletasks() 
win_w = window.winfo_reqwidth()
win_h = window.winfo_reqheight()

sw = window.winfo_screenwidth()
sh = window.winfo_screenheight()

x_pos = int((sw - win_w) / 2)
y_pos = int((sh - win_h) / 2)

window.geometry(f"{win_w}x{win_h}+{x_pos}+{y_pos}")
window.resizable(False, False)

window.mainloop()
