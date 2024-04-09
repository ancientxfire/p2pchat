from queue import Queue
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
class ChatApp:
    def __init__(self, master,username:str,messageQueueRecived:Queue,messageQueueSend:Queue, newMessageRecivedEvent:threading.Event,newMessageToSendEvent:threading.Event):
        self.username = username
        self.messageQueueRecived = messageQueueRecived
        self.messageQueueSend = messageQueueSend
        self.newMessageRecivedEvent = newMessageRecivedEvent
        self.newMessageToSendEvent = newMessageToSendEvent
        
        self.master = master
        self.master.title("Username: "+username)

        # Create text area for displaying messages
        self.message_area = scrolledtext.ScrolledText(master, state='disabled', wrap='word')
        self.message_area.grid(row=0, column=0, padx=5, pady=5, columnspan=2, sticky='nsew')
        self.message_area.config(state='disabled')

        # Create entry field for typing messages
        self.message_entry = tk.Entry(master, width=50)
        self.message_entry.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

        # Create send button
        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=5, pady=5, sticky='e')

    def send_message(self):
        message = self.message_entry.get()
        if message.strip() != "":
            self.appendMessage(f"You: {message}")
            self.messageQueueSend.put({"type":"message","message":message})
            self.newMessageToSendEvent.set()
            self.message_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Please enter a message.")
        
    def appendMessage(self, message):
            self.message_area.config(state='normal')
            self.message_area.insert(tk.END, f"{message}\n")
            self.message_area.see(tk.END)
            
            self.message_area.config(state='disabled')

def on_quit():
    global root, root_destroyed
    root_destroyed = True
    root.destroy()
def on_enter_key(event):
    app.send_message()
def runClientChatGUI(username,server_disconnected:threading.Event,messageQueueRecived:Queue,messageQueueSend:Queue, newMessageRecivedEvent:threading.Event,newMessageToSendEvent:threading.Event):
    global root, root_destroyed, app
    root = tk.Tk()
    
    root_destroyed = False
    app = ChatApp(root,username,messageQueueRecived,messageQueueSend, newMessageRecivedEvent,newMessageToSendEvent)
    app.message_area.insert(tk.END, f"Test"+"\n")
    root.protocol("WM_DELETE_WINDOW", on_quit)
    root.bind(sequence="<Return>", func=on_enter_key)
    
    while server_disconnected.is_set() == False and root_destroyed == False:
        root.update_idletasks()
        root.update()
        
        if newMessageRecivedEvent.is_set():
            while messageQueueRecived.qsize() > 0:
                message = messageQueueRecived.get()
                
                app.appendMessage(f"{message["sender"]}: {message["message"]}")
                root.deiconify()
                root.focus_force()
        newMessageRecivedEvent.clear()
