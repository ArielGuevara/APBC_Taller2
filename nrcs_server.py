import socket
import csv
import json
import os

ARCHIVO_NRCS = 'nrcs.csv'
HOST = 'localhost'
PORT = 12346 

def inicializar_nrcs_csv():
    if not os.path.exists(ARCHIVO_NRCS):
        with open(ARCHIVO_NRCS, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['NRC', 'Materia'])
            writer.writerow(['MAT101', 'Calculo Vectorial'])
            writer.writerow(['PROG202', 'Aplicaciones Distribuidas'])
            writer.writerow(['FIS303', 'Fisica de Ondas'])
            # ---------------------
        print(f"Archivo {ARCHIVO_NRCS} creado con datos de ejemplo.")

def buscar_nrc(nrc_buscado):
    try:
        with open(ARCHIVO_NRCS, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['NRC'] == nrc_buscado:
                    # Encontrado
                    return {"status": "ok", "data": row}
            # No encontrado
            return {"status": "not_found", "mensaje": f"NRC {nrc_buscado} no existe"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def listar_nrcs():
    try:
        with open(ARCHIVO_NRCS, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            return {"status": "ok", "data": data}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def procesar_comando_nrc(comando):
    partes = comando.strip().split('|')
    op = partes[0]

    if op == 'BUSCAR_NRC' and len(partes) == 2:
        return buscar_nrc(partes[1])
    elif op == 'LISTAR_NRCS':
        return listar_nrcs()
    else:
        return {"status": "error", "mensaje": "Comando NRC inválido"}


inicializar_nrcs_csv()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"Servidor de NRCs escuchando en {HOST}:{PORT}...")

try:
    while True:
        client_socket, addr = server_socket.accept()
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                respuesta = procesar_comando_nrc(data)
                client_socket.send(json.dumps(respuesta).encode('utf-8'))
        except Exception as e:
            print(f"Error procesando solicitud NRC: {e}")
        finally:
            client_socket.close()
except KeyboardInterrupt:
    print("\nServidor de NRCs detenido.")
finally:
    server_socket.close()
