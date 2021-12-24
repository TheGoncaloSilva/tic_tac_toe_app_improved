import socket
import threading
import signal
import sys

# A signal is used to interrupt the execution of a running function
def signal_handler(sig, frame):
    print('\nDone!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to exit...')

# Function to send data to client
# The field data must be of JSON type
#def send_Data(data):


def handle_client_connection(client_socket,address): 
    print('Accepted connection from {}:{}'.format(address[0], address[1]))
    try:
        while True:
            request = client_socket.recv(1024)
            if not request:
                client_socket.close()
            else:
                msg = request.decode()
                print('Received {}'.format(msg))
                msg = ("ECHO: " + msg).encode()
                client_socket.send(msg)
    except (socket.timeout, socket.error):
        print('Client {} error. Done!'.format(address))


# Create the server
def create_server(ip_addr, tcp_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Open a TCP socket
    server.bind((ip_addr, tcp_port))
    server.listen(1)  # max backlog of connections (1 players)

    print('Listening on {}:{}'.format(ip_addr, tcp_port))

    while True:
        client_sock, address = server.accept()
        client_handler = threading.Thread(target=handle_client_connection,args=(client_sock,address),daemon=True)
        client_handler.start()


# Manually create the server
create_server("0.0.0.0", 5005)


