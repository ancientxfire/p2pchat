import json
import os
import signal
import socket
 
import threading
from waiting import wait, TimeoutExpired
# Function to handle receiving messages from the server
def receive_messages(client_socket):
    global connection_astablished
    while True:
        try:
            # Receive data from the server
            data = client_socket.recv(1024)
            if not data:
                break
            json_data = json.loads(data.decode())
            if json_data["type"] == "rejection_message":
                print(json_data["payload"]["message"])
                break
            if json_data["type"] == "welcome_message":
                print(json_data["payload"]["message"])
                connection_astablished = True
                
            if json_data["type"] == "chat_message":
                print(f"Received message from server: {data.decode()}")
        except Exception as e:
            print(f"Error: {e}")
            break
    os.kill(os.getpid(), signal.SIGINT)

# Main function to start the client
def main():
    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    server_address = "192.168.1.105"
    server_port = 5555
    client_socket.connect((server_address, server_port))
    hello_message = json.dumps({"type": "auth_message","payload":{"username": "Matze", "password": input("Enter password for the server: ")}})
    client_socket.send(hello_message.encode())
    global connection_astablished
    connection_astablished = False
    
    try:
        # Start a thread to receive messages from the server
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.start()
        # implement waiting for 5 secounds before initiating the message loop to check if the connection is established
        wait(lambda: connection_astablished, 2)
        if connection_astablished == True:
            print("Connection established.")
        else:
            print("Connection not established.")
        
        # Loop to send messages to the server
        while True:
            if receive_thread.is_alive() == False:
                break
            message = input("Enter message to send to the server (or type 'quit' to exit): ")
            if message.lower() == 'quit':
                break
            try:
                # Send the message to the server
                message_json = json.dumps({"type": "message","payload": {"message": message}})
                client_socket.send(message_json.encode())
            except Exception as e:
                print(f"Error: {e}")
                break
    finally:
        # Close the client socket
        client_socket.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()
