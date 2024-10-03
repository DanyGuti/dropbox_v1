#!/usr/bin/env python3

import sys
import socket
import time

NULL  = b'\x00'
RRQ   = b'\x00\x01'
WRQ   = b'\x00\x02'
DATA  = b'\x00\x03'
ACK   = b'\x00\x04'
ERROR = b'\x00\x05'

PORT = 50069
BLOCK_SIZE = 512

def get_file(s, serv_addr, filename):
	start = time.time()

	f = open(filename, 'wb')
	"""A COMPLETAR POR EL/LA ESTUDIANTE:
	Enviar al servidor la petición de descarga de fichero (RRQ)
	"""
	req  = RRQ
	req +=  filename.encode() + NULL #el nombre del fichero, el valor 0 en binario en un byte para indicar el fin del nombre del fichero
	req += 'octet'.encode() + NULL #la palabra “octet” (modo de descarga en binario) segida de un 0 en binario en un byte
	s.sendto(req, serv_addr)
	expected_block = 1
	bytes_received = 0
	while True:
		"""A COMPLETAR POR EL/LA ESTUDIANTE:
		Recibir respuesta del servidor y comprobar que tiene el código correcto (DATA), si no, terminar.
		Comprobar que el número de bloque es el correcto (expected_block), si no, volver al comienzo del bucle.
		Escribir en el fichero (f) el bloque de datos recibido.
		Responder al servidor con un ACK y el número de bloque correspondiente.
		Si el tamaño del bloque de datos es menor que BLOCK_SIZE es el último, por tanto, salir del bucle.
		Si no, incrementar en uno el número de bloque esperado (expected_block)
		"""
		resp, serv_addr = s.recvfrom(4 + BLOCK_SIZE) #La cantidad de datos a recibir es de 4 bytes más el tamaño de bloque
		opcode = resp[:2] #cogemos el codigo para verificar si lo que nos ha mandado es de tipo DATA
		if opcode != DATA: #se verifica que sea de tipo DATA
			print('Unexpected response.')
			exit(1)
		else:
			block = int.from_bytes(resp[2:4], 'big') #cogemos el bloque
			if block != expected_block: #verificamos que sea el mismo bloque que el esperado
				continue
			data = resp[4:] #cogemos la data
			f.write(data) #escribimos la data
			bytes_received += len(data) #almacenamos los bytes recibidos
			req = ACK + expected_block.to_bytes(2, 'big') #creamos la respuesta: ACK + el bloque que se espera
			s.sendto(req, serv_addr) #lo mandamos
			if len(data) < BLOCK_SIZE: #verifica ver si es el ultimo bloque, ya que el ultimo es <512 bytes
				break
			expected_block += 1 #sumamos 1 al bloque esperado
	f.close()
	elapsed = time.time() - start
	bytes_received = (expected_block - 1) * BLOCK_SIZE + len(data)
	print('{} bytes received in {:.2e} seconds ({:.2e} b/s).'.format(bytes_received, elapsed, bytes_received * 8 / elapsed))

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print('Usage: {} server filename'.format(sys.argv[0]))
		exit(1)

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	serv_addr = (sys.argv[1], PORT)

	get_file(s, serv_addr, sys.argv[2])
