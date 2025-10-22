import socket
import csv
import json
import os
import threading

ARCHIVO_CSV = '../calificaciones.csv'
NRC_HOST = 'localhost'
NRC_PORT = 12346
def inicializar_csv():
    if not os.path.exists(ARCHIVO_CSV):
        with open(ARCHIVO_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID_Estudiante', 'Nombre', 'Materia', 'Calificacion'])

def consultar_nrc(nrc):
    try:
        nrc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        nrc_socket.connect((NRC_HOST, NRC_PORT))
        
        comando = f"BUSCAR_NRC|{nrc}" 
        nrc_socket.send(comando.encode('utf-8'))
        
        respuesta_raw = nrc_socket.recv(1024).decode('utf-8')
        respuesta_json = json.loads(respuesta_raw)
        
        nrc_socket.close()
        
        return respuesta_json
        
    except socket.error as e:
        print(f"[ERROR_CONSULTA_NRC] No se pudo conectar a {NRC_HOST}:{NRC_PORT}. {e}")
        return {"status": "error", "mensaje": "Error interno: El servicio de validación de NRC no está disponible."}
    except Exception as e:
        print(f"[ERROR_CONSULTA_NRC] {e}")
        return {"status": "error", "mensaje": str(e)}
    
def agregar_calificacion(id_est, nombre, materia, calif):
 
    print(f"Validando NRC: {materia}...")
    res_nrc = consultar_nrc(materia)
    
    if res_nrc.get('status') != 'ok':
        print(f"Validación fallida: {res_nrc.get('mensaje')}")
        return {"status": "error_nrc", "mensaje": f"Materia/NRC no válida. ({res_nrc.get('mensaje')})"}
    
    print(f"Validación exitosa: {res_nrc['data']}")
   

    try:
        with open(ARCHIVO_CSV, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([id_est, nombre, materia, calif])
        return {"status": "ok", "mensaje": f"Calificación agregada para {nombre} en {materia}"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

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

def actualizar_calificacion(id_est, nueva_materia, nueva_calif):
   
    
    print(f"Validando NUEVO NRC: {nueva_materia}...")
    res_nrc = consultar_nrc(nueva_materia)
    
    if res_nrc.get('status') != 'ok':
        print(f"Validación fallida: {res_nrc.get('mensaje')}")
        return {"status": "error_nrc", "mensaje": f"Materia/NRC nueva no válida. ({res_nrc.get('mensaje')})"}
    
    print(f"Validación exitosa: {res_nrc['data']}")


    try:
        rows = []
        found = False
        
        with open(ARCHIVO_CSV, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID_Estudiante'] == id_est:
                 
                    row['Materia'] = nueva_materia
                    row['Calificacion'] = nueva_calif
         
                    found = True
                rows.append(row)
        
        if not found:
            return {"status": "not_found", "mensaje": "ID no encontrado"}

        with open(ARCHIVO_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['ID_Estudiante', 'Nombre', 'Materia', 'Calificacion'])
            writer.writeheader()
            writer.writerows(rows)
            
        return {"status": "ok", "mensaje": f"Calificación y Materia actualizadas a {nueva_calif} / {nueva_materia}"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def listar_todas():
    """Lee y retorna todas las filas (sin cambios)."""
    try:
        with open(ARCHIVO_CSV, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            return {"status": "ok", "data": data}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def eliminar_por_id(id_est):
    """Elimina una fila por ID (sin cambios)."""
    try:
        rows = []
        found = False
        with open(ARCHIVO_CSV, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID_Estudiante'] != id_est:
                    rows.append(row)
                else:
                    found = True
        
        if not found:
            return {"status": "not_found", "mensaje": "ID no encontrado"}
        
        with open(ARCHIVO_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['ID_Estudiante', 'Nombre', 'Materia', 'Calificacion'])
            writer.writeheader()
            writer.writerows(rows)
            
        return {"status": "ok", "mensaje": f"Registro eliminado para ID {id_est}"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}

def procesar_comando(comando):
    partes = comando.strip().split('|')
    op = partes[0]

    if op == 'AGREGAR' and len(partes) == 5:
        return agregar_calificacion(partes[1], partes[2], partes[3], partes[4])
    
    elif op == 'BUSCAR' and len(partes) == 2:
        return buscar_por_id(partes[1])
    
    elif op == 'ACTUALIZAR' and len(partes) == 4: 
        return actualizar_calificacion(partes[1], partes[2], partes[3])
    
    elif op == 'LISTAR':
        return listar_todas()
    
    elif op == 'ELIMINAR' and len(partes) == 2:
        return eliminar_por_id(partes[1])
        
    else:
        return {"status": "error", "mensaje": f"Comando inválido o número incorrecto de argumentos: {comando}"}

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
server_socket.listen(5) 
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
