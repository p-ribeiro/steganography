import tkinter as tk
from tkinter import font

if __name__ == "__main__":
    
    root = tk.Tk()
    # fontfamilies = font.families()
    # print(fontfamilies)



    root.geometry("500x500")
    root.resizable(0,0)
    root.title("Instagram Image Downloader")

    back = tk.Frame(master = root, bg='black')
    back.propagate(0)
    back.pack(fill=tk.BOTH, expand = 1)

    titleText = tk.Label(master = back, text = "Instagram Image Downloader", bg = 'black', fg = 'white')
    titleText.configure(font=('Copperplate Gothic Light','15','bold'))

    url_label = tk.Label(master = back, text = "Insert the image url: ", bg = 'black', fg = 'white')
    
    url_button = tk.Button(master = back, text = "Get", bg = 'black', fg = 'white')
    
    titleText.grid(row = 0, columnspan = 20, ipadx = 75)
    url_label.grid(row = 1, column = 0, sticky = "W", pady = 20)
    
    
    
    url_entry = tk.Entry(back, width = 50)
    url_entry.grid(row = 1, column = 1, sticky = "W")

    url_button.grid(row = 1, column = 2)


    # close = tk.Button(master = back, text="Quit", command = root.destroy)
    # close.grid(row = 5, column = 3) 
    # close.pack()


    

    root.mainloop()
