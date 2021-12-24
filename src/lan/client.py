#!/usr/bin/python3

import os
from server import clean_client
import sys
import socket
import json
import base64
from common_comm import send_dict, recv_dict, sendrecv_dict

from Crypto.Cipher import AES

# Função para encriptar valores a enviar em formato jsos com codificação base64
# return int data encrypted in a 16 bytes binary string coded in base64
def encrypt_intvalue(cipherkey, data):
    cipher = AES.new (cipherkey, AES.MODE_ECB) # Definir o algoritmo de encriptação tendo em conta a chave fornecida
    result = cipher.encrypt (bytes("%16d" % (int(data)), 'utf8'))
    return str (base64.b64encode (result), 'utf8') # resultado encriptado


# Função para desencriptar valores recebidos em formato json com codificação base64
# return int data decrypted from a 16 bytes binary strings coded in base64
def decrypt_intvalue(cipherkey, data):
    cipher = AES.new (cipherkey, AES.MODE_ECB) # Definir o algoritmo de encriptação tendo em conta a chave fornecida
    result = base64.b64decode (data)
    result = cipher.decrypt (result)
    return int (str (result, 'utf8')) # resultado desencriptado


# verify if response from server is valid or is an error message and act accordingly
# If true there's an error
def validate_response(client_sock, response):
    if "error" in response: # Se existir a chave error no dicionário enviado pelo server
        print("Erro!: " + response['error']) # Mostra o erro
        return True 
    else: 
        return False


# process QUIT operation
def quit_action(client_sock, attempts):
    quit = {"op": "QUIT"} # dicionário para ser enviado
    recvquit = sendrecv_dict(client_sock, quit) # enviar o dicionário
    if validate_response(client_sock, recvquit): return recvquit['error'] # se houver um erro, mostra-o
    else:
        print(f"Desistiu do jogo depois de {attempts} tentativas") # Avisa o jogador que a operação foi efetuada e o número de tentativas
        return None


# Outcomming message structure:
# { op = "START", client_id, [cipher] }
# { op = "QUIT" }
# { op = "GUESS", number }
# { op = "STOP", number, attempts }
#
# Incomming message structure:
# { op = "START", status, max_attempts }
# { op = "QUIT" , status }
# { op = "GUESS", status, result }
# { op = "STOP", status, guess }


#
# Suporte da execução do cliente
#
def run_client(client_sock, client_id):
    tries = 0 # variavél usada para contar as tentativas feitas
    lastAttempt = 0 # variável usada para guardar a ultima tentativa do utilizador
    print("*# Bem vindo aoooooooooo Adivinha o número secreto!!!! *#")
    print("Deseja usar encriptação de dados? (S/N)")

    answer = input("-> ").upper() # Escolha da resposta pelo utilizador (text.upper() para não haver problemas com letras maiúsculas e minúsculas)
    while answer != "S" and answer != "N": # Enquanto o utilizador não escolher o valor correto
        answer = input("Inválido").upper() # text.upper() para não haver problemas com letras maiúsculas e minúsculas
    
    start = {'op': "START", 'client_id': client_id, 'cipher' : None} # dicionário de defeito, de pedido de começo de jogo ao servidor
    key = None # Valor por defeito da chave de encriptação

    if answer == "S": # Se o utilizador escolheu encriptar os dados
        key = os.urandom(16) # Gerar uma chave de encriptação
        start['cipher'] = str (base64.b64encode (key), 'utf8') # guardar a chave (de modo codificado) no dicionário 

    recvstart = sendrecv_dict(client_sock, start) # enviar os dados de começo de jogo para o servidor

    if validate_response(client_sock, recvstart): return None # validar que a resposta do servidor não contém um erro
    
    maxAttempts = recvstart['max_attempts'] # variável global contendo o valor máximo de tentativas

    if (key != None) : # Se o valor máximo de tentativas estiver encriptado, desencripta
        maxAttempts = decrypt_intvalue(key, maxAttempts)
    
    # print("Tentativas: " + str(maxAttempts)) # DEBUG
    
    while True:

        # Menu
        print()
        print("Tens " + str(maxAttempts - tries) + " tentativas restantes")
        print()
        print("########## MENU ##########")
        print("# O que pretendes fazer? #")
        print("# 1 - Adivinhar          #")
        print("# 2 - Terminar o jogo    #")
        print("# 3 - Desistir           #")
        print("##########################")
        print() # linha em branco

        #Escolha do menu
        try:
            print("Operação: ")
            option = int(input("-> "))
        except: 
            option = 999 # Se for inserido caracteres invés de números, é atribuido um valor por defeito que não acarreta uma opção
        
        #Operação Guess
        if option == 1:
            while True :
                try :  # testar se o cliente introduziu um caracter ou número
                    print("Adivinha o número secreto entre 0 e 100: ")
                    num = int(input("-> "))
                    if (num <= 100 and num >= 0): # verificar se foi introduzido um número fora da condição
                        break
                    else :
                        print("Erro!: Escolhe números entre 0 e 100")
                except :
                    print("Erro!: Por favor introduz apenas números")

            lastAttempt = num # variável global que guarda a última tentativa

            if (key != None) : # Se escolher encriptar, encripta a tentativa
                num = encrypt_intvalue(key, num)
    
            guess = {'op': "GUESS", 'number': num} # dicionário para ser enviado ao servidor
            recvguess = sendrecv_dict(client_sock, guess) # enviar o dicionário

            if validate_response(client_sock, recvguess): break # validar que não foi obtido um erro como resposta

            tries += 1 # registar que o utilizador fez uma tentativa e foi processada

            if recvguess['result'] == "equals": # o jogador acertou o número secreto
                print("*#* Conseguiste adivinhar *#*")
                option = 2 # mudar a escolha do utilizador, de forma a ser processado o término do jogo, pois acertou o número secreto
            elif recvguess['result'] == "smaller": # o jogador introduziu um número superior ao número secreto
                print("DICA: O número secreto é menor do que o inserido")
            elif recvguess['result'] == "larger": # o jogador introduziu um número inferior ao número secreto
                print("DICA: O número secreto é maior do que o inserido")
            else:
                print("Erro!: Ocorreu um erro") # ocorreu algum Erro

            if(tries >= maxAttempts) : # deixa o jogador jogar n tentativas até m jogadas máximas, de forma a n = m
                print("RESULTADO: Número máximo de tentativas obtido. O fim do jogo vai ser processado")
                option = 2 # mudar a escolha do utilizador, de forma a ser processado o término do jogo, pois o jogador excedeu as tentativas máximas
        
        #Operação Stop
        if option == 2:
            lastAttempt_toSend = lastAttempt # valor da última tentativa do jogador
            tries_toSend = tries # tentativas feitas pelo utilizador

            if (key != None) : # se o jogador escolheu encriptar os dados
                lastAttempt_toSend = encrypt_intvalue(key, lastAttempt) # encriptar o valor da última tentativa do jogador
                tries_toSend = encrypt_intvalue(key, tries) # encriptar o valor das tentativas do jogador

            stop = {"op": "STOP", "number": lastAttempt_toSend, "attempts": tries_toSend} # dicionário com o pedido de processamento da função
            recvstop = sendrecv_dict(client_sock, stop) # enviar o dicionário para o servidor

            if validate_response(client_sock, recvstop): break # validar que não foi obtido um erro como resposta            
            returnGuess = recvstop['guess'] # número secreto obtido como resposta

            if (key != None) : # se este número estiver encriptado, vamos desencriptá-lo
                returnGuess = decrypt_intvalue(key, returnGuess)

            if((str(lastAttempt) == str(returnGuess))) : # se o jogador acertou o número secreto
                print(f"As tuas tentativas deram fruto e conseguiste acertar, o número secreto era {returnGuess} e conseguiste acertar com " + str(tries) + " tentativas")
            else : # se o jogador falhou o número secreto
                print(f"O número secreto era {returnGuess}! Pena que não conseguiste acertar, boa sorte para a próxima")
            break
                
        #Operação Quit
        if option == 3:
            condition = quit_action(client_sock, tries)
            if condition == None: break # Se não houve erro
            else: # Se houver erro
                print(condition)
                break

        if(option < 1 or option > 3): print("ERRO!: Valor de operação inválido") #Se a opção inserida for inválida

    return None


def main(argv):
    # validate the number of arguments and eventually print error message and exit with error
    # verify type of of arguments and eventually print error message and exit with error
    if len(argv) < 3 or len(argv) > 4: # verificar se o número de argumentos introduzidos são válidos
        print("ERRO!: Argumentos inválidos, deve ter o formato:")
        print("python3 client.py client_id porto [máquina]")
        exit(4)
    elif len(argv) == 3: # se o utilizador não introduzir um endereço ip, atribui-se um por defeito
        hostname = "127.0.0.1"
    else : # atribuir o endereço ip
        hostname = argv[3]

    # Verifica a validade do id do cliente
    if not len(argv[1]): 
        print("ERRO!: ID de client inválido!")
        exit(4)

    # Verifica a validade da porta
    for i in range(0, len(argv[2]) - 1):
        if not argv[2][i].isdigit():
            print("ERRO!: Porta inválida! A porta só deve conter números")
            exit(4)

    if int(argv[2]) > 65535 or int(argv[2]) < 0:
        print("ERRO!: Porta inválida! Deve escrever um número entre 0 e 65535")
        exit(4)

    # Verifica a validade da máquina (endereço ip)
    host = hostname.split('.')
    for i in range(0, len(host) - 1):
        try : # o valor não é inteiro
            int(host[i])
            int(host[i])
        except :
            print("ERRO!: A máquina tem de ter números inteiros:")
            exit(4)
        if int(host[i]) < 0 or int(host[i]) > 255:
            print("ERRO!: A máquina é identificada da seguinte maneira:")
            print("X.X.X.X , sendo X um número entre 0 e 255")
            exit(4)

    port = int(argv[2]) # valor atribuído à porta

    # Socket
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Ligar ao servidor
    try : # testar se é possível efetuar a ligação
        client_sock.connect((hostname, port))
    except :
        print("Erro!: Aconteceu algum erro e a ligação não foi estabelecida")
        exit(3)

    run_client(client_sock, argv[1]) # função para efetuar todas as operações

    client_sock.close() # fechar a ligação com o servidor
    exit(0)


if __name__ == "__main__":
    main(sys.argv)