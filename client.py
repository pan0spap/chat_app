from cgitb import text
from tkinter import *
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter.font import BOLD
import tkinter.messagebox
from turtle import width
import sqlite3
import re
import hashlib
import tkinter as tk
from pygame import Cursor
import socket
import threading


def users_database():
    global gender, encPassword
    my_db = sqlite3.connect('users.db')
    c = my_db.cursor()

    c.execute("""CREATE TABLE if not exists users(
    id integer primary key,
    label_username text,
    label_password text,
    label_gender text
    )""")

    
    c.execute("INSERT INTO users(label_username, label_password, label_gender) VALUES (:entry_username, :entry_password, :gender)",
        {
            'entry_username': entry_username.get(),
            'entry_password': str(encPassword),
            'gender' : gender
        })

    my_db.commit()
    my_db.close()  



def messages_database(parame):
    x = str(parame)
    
    db = sqlite3.connect('users.db')
    c = db.cursor()

    c.execute("""CREATE TABLE if not exists messages(
        id integer primary key,
        send_text text,
        users_id integer not null,
        foreign key(users_id) references users(id)
    )""")

    
    c.execute("INSERT INTO messages(send_text, users_id) VALUES (:send_text, :users(id))",
        {
            'send_text': text_area.get('1.0', 'end-1c'),
            'users(id)': x
        })

    db.commit()
    db.close()    



def show_database():
    conn = sqlite3.connect('users.db')

    c = conn.cursor()

    c.execute("SELECT * FROM users")
    items = c.fetchall()
    print(items)

    conn.commit()
    conn.close() 

#symetric encryption
def encrypted_password():
    global encPassword
    passw = entry_password.get()
    passw = passw.encode('utf-8')
    encPassword = hashlib.md5(passw).hexdigest()


def sumbit():
    global v
    if entry_username.get() and entry_password.get():
        try:
            my_database = sqlite3.connect('users.db')
            c = my_database.cursor()

            c.execute('select exists(select label_username from users where label_username = ?)', [entry_username.get()])
        
            if len(entry_password.get())<6:
                tkinter.messagebox.showerror('Error', 'Password should have at least 6 characters!')
            elif c.fetchone()[0]:
                tkinter.messagebox.showerror('Error', 'Username exists please insert other username!')    
            elif  re.search('\s', entry_password.get()):
                tkinter.messagebox.showerror('Error', 'Password should not contain spaces!')   
            elif not re.search('\D', entry_password.get()):
                tkinter.messagebox.showerror('Error', 'Password should contain at least one single character!') 
            elif not re.search('\d', entry_password.get()):
                tkinter.messagebox.showerror('Error', 'Password should contain at least one number!')         
            else:
                encrypted_password()
                users_database()
                show_database()
                tkinter.messagebox.showinfo('Success', 'Registration sucessfully created!')
                display_registration.destroy()

        except sqlite3.OperationalError:
            encrypted_password()
            users_database()
            show_database() 
            tkinter.messagebox.showinfo('Success', 'Registration sucessfully created!')
            display_registration.destroy()     
            
    else:
        tkinter.messagebox.showerror('Error', 'You must set username and password!')


def send_message(text):
    global var
    client.send(text.encode('utf-8'))
    send_text.delete(1.0, 'end')
    send_text.insert(INSERT, var)
    messages_database(iduser)
    show_database()


def receive_message():
    while True:
        try:
            txt = client.recv(1024).decode('utf-8')
            text_area.insert(INSERT, txt)
        except OSError:
            break    



def login():
    global var, iduser
    try:
        my_db = sqlite3.connect('users.db')
        c = my_db.cursor()
        
        c.execute('select exists(select label_username from users where label_username = ?)', [entry_username_login.get()])
        if c.fetchone()[0]: 
            c.execute('select label_password from users where label_username = ?', [entry_username_login.get()])
            password = c.fetchone()

            login_passw = ent_password.get()
            login_passw = login_passw.encode('utf-8')
            login_passw = hashlib.md5(login_passw).hexdigest()
            str = ''.join(password)

            if str == login_passw:
                user = entry_username_login.get()
                client.send(user.encode('utf-8'))
                var = user + ':'
                send_text.insert(INSERT, var)
                entry_username_login.delete(0, END)
                ent_password.config(state=DISABLED)
                entry_username_login.config(state=DISABLED)
                c.execute('select id from users where label_username=?', [user])
                iduser = c.fetchone()
                tkinter.messagebox.showinfo('Success', 'Login success!')
            else:
                tkinter.messagebox.showerror('Error', 'Wrong password!')    
        else:
            tkinter.messagebox.showerror('Error', "Username doesn't exists, you should register first!")        

    except sqlite3.OperationalError:
        tkinter.messagebox.showerror('Error', "Username doesn't exists, you should register first!")

def logout():
    client.send('exit'.encode('utf-8'))
    send_text.delete(1.0, 'end')   
    text_area.delete(1.0, 'end') 
    ent_password.config(state=NORMAL)
    entry_username_login.config(state=NORMAL)
    ent_password.delete(0, END)
    entry_username_login.delete(0, END) 
    
def set_male():
    global gender
    gender = 'Male'


def set_female():
    global gender
    gender = 'Female'
    

def register():
    global entry_username, entry_password, display_registration

    #create a window registration form
    display_registration = Tk()
    display_registration.title("Registration form")
    display_registration.geometry('500x500')

    #create label registration
    label_reg = Label(display_registration, text='Registration form', width=20, font=('bold', 20))
    label_reg.place(x=90, y=53)

    #create label username
    label_username = Label(display_registration, text='Username:')
    label_username.place(x=80, y=130)

    #create entry username
    entry_username = Entry(display_registration)
    entry_username.place(x=180, y=130)

    #create label password
    label_password = Label(display_registration, text='Password:')
    label_password.place(x=80, y=180)

    #create entry password
    entry_password = Entry(display_registration, show='*')
    entry_password.place(x=180, y=180)
    
    #create label gender
    label_gender = Label(display_registration, text='Gender')
    label_gender.place(x=80, y=230)
    
    #radiobuttons for gender
    Radiobutton(display_registration, text="Male", variable=v, value='Male', command=set_male).place(x=170,y=230)
    Radiobutton(display_registration, text='Female', variable=v, value='Female', command=set_female).place(x=250, y=230)

    #create button sumbit
    button_sumbit = Button(display_registration, text='Sumbit', command=sumbit)
    button_sumbit.place(x=180, y=320)

    
####################################################################################################################################################


root = Tk()
root.title("Chat-app")
root.geometry('1000x750')
root.configure(bg='lightblue')
v = StringVar()

#create button register
button_register = Button(root, text="Registration Form", command=register)
button_register.place(x=5, y=10)

#chat label
label_chat = Label(root, text='Chat:', font='Helvetica 15 bold')
label_chat.place(x=720, y=10)

#chat area
text_area = scrolledtext.ScrolledText(root)
text_area.place(x=500, y=40, width=480, height=500 )

#label message
label_message = Label(root, text='Message:')
label_message.place(x=700, y=590)

#send text chat
send_text = scrolledtext.ScrolledText(root)
send_text.place(x=500, y=620, width=480, height=40)

#button send
button_send = Button(root, text='Send', command=lambda: send_message(send_text.get(1.0, END)))
button_send.place(x=700, y=680)

#login
label_login = Label(root, text='Login:', font='Helvetica 15')
label_login.place(x=230, y=60) 

#username login
username_login = Label(root, text='Username:')
username_login.place(x=150, y=120)

#password login
password_login = Label(root, text='Password:')
password_login.place(x=150, y=160)

#entry username login
entry_username_login = Entry(root)
entry_username_login.place(x=230, y=120)

#entry password login
ent_password = Entry(root, show='*')
ent_password.place(x=230, y=160)

#button login
button_login = Button(root, text='Login', command=login)
button_login.place(x=200, y=200)

#button logout
button_logout = Button(root, text='Logout', command=logout)
button_logout.place(x=260, y=200)

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (HOST, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

receive_msg = threading.Thread(target=receive_message)
receive_msg.start()

root.mainloop()