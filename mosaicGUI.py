__author__ = 'MichaelFriend'
from tkinter import Tk, Button, Label, filedialog, StringVar, Entry,IntVar
from photoMosaic import MosaicGenerator as mg
import threading
from tkinter.ttk import Progressbar
'''
todo: disable controls until program is done, validate file save type at front
'''

class MosaicGUI:
    def __init__(self,master):

        self.target_path = StringVar()
        self.gallery_path = StringVar()
        self.tile_size = 0
        self.job_label_text = StringVar()
        self.job_status_text = StringVar()
        self.error_text = StringVar()
        self.save_file_name = StringVar()
        self.launch_thread = None


        self.master = master
        self.master.title("Python Photo Mosaic Generator")
        self.master.geometry('500x300')

        self.target_button = Button(master, text="Choose target", command=self.choose_target)
        self.target_label = Label(master,textvariable=self.target_path)

        self.gallery_button = Button(master, text="Choose gallery", command=self.choose_gallery)
        self.gallery_label = Label(master,textvariable=self.gallery_path)

        valcmd = master.register(self.validate_size)
        self.size_entry = Entry(master, validate="key", validatecommand=(valcmd, '%P'))

        self.save_file_button = Button(master, text="Save file as", command=self.choose_save)
        self.save_file_label = Label(master,textvariable=self.save_file_name)

        self.start_button = Button(master, text="Start", command=self.start_thread)

        self.job_label = Label(master,textvariable=self.job_label_text)

        self.job_status = Label(master,textvariable=self.job_status_text)
        self.progress_bar = Progressbar(master, orient="horizontal",length=200,mode="indeterminate")

        self.error_label = Label(master,textvariable=self.error_text)


        self.target_button.pack()
        self.target_label.pack()
        self.gallery_button.pack()
        self.gallery_label.pack()
        Label(master,text="Input tile size: ").pack()
        self.size_entry.pack()
        self.save_file_button.pack()
        self.save_file_label.pack()
        self.start_button.pack()
        self.job_label.pack()
        self.job_status.pack()
        self.progress_bar.pack()
        self.error_label.pack()

    def choose_save(self):
        self.save_file_name.set(filedialog.asksaveasfilename(filetypes = [("jpeg files","*.jpg"),("gif","*.gif"),("png","*.png")]))

    def choose_target(self):
        self.target_path.set(filedialog.askopenfilename())

    def choose_gallery(self):
        self.gallery_path.set(filedialog.askdirectory())

    def validate_size(self,val):
        if not val:
            self.tile_size = 0
            return True
        try:
            self.tile_size = int(val)
            return True
        except ValueError:
            return False

    def launch_generator(self):
        self.error_text.set(mg(self.target_path.get(),self.gallery_path.get(),self.save_file_name.get(),self.tile_size,self.job_label_text,self.job_status_text).generate_mosaic())

    def start_thread(self):
        self.launch_thread = threading.Thread(target=self.launch_generator)
        self.start_button.config(state='disabled')
        self.progress_bar.start()
        root.after(20,self.check_start_thread)

    def check_start_thread(self):
        if self.launch_thread.is_alive():
            root.after(20,self.check_start_thread)
        else:
            self.start_button.config(state="normal")



root = Tk()
gui = MosaicGUI(root)
root.mainloop()