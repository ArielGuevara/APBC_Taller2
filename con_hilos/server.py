import socket
import csv
import json
import os
import threading

ARCHIVO_CSV = '../calificaciones.csv'

def inicializar_csv():
    if not os.path.exists(ARCHIVO_CSV):
        with open(ARCHIVO_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID_Estudiante', 'Nombre', 'Materia', 'Calificacion'])

def agregar_calificacion(id_est, nombre, materia, calif):
    try:
        with open(ARCHIVO_CSV, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([id_est, nombre, materia, calif])
            return {"status": "ok", "mensaje": f"Calificacin agregada para {nombre}"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def actualizar_calificacion(id_est, nueva_calif):
    try:
        row=[]
        found = False
        with open(ARCHIVO_CSV, 'r') as f:
            reader = csv.DictReader(f)
            for r in reader:
                if r['ID_Estudiante'] == id_est:
                    r['Calificacion'] = nueva_calif
                    found = True
                row.append(r)
        if not found:
            return {"status": "not_found", "mensaje": "ID no encontrado"}
        with open(ARCHIVO_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['ID_Estudiante', 'Nombre', 'Materia', 'Calificacion'])
            writer.writeheader()
            writer.writerows(row)
        return {"status": "ok", "mensaje": f"Calificacin actualizada para ID {id_est}"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def listar_todas():
    try:
        with open(ARCHIVO_CSV, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        return {"status": "ok", "data": data}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def eliminar_por_id(id_est):
    try:
        row = []
        found = False
        with open(ARCHIVO_CSV, 'r') as f:
            reader = csv.DictReader(f)
            for r in reader:
                if r['ID_Estudiante'] == id_est:
                    found = True
                    continue
                row.append(r)
        if not found:
            return {"status": "not_found", "mensaje": "ID no encontrado"}
        with open(ARCHIVO_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['ID_Estudiante', 'Nombre', 'Materia', 'Calificacion'])
            writer.writeheader()
            writer.writerows(row)
        return {"status": "ok", "mensaje": f"Registro eliminado para ID {id_est}"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def procesar_comando(comando):
    partes = comando.strip().split('|')
    op = partes[0]
    if op == "AGREGAR" and len(partes) == 5:
        return agregar_calificacion(partes[1], partes[2], partes[3], partes[4])
    elif op == "BUSCAR" and len(partes) == 2:
        return buscar_por_id(partes[1])
    elif op == "ACTUALIZAR" and len(partes) == 3:
        return actualizar_calificacion(partes[1], partes[2])
    elif op == "LISTAR":
        return listar_todas()
    elif op == "ELIMINAR" and len(partes) == 2:
        return eliminar_por_id(partes[1])
    else:
        return {"status": "error", "mensaje":"Comando invlido"}

def buscar_por_id(id_est):
    try:
        with open(ARCHIVO_CSV, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID_Estudiante'] == id_est:
                    return {"status": "ok", "data": row}
            return {"status": "not_found", "mensaje": "ID no encontrado"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def manejar_cliente(client_socket, addr):
    print(f"Cliente conectado desde {addr} en hilo {threading.current_thread().name}")
    try:
        data = client_socket.recv(1024).decode('utf-8')
        if data:
            respuesta = procesar_comando(data)
            client_socket.send(json.dumps(respuesta).encode('utf-8'))
    except Exception as e:
        print(f"Error en hilo: {e}")
    finally:
        client_socket.close()
        print(f"Cliente {addr} desconectado.")

inicializar_csv()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
server_socket.listen(5) # Cola para mltiples
print("Servidor concurrente escuchando en puerto 12345...")

try:
    while True:
        client_socket, addr = server_socket.accept()
        hilo = threading.Thread(target=manejar_cliente, args=(client_socket, addr))
        hilo.start()
except KeyboardInterrupt:
    print("Servidor detenido.")
finally:
    server_socket.close()
