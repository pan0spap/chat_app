import socket
import threading


SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (SERVER, PORT)
DISCONNECT_MESSAGE = 'exit'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = []

def broadcast(msg):
    for client in clients:
        client.send(msg)


def handle_client(communication_socket, addr):
    print(f"New connection {addr} connected.")
    clients.append(communication_socket)
    connected = True
    username = communication_socket.recv(1024).decode('utf-8')
    message = f'Welcome to the chat {username} \n'
    broadcast(message.encode('utf-8'))

    while connected:
        mesg = communication_socket.recv(1024).decode('utf-8')
        if mesg == DISCONNECT_MESSAGE:
            client_disconnect = f"{username} has disconnected!"
            broadcast(client_disconnect.encode('utf-8'))
            clients.remove(communication_socket)
            connected = False
        else:
            broadcast(mesg.encode('utf-8'))    
    communication_socket.close()

def run_server():
    server.listen()
    while True:
        communication_socket, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(communication_socket, addr))
        thread.start()
        print(f"Active connections {threading.active_count() - 1}")


print("Server is running...")
run_server()