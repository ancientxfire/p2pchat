import json
import socket
import threading

from modules.ipServices import getAllIps, ipBinaryToString

# Function to handle incoming connections from clients
def handle_client(client_socket, client_address):
    global clientsDetails
    print(f"Accepted connection from {client_address}")
    hasSendMessage = False
    # Loop to receive messages from the client
    while True:
        try:
            # Receive data from the client
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Received message from {client_address}: {data.decode()}")
            if hasSendMessage == False:
                hasSendMessage = True
                try:
                    decodedData = data.decode()
                    json_data = json.loads(decodedData)
                    print(json_data)
                    if json_data["type"] != "auth_message":
                        error_message = json.dumps({"type": "rejection_message","payload": {"message": "Invalid Credentials."}})
                        client_socket.send(error_message.encode())
                        raise "Invalid auth_message"
                        
                    if json_data["payload"]["password"]!= "Password":
                        
                        raise "Invalid auth_message"
                    welcome_message = json.dumps({"type": "welcome_message","payload": {"message": f"Succesfully connected to the host."}})
                    
                    clientsDetails[client_address] = {"username":json_data["payload"]["username"]}
                    print(clientsDetails)
                    client_socket.send(welcome_message.encode())
                    
                except Exception as exception:
                    print("Error:",exception)
                    error_message = json.dumps({"type": "rejection_message","payload": {"message": "invalid JSON data."}})
                    client_socket.send(error_message.encode())
                    print(f"Connection from {client_address} will be closed because of invalid JSON data.")
                    break
                    
            # Broadcast the message to all other connected clients
            for client in clients:
                if client != client_socket:
                    client.send(data)
                    
        except Exception as e:
            print(f"Error: {e}")
            break

    # Close the client socket
    client_socket.close()
    clients.remove(client_socket)
    print(f"Connection from {client_address} closed")
    disconnect_message = json.dumps({"type": "rejection_message","payload": {"message": "User disconnected."}})
    
    for client in clients:
        if client != client_socket:
            client.send(disconnect_message.encode())


# Main function to start the server
def main():
    
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a specific address and port
    ipAdresses = getAllIps()
    print(ipAdresses)
    server_socket.bind((ipBinaryToString(ipAdresses[0]), 5555))

    # Listen for incoming connections
    server_socket.listen(5)
    print("Server listening for connections...")

    # List to store connected clients
    global clients
    global clientsDetails
    clients = []
    clientsDetails = {}

    # Main loop to accept incoming connections
    while True:
        # Accept a new connection
        client_socket, client_address = server_socket.accept()

        # Add the new client socket to the list of clients
        clients.append(client_socket)
        

        # Create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()


if __name__ == "__main__":
    main()
