import socket, threading, signal, sys, base64, os, time, json
from Crypto.Cipher import AES

    # Encrypt the values given
def encrypt_values(data, key):
    # stress na encriptação de dicionários. Adaptar isso
    print(key)
    if key != '': 
        try:
            cipher = AES.new (key, AES.MODE_ECB) # Define the encryption algorithm
            result = cipher.encrypt(str(data)*16) # Fix padding
            return str (base64.b64encode (result), 'utf-8') # enconde into a format to be sent
        except Exception as e:
            print(f'No data to encrypt: {e}')
            print(f'Data: {data}')
            return None
    return data # If the connection isn't encrypted, just return the data

def decrypt_values(data, key):
    if key != '':
        try:
            cipher = AES.new (key, AES.MODE_ECB) # Define the encryption algorithm
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

    # Convert a dictionary into bytes data using json
def byting_dict(dictionary):
    """ Take a dictionary and convert it to bytes.    
    :param dictionary: 
    :return: byted dictionary
    """
    byted = json.dumps(dictionary)
    return byted.encode('utf-8')

    # Convert bytes data into a dictionary using json (inverse of unbyting_dict)
def unbyting_dict(dictionary):
    unbyted = dictionary.decode('utf-8')
    return json.loads (unbyted)