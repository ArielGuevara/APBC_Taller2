import socket
import json

def mostrar_menu():
    print("\n--- Menú de Calificaciones (Cliente Concurrente) ---")
    print("1. Agregar calificación")
    print("2. Buscar por ID")
    print("3. Actualizar calificación (y materia)")
    print("4. Listar todas")
    print("5. Eliminar por ID")
    print("6. Salir")
    return input("Elija opción: ")

def enviar_comando(comando):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', 12345))
        client_socket.send(comando.encode('utf-8')) 
        respuesta_raw = client_socket.recv(1024).decode('utf-8') 
        return json.loads(respuesta_raw)
    except Exception as e:
        print(f"[ERROR_CLIENTE] No se pudo conectar al servidor: {e}")
        return {"status": "error_conexion", "mensaje": "No se pudo conectar al servidor de calificaciones."}
    finally:
        client_socket.close()


while True:
    opcion = mostrar_menu()

    if opcion == '1':
        id_est = input("ID: ")
        nombre = input("Nombre: ")
        materia = input("Materia (NRC): ") 
        calif = input("Calificación: ")
        res = enviar_comando(f"AGREGAR|{id_est}|{nombre}|{materia}|{calif}")
        print(f"Respuesta: {res.get('mensaje', 'Error desconocido')}")

    elif opcion == '2':
        id_est = input("ID: ")
        res = enviar_comando(f"BUSCAR|{id_est}")
        if res.get('status') == 'ok':
            print("--- Resultado ---")
            print(res.get('data'))
        else:
            print(f"Respuesta: {res.get('mensaje', 'Error desconocido')}")


    elif opcion == '3':
        id_est = input("ID del estudiante a actualizar: ")
        nueva_materia = input("Nueva Materia (NRC): ")
        nueva_calif = input("Nueva calificación: ")
        
        res = enviar_comando(f"ACTUALIZAR|{id_est}|{nueva_materia}|{nueva_calif}")
        print(f"Respuesta: {res.get('mensaje', 'Error desconocido')}")


    elif opcion == '4':
        res = enviar_comando("LISTAR")
        if res.get('status') == 'ok':
            print("--- Listado de Calificaciones ---")
            data = res.get('data', [])
            if not data:
                print("(No hay calificaciones registradas)")
            for row in data:
                print(row)
        else:
            print(f"Respuesta: {res.get('mensaje', 'Error desconocido')}")

    elif opcion == '5':
        id_est = input("ID a eliminar: ")
        res = enviar_comando(f"ELIMINAR|{id_est}")
        print(f"Respuesta: {res.get('mensaje', 'Error desconocido')}")

    elif opcion == '6':
        print("Saliendo...")
        break

    else:
        print("Opción inválida.")