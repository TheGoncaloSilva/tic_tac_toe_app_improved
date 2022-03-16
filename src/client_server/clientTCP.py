from http import client, server
from pickletools import read_int4
import socket, signal, sys, platform, psutil, base64, json
from Crypto.Cipher import AES

def signal_handler(sig, frame):
    print('\nDone!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to exit...')

## Code

def encrypt_values(data):
    global rooms_enc
    if rooms_enc != '':
        cipher = AES.new (rooms_enc, AES.MODE_ECB) # Define the encryption algorithm
        #result = cipher.encrypt (bytes(data, 'utf8'))
        #return str (base64.b64encode (result), 'utf8') # encrypted result
        result = cipher.encrypt(str(data)*16) # Fix padding
        return str (base64.b64encode (result), 'utf-8')
    return data

def decrypt_values(data):
    global rooms_enc
    if rooms_enc != '':
        try:
            cipher = AES.new (rooms_enc, AES.MODE_ECB) # Define the encryption algorithm
            result = base64.b64decode (data)
            result = cipher.decrypt(result)
            result = result[0:round((len(result)/16))] # Fix the exta padding
            #result = base64.b64decode (data)
            #result = cipher.decrypt (result)
            return result.decode('utf-8') # Decrypted result
        except Exception as e:
            print(f'No data to decypt: {e}')
            print(f'Data: {data}')
            return None
    return data

def byting_dict(dictionary):
    byted = json.dumps(dictionary)
    return byted.encode('utf-8')

def unbyting_dict(dictionary):
    unbyted = dictionary.decode('utf-8')
    return json.loads (unbyted)

    # Principal function to operate the client 
def operate_client(client_sock):
    while True:
        try: 
            server_msg = client_sock.recv(5120) # wait for response (buffer should be enough for the most amount of data)
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
                    return False
                elif client_response[1] == 'no_response': # Information not to be sent to server
                    pass
                else: 
                    client_sock.send(byting_dict(client_response[1]))
        except (socket.timeout, socket.error):
            print('ERROR: Please try again!')
            client_sock.close()
            return False

    # Function to process the received information from the server
def new_message(server_msg):
    if decrypt_values(server_msg['op']) == 'auth':
        msg = authenticate_client(server_msg)
    elif decrypt_values(server_msg['op']) == 'info' or server_msg['op'] == 'info': # When providing the algorithm only use encryption on the cipher
        msg = inform_client(server_msg)
    elif decrypt_values(server_msg['op']) == 'data':
        msg = data_client(server_msg)
    else: 
        msg = [False, 'ERROR: Received unknown command']
    return msg

    # Function to authenticate the client with the server
def authenticate_client(server_msg):
    try:
        # Example server_msg = {'op': 'auth', 'type': 'request', 'payload': 'password'}
        if decrypt_values(server_msg['type']) == 'request' and decrypt_values(server_msg['payload']) == 'password':
            global rooms_password
            rooms_password = input("INPUT: Input the Room's Password: ") # Password to be sent to the server for comparison
            msg = {'op': encrypt_values('auth'), 'type': encrypt_values('response'), 'payload': encrypt_values(rooms_password)}
            return [True, msg]
        # Example server_msg = {'op': 'auth', 'type': 'response', 'payload': '...'}
        elif decrypt_values(server_msg['type']) == 'response':
            if decrypt_values(server_msg['payload']) == 'success':
                print("SUCCESS: Authentication Successfull\n")
                return [True,'no_response']
            else: 
                return [False,'END: Client failed authentication']
        else:
            return [False, 'ERROR: Received unknown command']
    except Exception as e:
        return [False,f'ERROR: {e}']

    # Function to process the information received from the server
def inform_client(server_msg):
    try:
        # Example server_msg = {'op': 'info', 'type': 'message', 'messsage': '...'}
        if decrypt_values(server_msg['type']) == 'message':
            msg = decrypt_values(server_msg['message']) # Receive the message
            print(f'SERVER MESSAGE: {msg}')
            return [True, 'no_response']
        # Example server_msg = {'op': 'info', 'type': 'encryption', 'cipher': '...'}
        elif decrypt_values(server_msg['type']) == 'encryption' or server_msg['type'] == 'encryption':
            global rooms_enc
            rooms_enc = base64.b64decode (server_msg['cipher']) # Received cipherkey
            print(f'INFO: server sent the key {str(rooms_enc)}')
            return[True, 'no_response']
        # Example server_msg = {'op': 'info', 'type': 'room_name', 'room_name': '...'}
        elif decrypt_values(server_msg['type']) == 'room_name':
            global rooms_name
            rooms_name = decrypt_values(server_msg['room_name']) # Received Room name
            print(f'INFO: Welcome to the Room {rooms_name}')
            return[True, 'no_response']
        else:
            return[False, 'ERROR: Received unknown command']
    except Exception as e:
        return [False,f'ERROR: {e}']

    # Function to prepare the data to be sent to the server
def data_client(server_msg):
    try:
        # Example server_msg = {'op': 'data', 'type': 'request', 'field': 'refresh_rate', 'refresh_rate': '...'}
        if decrypt_values(server_msg['type']) == 'request':
            if decrypt_values(server_msg['field']) == 'refresh_rate':
                global refresh_rate
                msg = {'op': encrypt_values('data'), 'type': encrypt_values('response'), 'field': server_msg['field'], 'refresh_rate':  encrypt_values(refresh_rate)}
                return [True, msg]
            elif decrypt_values(server_msg['field']) == 'sys_info':
                print(f'INFO: System info sent')
                msg = {'op': encrypt_values('data'), 'type': encrypt_values('response'), 'field': server_msg['field'], 'sys_info': get_system_info()}
                return[True, msg]
        else:
            return[False, 'Error: Received unknown command']
    except Exception as e:
        return [False,f'Error: {e}']

    # Function to get the client system information
    # and encrypt it if necessary
def get_system_info():
    info = {}
    try:
        info['platform'] = encrypt_values(platform.system()) # platform/ os used
        info['cpu'] = encrypt_values(platform.processor()) # cpu model/ architecture
        info['cpu_usage'] = encrypt_values(psutil.cpu_percent()) # percentage of memory in use
        info['ram'] = encrypt_values(psutil.virtual_memory().percent) # percentage of memory in use
        info['total_ram'] = encrypt_values(round(psutil.virtual_memory().total / (1024.0 **3))) # total amount of RAM
        return info # return the system information
    except  Exception as e:
        print(e)
        return False


def main():
    ### Variables with global scope
    global rooms_ip
    rooms_ip = ''
    global rooms_port
    rooms_port = 0
    global refresh_rate
    refresh_rate = 0
    global rooms_name
    rooms_name = ''
    global rooms_enc
    rooms_enc = '' # default value is no encryption. if otherwise, server will inform
    global rooms_password
    rooms_password = ''

    print("\n########################################################################")
    print("##### Welcome to the Network Manager client Monitoring application #####")
    print("########################################################################\n")
   
    # Get values to connect to server
    rooms_ip = input("Input the Room's ip: ")
    rooms_port = input("Input the Room's Port: ")

    try: # checking if the port is a number
        rooms_port = int(rooms_port)
    except:
        print("ERROR: The port should be a number and not contain characters")
        exit(1)

    while True:
        # refresh rate is the amount of time, in seconds, for the client to send the values to the server
        refresh_rate = input("Input the refresh rate of the data, between 1 and 10 seconds: ")
        try: # check the input values
            if int(refresh_rate) < 1 or int(refresh_rate) > 10: # show error and repeat cycle
                print("ERROR: refresh rate should be a value between 1 and 10")
                exit(2)
            break
        except:
            print("ERROR: refresh rate needs to be a number")

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create Socket TCP
    try:
        client_sock.connect((rooms_ip, rooms_port)) # Atempt server connection
    except:
        print("ERROR: An error occurred trying to connect to the server")
        exit(3)
    print()
    operate_client(client_sock) # Operate the client

    client_sock.close() # Closes the connection between the server and the client
    exit(4)

if __name__ == "__main__":
    main() # Call the main function uppon startup

