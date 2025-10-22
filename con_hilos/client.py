import socket
import json
def mostrar_menu():
    print("\n--- Men de Calificaciones ---")
    print("1. Agregar calificacin")
    print("2. Buscar por ID")
    print("3. Actualizar calificacin")
    print("4. Listar todas")
    print("5. Eliminar por ID")
    print("6. Salir")
    return input("Elija opcin: ")
def enviar_comando(comando):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))
    client_socket.send(comando.encode('utf-8'))
    respuesta = client_socket.recv(1024).decode('utf-8')
    client_socket.close()
    return json.loads(respuesta)

while True:
    opcion = mostrar_menu()
    if opcion == '1':
        id_est = input("ID: ")
        nombre = input("Nombre: ")
        materia = input("Materia: ")
        calif = input("Calificacin: ")
        res = enviar_comando(f"AGREGAR|{id_est}|{nombre}|{materia}|{calif}")
        print(res["mensaje"])
    elif opcion == '2':
        id_est = input("ID: ")
        res = enviar_comando(f"BUSCAR|{id_est}")
        if res["status"] == "ok":
            print("fNombre: {res['data']['Nombre']}, Materia: {res['data']['Materia']}, Calificacin: {res['data']['Calificacin']}")
            print(res["mensaje"])
    elif opcion == '3':
        id_est = input("ID: ")
        nueva_calif = input("Nueva calificacin: ")
        res = enviar_comando(f"ACTUALIZAR|{id_est}|{nueva_calif}")
        print(res["mensaje"])
    elif opcion == '4':
        res = enviar_comando(f"LISTAR")
        if res["status"] == "ok":
            for row in res["data"]:
                print(row)
        else:
            print(res["mensaje"])
    elif opcion == '5':
        id_est = input("ID: ")
        res = enviar_comando(f"ELIMINAR|{id_est}")
        print(res["mensaje"])
    elif opcion == '6':
        break
    else:
        print("Opcin invlida")