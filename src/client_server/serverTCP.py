from multiprocessing import cpu_count
import socket, threading, signal, sys, base64, os, time, json
from Crypto.Cipher import AES

def signal_handler(sig, frame):
    print('\nDone!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to exit...')

##

    # Encrypt the values given
def encrypt_values(data):
    # stress na encriptação de dicionários. Adaptar isso
    if room_attributes['enc'] != '': 
        cipher = AES.new (room_attributes['enc'], AES.MODE_ECB) # Define the encryption algorithm
        result = cipher.encrypt(str(data)*16) # Fix padding
        return str (base64.b64encode (result), 'utf-8') # enconde into a format to be sent
    return data # If the connection isn't encrypted, just return the data

    # Decrypt the values given
def decrypt_values(data):
    if room_attributes['enc'] != '':
        try:
            cipher = AES.new (room_attributes['enc'], AES.MODE_ECB) # Define the encryption algorithm
            result = base64.b64decode (data) # decode the information
            result = cipher.decrypt(result) # decrypt the information
            result = result[0:round((len(result)/16))] # Fix the exta padding
            # result = base64.b64decode (data) # DEBUG
            # result = cipher.decrypt (result) # DEBUG
            return result.decode('utf-8') # return the decrypted result
        except Exception as e:
            print(f'No data to decypt: {e}')
            print(f'Data: {data}')
            return None
    return data # If the connection isn't encrypted, just return the data

    # Convert a dictionary into bytes data using json
def byting_dict(dictionary):
    byted = json.dumps(dictionary)
    return byted.encode('utf-8')

    # Convert bytes data into a dictionary using json (inverse of unbyting_dict)
def unbyting_dict(dictionary):
    unbyted = dictionary.decode('utf-8')
    return json.loads (unbyted)

    # Queue of type FILO (First in Last Out)
def queue_client_data(data, *kwargs):
    global s_queue
    s_queue.append(data) # Add the data to the most recent

    # Get the oldest queue data 
def get_queue_client_data(*kwargs):
    try:
        global s_queue
        if len(s_queue) == 0: return None # Stack doesn't have any data
        #  print(len(s_queue)) DEBUG
        return s_queue[(len(s_queue)-1)] # return the oldest value
    except: return None # If the stack hasn't been inicialized

    # Remove the oldest value of the Queue and returns it
    # In other implementation, just this function could be use
    # and no other need for the get_queue_client_data 
def remove_last_queue_client_data(*kwargs):
    try:
        global s_queue
        if len(s_queue) == 0: return None # Stack doesn't have any data
        return s_queue.pop(len(s_queue)-1) # return and delete the oldest value
    except: return None # If the stack hasn't been inicialized

    # Function that deals with server-client interaction
def handle_client_connection(client_socket,address): 
    global room_attributes # global scope variable
    
    if room_attributes['enc'] != '': # if the server was started using encryption
        # first we inform that the connection will be encripted and give the key
        if not inform_client(client_socket, 'encryption', ''):
            client_socket.close()
            return False

    # Authenticate client connection
    if not authenticate_client(client_socket, address): # If client didn't pass authentication close connection
        client_socket.close()
        return False

    # Inform the client about the room's name
    if not inform_client(client_socket, 'room_name', ''):
        client_socket.close()
        return False
    
    data = get_data(client_socket, 'refresh_rate') # Get the client choosen refresh rate
    if not data[0]:
        client_socket.close()
        return False
    else:
        try:
            room_attributes['refresh_rate'] = int(data[1]) # parsse the received value to integer
        except:
            print("ERROR: Bad conversion")
            client_socket.close()
            return False
    print(f'REFRESH: {room_attributes}')
    try:
        while True:
            time.sleep(room_attributes['refresh_rate'])
            data = get_data(client_socket, 'sys_info') # Ask the client for the data
            # print(len(get_queue_client_data())) DEBUG
            if data[0]: # data received
                print(data[1]) 
            else:
                print(data[1]) # Error
                client_socket.close()
                return False
    except Exception as e:
        print(f'Error: {e}')
        return [False, 'error']

    # Function to get data from the client
def get_data(client_socket, type):
    try:
        if type == 'refresh_rate': # type of data to get from the client
            # Example send_msg = {'op': 'data', 'type': 'request', 'field': 'refresh_rate', 'refresh_rate': '.'}
            send_msg = byting_dict({'op': encrypt_values('data'), 'type': encrypt_values("request"), 'field': encrypt_values('refresh_rate'), 'refresh_rate': encrypt_values('.')})
            client_socket.send(send_msg)
        elif type == 'sys_info': # type of data to get from the client
            # Example send_msg = {'op': 'data', 'type': 'request', 'field': 'sys_info', 'sys_info': '.'}
            send_msg = byting_dict({'op': encrypt_values('data'), 'type': encrypt_values("request"), 'field': encrypt_values('sys_info'), 'sys_info': encrypt_values('.')})
            client_socket.send(send_msg)
        while True:
            response = client_socket.recv(2048) # wait for response (buffer should be enough for the most amount of data)
                                                # alternatively in other implementations this buffer should be defined by the
                                                # header of the message itself, as that would be more secured
            if not response: # connection with server ended
                [False, 'error']
            else: 
                recv_msg = unbyting_dict(response)
                # print('From  {}:{}, Received: {}'.format(client_socket.getpeername()[0], client_socket.getpeername()[1], recv_msg)) DEBUG
                if decrypt_values(recv_msg['op']) == "data" and decrypt_values(recv_msg['type']) == "response": # Decrypt the values received and check the dictionary
                    if decrypt_values(recv_msg['field']) == 'refresh_rate': 
                        return [True, decrypt_values(recv_msg['refresh_rate'])] # refresh rate received (amount of time per second for the server to ask for system information)
                    elif decrypt_values(recv_msg['field']) == 'sys_info': # process the client system information received
                        # Decrypt the values received
                        recv_msg['sys_info']['platform'] = decrypt_values(recv_msg['sys_info']['platform'])
                        recv_msg['sys_info']['cpu'] = decrypt_values(recv_msg['sys_info']['cpu'])
                        recv_msg['sys_info']['cpu_usage'] = decrypt_values(recv_msg['sys_info']['cpu_usage'])
                        recv_msg['sys_info']['ram'] = decrypt_values(recv_msg['sys_info']['ram'])
                        recv_msg['sys_info']['total_ram'] = decrypt_values(recv_msg['sys_info']['total_ram'])
                        data = {'ip': client_socket.getpeername()[0], 'port': client_socket.getpeername()[1], 'sys_info': recv_msg['sys_info']}
                        queue_client_data(data) # add this data to the queue for the kivy application to process
                        return [True, recv_msg['sys_info']]
                return [False, 'error']
    except Exception as e:
        print(f'ERROR: {e}')
        return [False, 'error']

    # Provide information to the client
    # Doesn't accept a response
    # There is no point to have a return from the client stating that he received the data, since we are using the TCP protocol
def inform_client(client_socket, type, message):
    global room_attributes # global scope variable
    try:
        # Example send_msg = {'op': 'info', 'type': 'message', 'messsage': '...'}
        if type == 'message': # type of information to send to the server
            send_msg = byting_dict({'op': encrypt_values('info'), 'type': encrypt_values('message'), 'messsage': encrypt_values(message)})
            client_socket.send(send_msg)
            return True
        # Example send_msg = {'op': 'info', 'type': 'encryption', 'cipher': '...'}
        elif type == 'encryption': # type of information to send to the server
            # key already generated in the main.py file
            cipher = str (base64.b64encode (room_attributes['enc']), 'utf8') # encode the key to be sent
            #send_msg = byting_dict({'op': encrypt_values('info'), 'type': encrypt_values('encryption'), 'cipher': cipher})
            send_msg = byting_dict({'op': 'info', 'type': 'encryption', 'cipher': cipher}) # only encrypt the cipher
            client_socket.send(send_msg)
            return True
        # Example send_msg = {'op': 'info', 'type': 'room_name', 'room_name': '...'}
        elif type == 'room_name': # type of information to send to the server
            send_msg = byting_dict({'op': encrypt_values('info'), 'type': encrypt_values('room_name'), 'room_name': encrypt_values(room_attributes['name'])})
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

    global room_attributes # use the variable in a global scope (needs to be referenced in every function)
    if room_attributes['enc'] == '' or room_attributes['password'] == '': return True

    try:
        # create the dictionary to send
        msg = byting_dict({'op': encrypt_values('auth'), 'type': encrypt_values("request"), 'payload': encrypt_values('password')})
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
                if decrypt_values(msg['op']) == "auth" and decrypt_values(msg['type']) == "response":
                    
                    # print(decrypt_values(msg['payload'])) DEBUG

                    if decrypt_values(msg['payload']) == room_attributes['password']: # Authentication successfull
                        msg = byting_dict({'op': encrypt_values('auth'), 'type': encrypt_values("response"), 'payload': encrypt_values('success')})
                        client_socket.send(msg)
                        return True
                    else: # Provide fields not valid, raise error
                        print('Client {}:{} failed authentication'.format(address[0], address[1]))
                        msg = byting_dict({'op': encrypt_values('auth'), 'type': encrypt_values("response"), 'payload': encrypt_values('failed')})
                        client_socket.send(msg)
                return False

    except Exception as e:
        print(f'ERROR: {e}')
        return False

    # Initiate server with the provided arguments
def initiate_server(ip, port, max_hosts, name, enc, password):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try: # Try server creation
        server_socket.bind((ip, port))
    except:
        print('ERROR: Address already in use')
        return False # Server creation failed
    
    server_socket.listen(1)  # max backlog of connections
    global s_sock
    s_sock = server_socket # to be used on server closing
    global room_attributes # variable to be used in the whole program
    global s_queue # variable to be used from the kivy application to process received system information
    s_queue = [] # initialize

    # dictionary containing the room information
    room_attributes = {'ip': ip, 'port': port, 'max_hosts': max_hosts, 'name': name, 'enc': enc, 'password': password, 'refresh_rate': ''}

    print('Listening on {}:{}'.format(ip, port))

    while True:
        client_sock, address = server_socket.accept()
        print(f'Accepted client connection from {address}')
        client_handler = threading.Thread(target=handle_client_connection,args=(client_sock,address),daemon=True) # handle connection for every client
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

#def quit_server():
#    global s_sock
#    print('NOTICE: Server closed')
#    s_sock.close()

if __name__ == "__main__":
    # Default run for testing
    #initiate_server("0.0.0.0", 5005, 5, 'test', '', '')
    #initiate_server("0.0.0.0", 5005, 5, 'test', b'$\xa5\xab\x8b\x1b,\xed\x98m\x8c0gV\xec$\xad', '')
    initiate_server("0.0.0.0", 5005, 5, 'test', b'$\xa5\xab\x8b\x1b,\xed\x98m\x8c0gV\xec$\xad', 'rc1_rocks')
