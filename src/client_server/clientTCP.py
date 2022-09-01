from http import client, server
from pickletools import read_int4
import socket, signal, sys, platform, psutil, base64, json
from Crypto.Cipher import AES
from src.client_server.common import * # import all functions in the common area

def signal_handler(sig, frame):
    print('\nDone!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to exit...')

    # Queue of type FILO (First in Last Out)
def queue_Server_data(data, *kwargs): # Receive data from server
    global server_queue
    server_queue.append(data) # Add the data to the most recent

    # Get the oldest queue data 
def get_queue_Server_data(*kwargs):
    try:
        global server_queue
        if len(server_queue) == 0: return None # Stack doesn't have any data
        #  print(len(server_queue)) DEBUG
        return server_queue[(len(server_queue)-1)] # return the oldest value
    except: return None # If the stack hasn't been inicialized

    # Remove the oldest value of the Queue and returns it
    # In other implementation, just this function could be use
    # and no other need for the get_queue_client_data 
def remove_last_queue_Server_data(*kwargs):
    try:
        global server_queue
        if len(server_queue) == 0: return None # Stack doesn't have any data
        return server_queue.pop(len(server_queue)-1) # return and delete the oldest value
    except: return None # If the stack hasn't been inicialized

    # Queue of type FILO (First in Last Out)
def queue_Client_data(data, *kwargs): # Send data to server
    global client_queue
    client_queue.append(data) # Add the data to the most recent

    # Get the oldest queue data 
def get_queue_Client_data(*kwargs):
    try:
        global client_queue
        if len(client_queue) == 0: return None # Stack doesn't have any data
        #  print(len(server_queue)) DEBUG
        return client_queue[(len(client_queue)-1)] # return the oldest value
    except: return None # If the stack hasn't been inicialized

    # Remove the oldest value of the Queue and returns it
    # In other implementation, just this function could be use
    # and no other need for the get_queue_client_data 
def remove_last_queue_Client_data(*kwargs):
    try:
        global client_queue
        if len(client_queue) == 0: return None # Stack doesn't have any data
        return client_queue.pop(len(client_queue)-1) # return and delete the oldest value
    except: return None # If the stack hasn't been inicialized

#################################### CLIENT FUNCTIONS ###############################################

    # Principal function to operate the client 
def pair_wServer(client_sock):
    global server_attributes

    while True:
        try: 
            server_msg = client_sock.recv(2048) # wait for response (buffer should be enough for the most amount of data)
                                                # alternatively in other implementations this buffer should be defined by the
                                                # header of the message itself, as that would be more secured
            if not server_msg: # If the connection with server is terminated
                print("END: Connection with server terminated")
                client_sock.close()
            else:
                server_msg = unbyting_dict(server_msg) # convert the receive information to a usable dictionary
                # print('Server message: {}'.format(server_msg)) DEBUG

                client_response = new_message(server_msg)
                # print(f'Response: {client_response}') DEBUG

                if not client_response[0]: # If error occurred
                    print(client_response[1])
                    client_sock.close()
                    return [False, client_response[1]]
                elif client_response[1] == 'no_response': # Information not to be sent to server
                    pass
                elif client_response[1] == 'start_game':
                    return [True, 'success']
                else: 
                    client_sock.send(byting_dict(client_response[1]))
        except Exception as e:
            print('ERROR: Please try again!')
            client_sock.close()
            return [False, f'Error: {e}']

    # Function to process the received information from the server
def new_message(server_msg):
    global server_attributes
    if decrypt_values(server_msg['op'], server_attributes['enc']) == 'auth':
        msg = authenticate_client(server_msg)
    elif decrypt_values(server_msg['op'], server_attributes['enc']) == 'info' or server_msg['op'] == 'info': # When providing the algorithm only use encryption on the cipher
        msg = inform_client(server_msg)
    elif decrypt_values(server_msg['op'], server_attributes['enc']) == 'status' and decrypt_values(server_msg['status'], server_attributes['enc']) == 'logged_in':
        return [True, 'start_game']
    else: 
        msg = [False, 'ERROR: Received unknown command']
    return msg

    # Function to authenticate the client with the server
def authenticate_client(server_msg):
    global server_attributes
    try:
        # Example server_msg = {'op': 'auth', 'type': 'request', 'payload': 'password'}
        if decrypt_values(server_msg['type'], server_attributes['enc']) == 'request' and decrypt_values(server_msg['payload'], server_attributes['enc']) == 'password':
            msg = {'op': encrypt_values('auth', server_attributes['enc']), 'type': encrypt_values('response', server_attributes['enc']), 'payload': encrypt_values(server_attributes['password'], server_attributes['enc'])}
            return [True, msg]
        # Example server_msg = {'op': 'auth', 'type': 'response', 'payload': '...'}
        elif decrypt_values(server_msg['type'], server_attributes['enc']) == 'response':
            if decrypt_values(server_msg['payload'], server_attributes['enc']) == 'success':
                return [True,'no_response']
            else: 
                return [False,'END: Client failed authentication']
        else:
            return [False, 'ERROR: Received unknown command']
    except Exception as e:
        return [False,f'ERROR: {e}']

    # Function to process the information received from the server
def inform_client(server_msg):
    global server_attributes
    try:
        # Example server_msg = {'op': 'info', 'type': 'message', 'messsage': '...'}
        if decrypt_values(server_msg['type'], server_attributes['enc']) == 'message':
            msg = decrypt_values(server_msg['message'], server_attributes['enc']) # Receive the message
            print(f'SERVER MESSAGE: {msg}')
            return [True, 'no_response']
        # Example server_msg = {'op': 'info', 'type': 'encryption', 'cipher': '...'}
        elif decrypt_values(server_msg['type'], server_attributes['enc']) == 'encryption' or server_msg['type'] == 'encryption':
            server_attributes['enc'] = base64.b64decode (server_msg['cipher']) # Received cipherkey
            return[True, 'no_response']
        else:
            return[False, 'ERROR: Received unknown command']
    except Exception as e:
        return [False,f'ERROR: {e}']

def receiveServerGameData(client_socket):
    global server_attributes
    try:
        while True:
            header = client_socket.recv(1) 
            if not header: # if server connection has been terminated
                raise Exception("Server connection terminated")
            else:
                while True:
                    header += client_socket.recv(1)
                    if ':' in header.decode('utf-8'):
                        break
                buffSize = (header.decode('utf-8')).split(':')[0]
                #print(buffSize)
                request = client_socket.recv(int(buffSize))
                print(request)

                msg = unbyting_dict(request) # the response is received in bytes. We need to exchange it to a dictionary form again 
                # print('From  {}:{}, Received: {}'.format(client_socket.getpeername()[0], client_socket.getpeername()[1], msg)) DEBUG
                
                for col in msg:
                    msg[col] = decrypt_values(msg[col], server_attributes['enc'])

                queue_Server_data(msg)
                
    except Exception as e:
        print(f'Error Reception: {e}')
        client_socket.close()
        return [False, f'Error: {e}']

def sendGameDataServer(client_socket):
    global server_attributes
    try:
        while True:
            data = get_queue_Client_data()
            if data != None: # if server connection has been terminated

                for col in data:
                    data[col] = encrypt_values(data[col], server_attributes['enc'])
                
                msg = byting_dict(data)
                headerSize = len(msg)
                header = (str(headerSize) + ':').encode('utf-8')
                client_socket.send(header)
                client_socket.send(msg)
                remove_last_queue_Client_data()
                
    except Exception as e:
        print(f'Error Sending: {e}')
        client_socket.close()
        return [False, f'Error: {e}']


def connect_server(ip, port, enc, password):
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create Socket TCP

    try:
        client_sock.connect((ip, port)) # Atempt server connection
    except:
        print("ERROR: An error occurred trying to connect to the server")
        exit(3)

    global server_attributes # variable to be used in the whole program
    global server_queue # variable to be used from the kivy application to process received data from client
    server_queue = [] # initialize
    global client_queue # variable to be used from the kivy application to send data to client
    client_queue = [] # initialize
    global threads
    threads = list()
    global c_socket
    c_socket = client_sock

    # dictionary containing the room information
    server_attributes = {'ip': ip, 'port': port, 'enc': enc, 'password': password}

    connection_establisher = threading.Thread(target=pair_wServer,args=(client_sock,),daemon=True) # establish connection  to the client
    threads.append(connection_establisher)
    connection_establisher.start()

    if not connection_establisher.is_alive():
        threads.pop()
        
    Receive_Handler = threading.Thread(target=receiveServerGameData,args=(client_sock,),daemon=True) # handle incoming data
    threads.append(Receive_Handler)
    Receive_Handler.start()

    Server_Handler = threading.Thread(target=sendGameDataServer,args=(client_sock,),daemon=True) # handle outgoing data
    threads.append(Server_Handler)
    Server_Handler.start()

def exit_server():
    pass

if __name__ == "__main__":
    connect_server("0.0.0.0", 5005, b'$\xa5\xab\x8b\x1b,\xed\x98m\x8c0gV\xec$\xad', '1234') # Call the main function uppon startup

