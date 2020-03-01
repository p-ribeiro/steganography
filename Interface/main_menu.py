from tkinter import *
from tkinter.messagebox import *

class File():

    def quit(self):
        entry = askyesno(title = "Quit", message = "Are you sure?")
        if entry == True:
            self.root.destroy()


    def __init__(self, text, root):
        self.root = root

def main(root, text, menubar):
    filemenu = Menu(menubar, tearoff=False)
    objFile = File(text,root)
    filemenu.add_command(label="Quit", command=objFile.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu=menubar)


if __name__ == "__main__":
    print("run main.py")