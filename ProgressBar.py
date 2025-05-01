from  tkinter import *
import time
import os
from tkinter.ttk import Progressbar
from PIL import ImageTk, Image

window=Tk()
window.title("Book Lens")
window.config(bg='Skyblue')

rw=630
rh=390
sw=window.winfo_screenwidth()
sh=window.winfo_screenheight()
wpos=(sw/2)-(rw/2)
hpos=(sh/2)-(rh/2)
window.geometry("%dx%d+%d+%d"%(rw,rh,wpos,hpos))
window.maxsize(1000,800)
window.minsize(400,200)

bg=ImageTk.PhotoImage(file="Image\\Untitled-1.jpg")
bgl=Label(window,image=bg)
bgl.place(x=0,y=0)

p=Progressbar(window,orient=HORIZONTAL,length=100,mode='determinate',value=0)
p.place(x=240,y=350)

def display():
    for i in range(1,11):
        window.update_idletasks()
        p['value']+=10
        time.sleep(0.5)
        L['text']=p['value'],'%'
    window.destroy()
    os.system("Login.py")

l1=Label(window,text="Find My Book:",width=0,height=0,font=('Comic Sans Ms',10,"bold"))
l1.config(bg="white",fg="brown")
l1.place(x=271,y=25)

l2=Label(window,text="A Smart Search Tool",width=0,height=0,font=('Comic Sans Ms',10,"bold"))
l2.config(bg="white",fg="brown")
l2.place(x=250,y=45)

L=Label(window,width=0,height=0,font=('Comic Sans Ms',8,"bold"))
L.config(bg="white",fg="black")
L.place(x=350,y=350)

display()

window.mainloop()

