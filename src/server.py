#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import socket
import select
import json
import base64
import csv
import random
import os
from Crypto import Cipher
from common_comm import send_dict, recv_dict, sendrecv_dict

from Crypto.Cipher import AES

# Dicionário com a informação relativa aos clientes
# Exemplo do formato
# gammers = {
#			 'manel': { 'socket': <socket ... raddr=('127.0.0.1', 46196)>,
#						'cipher': b')6\x0c\xba\xf8\x14\xa7iU\xac\x8a~\xe0H~0',
#						'guess': 36, 'max_attempts': 22, 'attempts': 0 }
# }
# Método de acesso: gamers[client_id][0][campo]
gamers = {}

# Código seguinte, usado apenas para testes
def write_gamer(value) : # overwrite o gamers caso seje preciso
	global gamers
	gamers = value

def update_gamer(value) : # atualizar o gamers caso seje preciso
	global gamers
	gamers.update(value)

def print_gamer(): # mostrar o conteúdo do dicionário gamers
	return gamers

def print_client(client_id):
	return gamers[client_id]
# Fim do código para testes

# return the client_id of a socket or None
def find_client_id (client_sock):
	for val in gamers:	# val tem o client_id de cada registo
		if client_sock == gamers[val][0]['socket']: # check socket of each entry
   			return val # client_id found
	
	return None


# Função para encriptar valores a enviar em formato json com codificação base64
# return int data encrypted in a 16 bytes binary string and coded base64
def encrypt_intvalue (client_id, data):
	cipher = AES.new (gamers[client_id][0]['cipher'], AES.MODE_ECB) # Definir o algoritmo de encriptação tendo em conta a chave fornecida
	result = cipher.encrypt (bytes("%16d" % (int(data)), 'utf8'))
	return str (base64.b64encode (result), 'utf8') # resultado encriptado
	


# Função para desencriptar valores recebidos em formato json com codificação base64
# return int data decrypted from a 16 bytes binary string and coded base64
def decrypt_intvalue (client_id, data):
	cipher = AES.new (gamers[client_id][0]['cipher'], AES.MODE_ECB) # Definir o algoritmo de encriptação tendo em conta a chave fornecida
	result = base64.b64decode (data)
	result = cipher.decrypt (result)
	return int (str (result, 'utf8')) #resultado desencriptado


#
# Incomming message structure:
# { op = "START", client_id, [cipher] }
# { op = "QUIT" }
# { op = "GUESS", number }
# { op = "STOP", number, attempts }
#
# Outcomming message structure:
# { op = "START", status, max_attempts }
# { op = "QUIT" , status }
# { op = "GUESS", status, result }
# { op = "STOP", status, guess }


#
# Suporte de descodificação da operação pretendida pelo cliente
#
def new_msg (client_sock):
	response = {}
	request = recv_dict (client_sock)
	try : # se um cliente aceder sem o formato correto
		op = request['op'].upper() # Operação escolhida pelo cliente (text.upper para não haver problemas com letras minúsculas e maiúsculas)
	except :
		return None
	#cipher = request['cipher'] -> cifra escolhida pelo utilizador
	print("Request" + str(request)) # DEBUG
	if (op == 'START') :
		response = new_client(client_sock, request)
	elif (op == 'QUIT') :
		response = quit_client(client_sock, request)
	elif (op == 'GUESS') :
		response = guess_client(client_sock, request)
	elif (op == 'STOP') :
		response = stop_client(client_sock, request)
	else :
		response = { 'op': request['op'], 'status': False, 'error' : 'Operação Inválida' }

	print("Response: " + str(response)) # DEBUG

	send_dict (client_sock, response) # enviar o resultado para o cliente
	return response

# read the client request
# detect the operation requested by the client
# execute the operation and obtain the response (consider also operations not available)
# send the response to the client


#
# Suporte da criação de um novo jogador - operação START
#
def new_client (client_sock, request):
	# obter o request e verificar guardar um novo registo no dicionário gamers
	# Check the return value and print message
	try : # "testar" o campo client_id para verificar se existe
		request['client_id']
	except :
		return { 'op': 'START', 'status': False, 'error': 'Condições inválidas' }

	if (search_gamers(request['client_id']) != None) : # Procurar se o client já está registado
  		return { 'op': 'START', 'status': False, 'error': 'Cliente existente' }

	secret_number = random.randint(0, 100) # Gera o número secreto
	print("****** NÚMERO SECRETO: " + str(secret_number) + " de " + str(request['client_id']) + " ******") # DEBUG
	max_Plays = random.randint(10, 30) # Gera o número máximo de tentativas

	try : # testar se o campo cipher existe 
		cipherkey = base64.b64decode (request['cipher']) # Decode cypherkey
	except : # se o campo cipher não existir, quer dizer que o utilizador não escolheu encriptar a ligação
		cipherkey = None

	gamers.update({request['client_id'] : [{ 'socket': client_sock, 'cipher' : cipherkey,
			'guess' : secret_number, 'max_attempts' : max_Plays, 'attempts' : 0 }]}) # Atualizar o dicionário

	if(cipherkey != None) : # Se o cliente escolheu comunicar por encriptação
		max_Plays = encrypt_intvalue(request['client_id'], max_Plays) # encriptar o número de jogadas

	return { 'op': 'START', 'status': 'True', 'max_attempts' : max_Plays }

# detect the client in the request
# verify the appropriate conditions for executing this operation
# obtain the secret number and number of attempts
# process the client in the dictionary
# return response message with results or error message

#
# Procurar no dicionário gamers se já existe um jogador
# value = client_id
#
def search_gamers(value):
	for val in gamers:
		if value == val: # Check each line 
   			return val # client_found
	return None


#
# Suporte da eliminação de um cliente
#
def clean_client (client_sock):
	client_id = find_client_id(client_sock) # Id do cliente devolvido pela função
	if (client_id == None):
  		return False
	del gamers[client_id] # eliminar o cliente do dicionário de jogadores ativos
	return True

# obtain the client_id from his socket and delete from the dictionary


#
# Suporte do pedido de desistência de um cliente - operação QUIT
#
def quit_client (client_sock, request):
	client_id = find_client_id(client_sock) # Id do cliente devolvido pela função

	try : # Testar se o cliente escolheu a operação certa
		request['op'] == "QUIT"
	except :
		return { 'op': 'QUIT', 'status': False, 'error': 'Erro na operação' }

	if (client_id == None): # Se não existir nenhum cliente no dicionário de jogadores atuais
  		return { 'op': 'QUIT', 'status': False, 'error': 'Cliente inexistente' }

	result = { 'client_id' : client_id, 'secret_number' : gamers[client_id][0]['guess'], 
	'max_plays' : gamers[client_id][0]['max_attempts'], 'current_plays' : gamers[client_id][0]['attempts'],
	'result' : 'QUIT'} # Dicionário para guardar no ficheiro csv
	
	update_file(client_id, result) # atualizar o ficheiro
	clean_client(client_sock) # remover o cliente

	return {'op': 'QUIT', 'status': True}

# obtain the client_id from his socket
# verify the appropriate conditions for executing this operation
# process the report file with the QUIT result
# eliminate client from dictionary
# return response message with result or error message


#
# Suporte da criação de um ficheiro csv com o respectivo cabeçalho
# <client_id> <secret_number> <max_attempts> <attempts_made> <result>
# result:
# 		QUIT -> cliente desiste
#		SUCCESS -> se o cliente acertou, respeitando o número máximo de jogadas
#		FAILURE -> se não acertou o nº secreto ou se excedeou o nº máximo de jogadas
#
def create_file ():
	# create report csv file with header
	file = open('report.csv', 'w') # abrir ou criar o ficheiro se não existir
	writer = csv.DictWriter(file, delimiter=';', fieldnames=['client_id', 'secret_number', 'max_plays', 'current_plays', 'result']) # Preferências e nomes das colunas
	writer.writeheader() # Escrever os nomes das colunas
	file.close()
	return None

#
# Suporte da actualização de um ficheiro csv com a informação do cliente e resultado
#
def update_file (client_id, result): # client_id é redudante
	file = open('report.csv', 'a') # abrir o ficheiro em modo append (Não sobrescrever os dados existentes)
	writer = csv.DictWriter(file, delimiter=';', fieldnames=['client_id', 'secret_number', 'max_plays', 'current_plays', 'result']) # Preferências e nomes das colunas
	writer.writerow(result) # Escrever uma nova linha no ficheiro
	file.close()
	return None
# update report csv file with the result from the client


#
# Suporte da jogada de um cliente - operação GUESS
#
def guess_client (client_sock, request):
	client_id = find_client_id(client_sock) # Id do cliente devolvido pela função

	try : # testar o campo number
		request['number']
	except : # Se o campo number não existir no dicionário enviado
		return { 'op': 'GUESS', 'status': False, 'error': 'Condições inválidas' }

	if (client_id == None): # Se não existir nenhum cliente no dicionário de jogadores atuais
  		return { 'op': 'GUESS', 'status': False, 'error': 'Cliente inexistente' }

	gamers[client_id][0]['attempts'] += 1 # contar uma tentativa
	clientNumber = request['number'] # tentativa do cliente

	if (gamers[client_id][0]['cipher'] != None) : # se o cliente encriptou a resposta, vamos desencriptá-la
		clientNumber = decrypt_intvalue(client_id, clientNumber)
	
	result = ''# valor por defeito do resultado 

	if(clientNumber < gamers[client_id][0]['guess']) : # se o cliente escolheu um número inferior ao número secreto
		result = 'larger'
	elif (clientNumber > gamers[client_id][0]['guess']) : # se o cliente escolheu escolheu um número superior ao número secreto
		result = 'smaller'
	else : # se o cliente acertou o número secreto
		result = 'equals'

	return { 'op' : 'GUESS', 'status' : True, 'result' : result}

# obtain the client_id from his socket
# verify the appropriate conditions for executing this operation
# return response message with result or error message


#
# Suporte do pedido de terminação de um cliente - operação STOP
#
def stop_client (client_sock, request):
	client_id = find_client_id(client_sock) # Id do cliente devolvido pela função

	try : # testar se os campos existem
		user_attempts = request['attempts']
		user_number = request['number']
	except : # Se o campo number e attempts não existir no dicionário enviado
		return { 'op': 'STOP', 'status': False, 'error': 'Condições inválidas' }
	
	if (client_id == None): # Se não existir nenhum cliente no dicionário de jogadores atuais
  		return { 'op': 'STOP', 'status': False, 'error': 'Cliente inexistente' }

	if (gamers[client_id][0]['cipher'] != None) : # se o cliente escolheu encriptar os números, vamos desencriptá-los
		user_attempts = decrypt_intvalue(client_id, user_attempts)
		user_number = decrypt_intvalue(client_id, user_number)

	response = {'op' : 'QUIT', 'status' : False, 'error' : 'Número de jogadas inconsistente'} # resposta por defeito
	write = 'FAILURE' # resultado de defeito a ser guardado no ficheiro report.csv

	if (int(user_attempts) == int(gamers[client_id][0]['attempts']) and int(user_attempts) <= int(gamers[client_id][0]['max_attempts'])) : # se o valor de tentativas for certo e menor que o valor máximo de tentativas
		response = {'op' : 'STOP', 'status' : True, 'guess' : gamers[client_id][0]['guess']} # Se o jogador indicar o número correto de tentativas e elas forem menores ou igual ao número máximo
		if (gamers[client_id][0]['cipher'] != None) : # se o cliente escolheu encriptar os dados, vamos encriptar o número secreto
			response['guess'] = encrypt_intvalue(client_id, gamers[client_id][0]['guess']) # alterar o dicionário para incluir o dado encriptado
		if ((int(user_number) == int(gamers[client_id][0]['guess']))) : # se o cliente acertou o número secreto
			write = 'SUCCESS' # valor a ser guardado como resultado no ficheiro report.csv

	result = { 'client_id' : client_id, 'secret_number' : gamers[client_id][0]['guess'], 
	'max_plays' : gamers[client_id][0]['max_attempts'], 'current_plays' : gamers[client_id][0]['attempts'],
	'result' : write} # Dicionário para guardar no ficheiro json
			
	update_file(client_id, result) # atualizar o ficheiro report.csv
	clean_client(client_sock) # apagar o cliente do dicionário de jogadores ativos

	return response # devolver a resposta para ser enviada ao cliente

# obtain the client_id from his socket
# verify the appropriate conditions for executing this operation
# process the report file with the SUCCESS/FAILURE result
# eliminate client from dictionary
# return response message with result or error message


def main(argv):
	# validate the number of arguments and eventually print error message and exit with error
	# verify type of of arguments and eventually print error message and exit with error
	if (len(argv) <= 1) : # se os argumentos não forem os suficientes
		print("Porto de acesso precisa de ser especificado")
		exit(4) # fechar o programa

	try : # testar se o valor é um número
		port = int(argv[1])
	except :
		print("O valor do porto de acesso precisa de ser um número")
		exit(4)

	if (port <= 0 or port > 65535 ) : # testar o valor do porto e verificar a condição
		print("Valor do porto tem de ser superior a 0 e inferior a 65535")
		exit(4)

	server_socket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
	try: # tentar a conecção
		server_socket.bind (("127.0.0.1", port))
		server_socket.listen (10)
	except PermissionError: # se a porta estiver ocupada
		print("ERRO : Acesso negado com a porta de acesso fornecida")
		exit(4)
	except OSError: # se o servidor já estiver a correr
		print("ERRO : O servidor já está a correr")
		exit(4)


	clients = []
	create_file ()

	while True:
		try:
			available = select.select ([server_socket] + clients, [], [])[0]
		except ValueError:
			# Sockets may have been closed, check for that
			for client_sock in clients:
				if client_sock.fileno () == -1: client_sock.remove (client) # closed
			continue # Reiterate select

		for client_sock in available:
			# New client?
			if client_sock is server_socket:
				newclient, addr = server_socket.accept ()
				clients.append (newclient)
			# Or an existing client
			else:
				# See if client sent a message
				if len (client_sock.recv (1, socket.MSG_PEEK)) != 0:
					# client socket has a message
					# print ("server" + str (client_sock))
					new_msg (client_sock)
				else: # Or just disconnected
					clients.remove (client_sock)
					clean_client (client_sock)
					client_sock.close ()
					break # Reiterate select

if __name__ == "__main__":
	main(sys.argv)
