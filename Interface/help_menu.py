from tkinter import *
from tkinter.messagebox import *


class Help():

    def aboutMe(self):
        showinfo(title = "About me",message="I'm a program that hides messages inside images \n ************** \n Still in development")

    def __init__(self, text, root):
        self.root = root


def main(root, text, menubar):
    helpmenu = Menu(menubar, tearoff=False)
    objHelp = Help(text,root)
    helpmenu.add_command(label="About me", command = objHelp.aboutMe)
    menubar.add_cascade(label="Help", menu=helpmenu)
    root.config(menu=menubar)


if __name__ == "__main__":
    print("run main.py")