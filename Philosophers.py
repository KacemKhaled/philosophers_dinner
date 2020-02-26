#Interface solving the Philosophers Dinner Problem, Created by Kacem on 06/11/2017, Last Edit 11/11/2017
#Interface libraries
from tkinter import Tk, StringVar, Menu, GROOVE, Text,  PhotoImage, Canvas
from tkinter.ttk import Style, Button, Frame, Label, Entry
import tkinter.ttk as ttk
import tkinter.messagebox
from PIL import Image, ImageTk
from math import sin, cos, pi

#Philosophers
import sys
import threading
import time

#Interface Configuration
root=Tk()
root.title("Dining philosophers problem")
root.geometry("1000x680")
root.configure(background="#667882")
root.resizable(False, False)

styl = Style()
styl.theme_use('clam')

Frame1 = Frame(root)
Frame1.place(relx=0.02, rely=0.03, relheight=0.08, relwidth=0.48)
Frame1.configure(borderwidth="5")
Frame1.configure(relief=GROOVE)
#Frame1.configure(width=485)

Frame2 = Frame(root)
Frame2.place(relx=0.02, rely=0.12, relheight=0.85, relwidth=0.95)
Frame2.configure(relief=GROOVE)
Frame2.configure(borderwidth="5")
#Frame2.configure(width=485)

Frame3 = Frame(root)
Frame3.place(relx=0.505, rely=0.03, relheight=0.08, relwidth=0.465)
Frame3.configure(borderwidth="5")
Frame3.configure(relief=GROOVE)
#Frame3.configure(width=485)

def about():  #Menu
    tkinter.messagebox.showinfo("Source Code","\n\nVisit : \n github.com/KacemKhaled/Philosophers-Dining ")
mainMenu=Menu(root)
root.configure(menu=mainMenu)
subMenu=Menu(mainMenu)
mainMenu.add_cascade(label="Help",menu=subMenu)
subMenu.add_command(label="About",command=about)



canvas=Canvas(Frame2,width=800,height=800) #Drawing zone
canvas.pack()
canvas.configure(background="white")
canvas.configure(borderwidth="5")
canvas.configure(width=816)

imgSpag = ImageTk.PhotoImage(Image.open("images/spaghetti.jpg"))
imgFork = ImageTk.PhotoImage(Image.open("images/fork.png"))
imgPhilo = ImageTk.PhotoImage(Image.open("images/philo.png"))



label=Label(Frame1,text="Please select the number of philosophers:")
label.grid(row=1,column=2)


class Spinbox(ttk.Entry):
    def __init__(self, master, **kw):
        ttk.Widget.__init__(self, master, 'ttk::spinbox', kw)



philoVar=StringVar()
philoVar.set(5)
spin=Spinbox(Frame1,from_=2, to=100)
spin.configure(textvariable=philoVar)
spin.grid(row=1,column=3)
spin.configure(takefocus="")

eVar=StringVar()
eVar.set(0.4)
spin2=Spinbox(Frame1, from_=0.1, to=5.1)
spin2.configure(textvariable=eVar)
spin2.configure(increment=0.1)
spin2.grid(row=2,column=3)
spin2.configure(takefocus="")
label2=Label(Frame1,text="Please choose the Time Constraint (seconds):")
label2.grid(row=2,column=2)

def begin():
    print("Number of philosophers chosen : "+spin.get())
    main()


def before():
    if int(spin.get()) < 2:
        tkinter.messagebox.showinfo("Error","Please select a number of philosophers equal or greater than 2!")
    else :
        answer=tkinter.messagebox.askquestion("Colors","\n\nWhite Philosopher: He is thinking"
                                                       "\nRed Philosopher: He is eating"
                                                       "\nYellow Philosopher: He is hungry"
                                                       "\nGreen Philosopher: He has finished thinking and eating"
                                                       "\n\nBlue Fork: It is taken by a Philosopher"
                                                        "\nWhite Fork: It is free"
                                                        "\n\nPS: You can change the Time Constraint whenever you want !"
                                                       "\nAre you ready ?")
        if answer=="yes":
            begin()
        if answer=="no":
            before()


btn=Button(Frame3,text="Begin the Dinner")
btn.configure(command=before)
btn.place(relx=0.25,rely=0.08,width=200,height=40)



#--begin-philo------

class Semaphore(object):

    def __init__(self, initial):
        self.lock = threading.Condition(threading.Lock())
        self.value = initial

    def up(self):
        with self.lock:
            self.value += 1
            self.lock.notify()

    def down(self):
        with self.lock:
            while self.value == 0:
                self.lock.wait()
            self.value -= 1

class Fork(object):
    posx = 0    #x coordinates of the Fork
    posy = 0    #y coordinates of the Fork
    diff = 0    #shift position compared to Plates position
    ap = 99

    def __init__(self, number):
        self.number = number           # chop stick ID
        self.user = -1                 # keep track of philosopher using it
        self.lock = threading.Condition(threading.Lock())
        self.taken = False

        self.diff = -2 * pi / (int(spin.get()) * 2)

        self.posx = 150 * sin(2 * number * pi / int(spin.get()) + self.diff)
        self.posy = 150 * cos(2 * number * pi / int(spin.get()) + self.diff)
        self.imF = Label(canvas, image=imgFork, borderwidth=0, style='f.TLabel',background="white") #config image Fork
        self.imF.place(relx=0.5, rely=0.5, x=(-13 - self.posx) * 1, y=(-13 - self.posy) * 1) #draw image Fork

    def take(self, user):         # used for synchronization
        with self.lock:
            while self.taken == True:
                self.lock.wait()
            self.user = user
            self.taken = True
            self.imF.configure(background='blue')
            sys.stdout.write("Philosopher[%s] took Fork[%s]\n" % (user, self.number))
            self.lock.notifyAll()

    def drop(self, user):         # used for synchronization
        with self.lock:
            while self.taken == False:
                self.lock.wait()
            self.user = -1
            self.imF.configure(background='white')
            self.taken = False
            sys.stdout.write("Philosopher[%s] dropped Fork[%s]\n" % (user, self.number))
            self.lock.notifyAll()


class Philosopher (threading.Thread):

    def __init__(self, number, left, right, butler):
        threading.Thread.__init__(self)
        self.number = number            # philosopher number
        self.left = left
        self.right = right
        self.butler = butler

        self.posx = 150 * sin(2 * number * pi / int(spin.get()))    #x coordinates of the Philosopher Image
        self.posy = 150 * cos(2 * number * pi / int(spin.get()))    #y coordinates of the Philosopher Image

        self.imPh = Label(canvas, image=imgPhilo, borderwidth=2, style='s' + str(number) + '.TLabel',background="white") #config Philosopher Image
        self.imPh.place(relx=0.5, rely=0.5, x=(-13 - self.posx)*1.6, y=(-13 - self.posy)*1.6) #draw Philosopher Image

        self.imSp = Label(canvas, image=imgSpag, borderwidth=0) #config Spaghetti Plate Image
        self.imSp.place(relx=0.5, rely=0.5, x=(-13 - self.posx) * 1.1, y=(-13 - self.posy) * 1.1) #draw Spaghetti Plate Image

    def run(self):
        for i in range(20):
            self.butler.down()              # start service by butler
            self.imPh.configure(background="white")
            sys.stdout.write("Philosopher[%s] thinking\n" % self.number)
            time.sleep(float(spin2.get()))  # think
            self.left.take(self.number)     # pickup left Fork
            self.imPh.configure(background="yellow")
            sys.stdout.write("Philosophe[%s] hungry\n" % self.number)
            time.sleep(float(spin2.get()))  # (yield makes deadlock more likely)
            self.right.take(self.number)    # pickup right Fork
            self.imPh.configure(background="red")
            sys.stdout.write("Philosophe[%s] eating\n" % self.number)
            time.sleep(float(spin2.get()))                 # eat
            self.imPh.configure(background="white")
            sys.stdout.write("Philosophe[%s] thinking\n" % self.number)
            self.right.drop(self.number)    # drop right Fork
            self.left.drop(self.number)     # drop left Fork
            self.butler.up()                # end service by butler
            sys.stdout.write("--\n")
        sys.stdout.write("Philosopher[%s] has finished thinking and eating\n" % self.number)
        self.imPh.configure(background="green")


def main():
    # number of Philosophers / Forks
    n = int(spin.get())

    # butler for deadlock avoidance (n-1 available)
    butler = Semaphore(n-1)

    # list of Forks
    c = [Fork(i) for i in range(n)]

    # list of philsophers
    p = [Philosopher(i, c[i], c[(i+1)%n], butler) for i in range(n)]

    for i in range(n):
        p[i].start()

root.mainloop()