from multiprocessing import cpu_count
import socket, threading, signal, sys, base64, os, time, json
from Crypto.Cipher import AES
from requests import request
from src.client_server.common import * # import all functions in the common area

def signal_handler(sig, frame):
    print('\nDone!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to exit...')

    # Queue of type FILO (First in Last Out)
def queue_client_data(data, *kwargs): # Receive data from client
    global server_queue
    server_queue.append(data) # Add the data to the most recent

    # Get the oldest queue data 
def get_queue_client_data(*kwargs):
    try:
        global server_queue
        if len(server_queue) == 0: return None # Stack doesn't have any data
        #  print(len(server_queue)) DEBUG
        return server_queue[(len(server_queue)-1)] # return the oldest value
    except: return None # If the stack hasn't been inicialized

    # Remove the oldest value of the Queue and returns it
    # In other implementation, just this function could be use
    # and no other need for the get_queue_client_data 
def remove_last_queue_client_data(*kwargs):
    try:
        global server_queue
        if len(server_queue) == 0: return None # Stack doesn't have any data
        return server_queue.pop(len(server_queue)-1) # return and delete the oldest value
    except: return None # If the stack hasn't been inicialized

    # Queue of type FILO (First in Last Out)
def queue_server_data(data, *kwargs): # Send data to client
    global client_queue
    client_queue.append(data) # Add the data to the most recent

    # Get the oldest queue data 
def get_queue_server_data(*kwargs):
    try:
        global client_queue
        if len(client_queue) == 0: return None # Stack doesn't have any data
        #  print(len(server_queue)) DEBUG
        return client_queue[(len(client_queue)-1)] # return the oldest value
    except: return None # If the stack hasn't been inicialized

    # Remove the oldest value of the Queue and returns it
    # In other implementation, just this function could be use
    # and no other need for the get_queue_client_data 
def remove_last_queue_server_data(*kwargs):
    try:
        global client_queue
        if len(client_queue) == 0: return None # Stack doesn't have any data
        return client_queue.pop(len(client_queue)-1) # return and delete the oldest value
    except: return None # If the stack hasn't been inicialized

#################################### SERVER FUNCTIONS ###############################################

    # Function that deals with server-client interaction
def handle_client_connection(client_socket,address): 
    global server_attributes # global scope variable
    
    if server_attributes['enc'] != '': # if the server was started using encryption
        # first we inform that the connection will be encripted and give the key
        if not inform_client(client_socket, 'encryption', ''):
            client_socket.close()
            return False
    

    # Authenticate client connection
    if not authenticate_client(client_socket, address): # If client didn't pass authentication close connection
        client_socket.close()
        return False
    
    send_msg = byting_dict({'op': encrypt_values('status', server_attributes['enc']), 'status': encrypt_values("logged_in", server_attributes['enc'])})
    client_socket.send(send_msg)

    # GET CLIENTS NAME
    player_name = "outside"

    queue_client_data({'op' : 'status', 'connection' : 'established', 'ip': address, 'name': player_name}) # inform the server that client connection has been established
    
    #queue_server_data({'op' : 'status', 'connection' : 'established', 'ip': address})
    # Send the client his socket info
    send_msg = byting_dict({'op': encrypt_values('status', server_attributes['enc']), 
                        'connection': encrypt_values("established", server_attributes['enc']), 
                        'ip': encrypt_values(address, server_attributes['enc'])})
    client_socket.send(send_msg)

    global threads
    Receive_Handler = threading.Thread(target=receiveClientGameData,args=(client_socket,address),daemon=True) # handle incoming data
    threads.append(Receive_Handler)
    Receive_Handler.start()

    Server_Handler = threading.Thread(target=sendGameDataClient,args=(client_socket,address),daemon=True) # handle outgoing data
    threads.append(Server_Handler)
    Server_Handler.start()

def receiveClientGameData(client_socket, address):
    global server_attributes
    try:
        while True:
            request = client_socket.recv(4096) 
            if not request: # if server connection has been terminated
                raise Exception("Server connection terminated")
            else:
                msg = unbyting_dict(request) # the response is received in bytes. We need to exchange it to a dictionary form again 
                # print('From  {}:{}, Received: {}'.format(client_socket.getpeername()[0], client_socket.getpeername()[1], msg)) DEBUG

                for col in msg:
                    msg[col] = decrypt_values(msg[col], server_attributes['enc'])

                queue_client_data(msg)
                
    except Exception as e:
        print(f'Error: {e}')
        client_socket.close()
        return [False, f'Error: {e}']

def sendGameDataClient(client_socket, address):
    global server_attributes
    try:
        while True:
            data = get_queue_server_data()
            if data != None: # if server connection has been terminated

                for col in data:
                    data[col] = encrypt_values(data[col], server_attributes['enc'])
                
                msg = byting_dict(data)
                client_socket.send(msg)
                remove_last_queue_server_data()
                
    except Exception as e:
        print(f'Error: {e}')
        client_socket.close()
        return [False, f'Error: {e}']



    # Function to get data from the client
def send_client(client_socket, type):
    global server_attributes
    try:
        if type == 'game_update': # type of data to get from the client
            # Example send_msg = {'op': 'data', 'type': 'request', 'field': 'refresh_rate', 'refresh_rate': '.'}
            send_msg = byting_dict({'op': encrypt_values('game', server_attributes['enc']), 'type': encrypt_values("request", server_attributes['enc']), 'field': encrypt_values('refresh_rate', server_attributes['enc']), 'refresh_rate': encrypt_values('.', server_attributes['enc'])})
            client_socket.send(send_msg)
        elif type == 'sys_info': # type of data to get from the client
            # Example send_msg = {'op': 'data', 'type': 'request', 'field': 'sys_info', 'sys_info': '.'}
            send_msg = byting_dict({'op': encrypt_values('game', server_attributes['enc']), 'type': encrypt_values("request", server_attributes['enc']), 'field': encrypt_values('sys_info', server_attributes['enc']), 'sys_info': encrypt_values('.', server_attributes['enc'])})
            client_socket.send(send_msg)
    
    except Exception as e:
        print(f'ERROR: {e}')
        return [False, 'error']

    # Provide information to the client
    # Doesn't accept a response
    # There is no point to have a return from the client stating that he received the data, since we are using the TCP protocol
def inform_client(client_socket, type, message):
    global server_attributes # global scope variable
    try:
        # Example send_msg = {'op': 'info', 'type': 'message', 'messsage': '...'}
        if type == 'message': # type of information to send to the server
            send_msg = byting_dict({'op': encrypt_values('info', server_attributes['enc']), 'type': encrypt_values('message', server_attributes['enc']), 'messsage': encrypt_values(message, server_attributes['enc'])})
            client_socket.send(send_msg)
            return True
        # Example send_msg = {'op': 'info', 'type': 'encryption', 'cipher': '...'}
        elif type == 'encryption': # type of information to send to the server
            # key already generated in the main.py file
            cipher = str (base64.b64encode (server_attributes['enc']), 'utf8') # encode the key to be sent
            #send_msg = byting_dict({'op': encrypt_values('info'), 'type': encrypt_values('encryption'), 'cipher': cipher})
            send_msg = byting_dict({'op': 'info', 'type': 'encryption', 'cipher': cipher}) # only encrypt the cipher
            client_socket.send(send_msg)
            return True
        else:
            print('ERROR: Received unknown command')
            return False
    except Exception as e:
        print(f'ERROR: {e}')
        return False

    # If the server was launched with encryption or password (it's not possible to launch the server with password and not data encryption as that wouldn't be secure)
def authenticate_client(client_socket, address):

    global server_attributes # use the variable in a global scope (needs to be referenced in every function)
    if server_attributes['enc'] == '' or server_attributes['password'] == '': return True

    try:
        # create the dictionary to send
        msg = byting_dict({'op': encrypt_values('auth', server_attributes['enc']), 'type': encrypt_values("request", server_attributes['enc']), 'payload': encrypt_values('password', server_attributes['enc'])})
        client_socket.send(msg) # send the dictionary
        while True: # while cycle is not necessary in other implementations
            response = client_socket.recv(2048) # wait for response (buffer should be enough for the most amount of data)
                                                # alternatively in other implementations this buffer should be defined by the
                                                # header of the message itself, as that would be more secured
            if not response: # if server connection has been terminated
                return False
            else:
                msg = unbyting_dict(response) # the response is received in bytes. We need to exchange it to a dictionary form again 

                # print('From  {}:{}, Received: {}'.format(client_socket.getpeername()[0], client_socket.getpeername()[1], msg)) DEBUG

                # Check the response data
                if decrypt_values(msg['op'], server_attributes['enc']) == "auth" and decrypt_values(msg['type'], server_attributes['enc']) == "response":
                    
                    # print(decrypt_values(msg['payload'])) DEBUG

                    if decrypt_values(msg['payload'], server_attributes['enc']) == server_attributes['password']: # Authentication successfull
                        msg = byting_dict({'op': encrypt_values('auth', server_attributes['enc']), 'type': encrypt_values("response", server_attributes['enc']), 'payload': encrypt_values('success', server_attributes['enc'])})
                        client_socket.send(msg)
                        return True
                    else: # Provide fields not valid, raise error
                        print('Client {}:{} failed authentication'.format(address[0], address[1]))
                        msg = byting_dict({'op': encrypt_values('auth', server_attributes['enc']), 'type': encrypt_values("response", server_attributes['enc']), 'payload': encrypt_values('failed', server_attributes['enc'])})
                        client_socket.send(msg)
                return False

    except Exception as e:
        print(f'ERROR: {e}')
        return False

    # Initiate server with the provided arguments
def initiate_server(ip, port, enc, password):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try: # Try server creation
        server_socket.bind((ip, port))
    except:
        print('ERROR: Address already in use')
        return False # Server creation failed
    
    server_socket.listen(1)  # max backlog of connections
    global server_attributes # variable to be used in the whole program
    global server_queue # variable to be used from the kivy application to process received data from client
    server_queue = [] # initialize
    global client_queue # variable to be used from the kivy application to send data to client
    client_queue = [] # initialize
    global threads
    threads = list()
    global sockets
    sockets = list()
    sockets.append(server_socket) # 1st socket = server, 2nd = client

    # dictionary containing the room information
    server_attributes = {'ip': ip, 'port': port, 'enc': enc, 'password': password}

    print('Listening on {}:{}'.format(ip, port))

    while True:
        client_sock, address = server_socket.accept()
        print(f'Accepted client connection from {address}')
        sockets.append(client_sock)
        client_handler = threading.Thread(target=handle_client_connection,args=(client_sock,address),daemon=True) # establish connection  to the client
        threads.append(client_handler)
        client_handler.start()

    # Test if server creation is possible and port is free
def test_connection(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if server_socket.connect_ex((ip,port)) == 0:
        print('ERROR: Address already in use')
        return False # Server creation failed
    else:
        server_socket.close()
        time.sleep(2) # Make sure the server closes
        return True

def quit_server():
    global threads
    for index, thread in enumerate(threads):
            thread.join()

if __name__ == "__main__":
    # Default run for testing
    #initiate_server("0.0.0.0", 5005, '', '')
    #initiate_server("0.0.0.0", 5005, b'$\xa5\xab\x8b\x1b,\xed\x98m\x8c0gV\xec$\xad', '')
    initiate_server("0.0.0.0", 5005, b'$\xa5\xab\x8b\x1b,\xed\x98m\x8c0gV\xec$\xad', '1234')
    # IP, PORT, ENCRYPTION KEY, PASSWORD
