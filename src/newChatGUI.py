import customtkinter

class MyFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)




        self.label = customtkinter.CTkLabel(self)
        self.label.grid(row=0, column=0, padx=20)


class MyFrame2(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(2, weight=1,)
        self.grid_columnconfigure(2, weight=1,)
        self.entry = customtkinter.CTkEntry(self, placeholder_text="Message", )
        self.entry.grid(row=0, column=0, sticky="nsew")
        self.button = customtkinter.CTkButton(self, text="CTkButton", command=self.button_event)
        self.button.grid(row=0, column=1)

    def button_event(self):
        print("button pressed")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.grid_rowconfigure(2, weight=1,)
        self.grid_columnconfigure(2, weight=1,)
        self.my_frame = MyFrame(master=self, width=700, height=500)
        self.my_frame.grid(row=0, column=0, padx=20, pady=20)
        self.my_frame2 = MyFrame2(master=self)
        self.my_frame2.grid(row=1, column=0, padx=20, pady=20, sticky="NSEW")

app = App()
app.mainloop()

app = App()
app.mainloop()