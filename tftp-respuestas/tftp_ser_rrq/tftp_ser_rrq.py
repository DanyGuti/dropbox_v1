#!/usr/bin/env python3

import sys
import os
import socket

NULL  = b'\x00'
RRQ   = b'\x00\x01'
WRQ   = b'\x00\x02'
DATA  = b'\x00\x03'
ACK   = b'\x00\x04'
ERROR = b'\x00\x05'

PORT = 50069
BLOCK_SIZE = 512
FILES_PATH ='./data/'

def send_error(s, addr, code, message):
	resp  = ERROR
	resp += code.to_bytes(2, 'big')
	resp += message.encode()
	resp += NULL
	s.sendto(resp, addr)

def send_file(s, addr, filename):
	try:
		f = open(os.path.join(FILES_PATH, filename), 'rb')
	except:
		send_error(s, addr, 1, 'File not found.')
		exit(1)

	data = f.read(BLOCK_SIZE)
	"""A COMPLETAR POR EL/LA ESTUDIANTE:
	Enviar al cliente el primer bloque de datos (DATA)
	"""
	resp  = DATA
	resp += b'\x00\x01' #se escribe en bytes el numero de bloque que es, que en este caso al ser el primero es el 1
	resp += data
	s.sendto(resp, addr)

	block_num = 1
	last = False if len(data) == BLOCK_SIZE else True
	while True:
		"""A COMPLETAR POR EL/LA ESTUDIANTE:
		Recibir el mensaje del cliente.
		Si es un mensaje de error, terminar.
		Comprobar que es un ACK, si no, volver al comienzo del bucle.
		Comprobar que el número de bloque es el correcto (block_num), si no, volver al comienzo del bucle.
		"""
		###########################################################################################
		resp, addr = s.recvfrom(64) #recive la respuesta del cliente
		opcode = resp[:2] #pone en una variable el tipo de dato
		if opcode == ERROR: #comprueba que no sea un error
			error_code = int.from_bytes(resp[2:4], 'big')
			print('Server error {}: {}'.format(error_code, resp[4:-1].decode()))
			exit(1)
		elif opcode != ACK: #comprueba si es algo distinto a ACK
			print('Unexpected response.')
			exit(1)
		###########################################################################################
		else: #ya ve que es un ACK 
			ack_num = int.from_bytes(resp[2:4], 'big') #coge el bloque
			if ack_num != block_num: #si no es igual vuelve alprincipio del while
				continue
			if last: #si es el ultimo se para la ejecucion
				break
			block_num += 1 
			data = f.read(BLOCK_SIZE) #lee la informacion del fichero y la almacena
			resp  = DATA #almacena el tipo de ato que se va a enviar
			resp += block_num.to_bytes(2, 'big') #pasa el numero de bloque a bytes
			resp += data #le añade la informacion(data)
			s.sendto(resp, addr) #le manda lo almacenado a la direccion del cliente
			if len(data) < BLOCK_SIZE: #si la longitud de los datos es < 512, ese era el ultimo
				last = True
			print('{}: {} bytes sent.'.format(filename, (block_num - 1) * BLOCK_SIZE + len(data)))
	f.close()

if __name__ == '__main__':
	"""A COMPLETAR POR EL/LA ESTUDIANTE:
	Crear un socket UDP en s y asociarle el puerto PORT.
	"""
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(('', PORT))
	while True:
		req, cli_addr = s.recvfrom(64)

		opcode = req[:2]
		if opcode != RRQ:
			send_error(s, cli_addr, 5, 'Unexpected opcode.')
		else:
			filename, mode, _ = req[2:].split(b'\x00')
			if mode.decode().lower() not in ('octet', 'binary'):
				send_error(s, cli_addr, 0, 'Mode unkown or not implemented')
				continue
		filename = os.path.basename(filename.decode()) # For security, filter possible paths.
		send_file(s, cli_addr, filename)
