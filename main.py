import tkinter as tk
from tkinter import filedialog
from PIL import Image
import Interface.main_menu as main_menu
import Interface.help_menu as help_menu
import estego


def getCoverFile():
    coverFile = filedialog.askopenfile()
    coverFile = str(coverFile).split("'",2)[1]
    coverEntry.delete(0,filedialog.END)
    coverEntry.insert(0,coverFile)
    print("coverfile")

def getMsgFile():
    msgFile = filedialog.askopenfile()
    msgFile = str(msgFile).split("'",2)[1]
    msgEntry.delete(0,filedialog.END)
    msgEntry.insert(0,msgFile)
    print("msgFile")

def encode():
    estego.Main(coverEntry.get(),msgEntry.get(),True)

def decode():
    print("Here I will call the decode function")

if __name__ == "__main__":

    root = tk.Tk()

    root.title("Steganographia")
    root.geometry("300x250+400+120")
    root.minsize(width=400, height=400)
    root.configure(background = 'black')
    root.bind("<Escape>", lambda e: e.widget.quit())

    text = ""
    menubar = tk.Menu(root)

    main_menu.main(root,text,menubar)
    help_menu.main(root,text,menubar)

    coverSelectionLabel = tk.Label(master = root, text= "Please select an image to hide the message: ", bg="black", fg="white")
    coverSelectionLabel.grid(row=0, column=0, columnspan=2, sticky="W")

    coverEntry = tk.Entry(root,textvariable="coverE", width=50)
    coverEntry.grid(row=1, column=0, columnspan=2, padx = 5, sticky="W")

    searchButton1 = tk.Button(master = root, text="Search", command=getCoverFile)
    searchButton1.grid(row=1, column=2)

    msgSelectionLabel = tk.Label(master = root, text = "Please select the image or text file to be encoded", bg ="black", fg ="white")
    msgSelectionLabel.grid(row=2, column=0, columnspan = 2,padx = 5, sticky = "W")

    msgEntry = tk.Entry(root, textvariable="msgE", width=50)
    msgEntry.grid(row=3, column=0, columnspan=2, padx = 5, sticky="W")
    
    searchButton2 = tk.Button(master = root, text="Search", command=getMsgFile)
    searchButton2.grid(row=3, column=2)

    encodeButton = tk.Button(master = root, text = "Encode",command=encode)
    encodeButton.grid(row=4, column=0, pady = 15, padx = 15, sticky="E")

    decodeButton = tk.Button(master = root, text = "Decode", command = decode)
    decodeButton.grid(row=4,column=1, pady = 15, padx = 15, sticky="W")

    root.mainloop()

    