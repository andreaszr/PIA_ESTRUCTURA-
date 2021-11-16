from collections import namedtuple
import csv
import time
from os import read 
import sys
import sqlite3
from sqlite3 import Error
import datetime
import time

Claves = namedtuple("Claves", "folio fecha_venta fecha_actual")
Detalles = namedtuple("Detalles", "descripcion cantidad precio")
separador = "*" * 80

try:
    with sqlite3.connect("VentasPIA.db") as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS Claves (folio_venta INTEGER PRIMARY KEY, fecha_venta TEXT NOT NULL, fecha_actual TEXT NOT NULL);")
        cursor.execute("CREATE TABLE IF NOT EXISTS Detalles (folio_venta INTEGER, descripcion TEXT NOT NULL, cantidad INTEGER NOT NULL, precio REAL NOT NULL, FOREIGN KEY(folio_venta) REFERENCES Claves(folio_venta));")
except Error as e:
    print(e)
except Exception:
    print(f"Ha ocurrido un problema: {sys.exc_info()[0]}")
else: 
    print("Se realizo la conexion")
    
time.sleep(1)
while True:
    print(separador)
    print("Menú principal")
    print("1- Registrar una venta.")
    print("2- Consultar ventas de un día específico")
    print("3- Salir")
    
    print(separador)
    opcion_usuario = int(input("Escribe la opcion que desea realizar: "))
    print(separador)
    
    if opcion_usuario == 1:
        folio = int(input("Ingrese el folio: "))
        while True:
            try:
                with sqlite3.connect("VentasPIA.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT folio_venta FROM Claves WHERE folio_venta = {folio}")
                    validacion_folio = cursor.fetchall()
                    if validacion_folio:
                        print("Este folio ya se encuentra registrado")
                        input("Presione ENTER para continuar ")
                        break
                    
                    else:
                        while True:
                            fecha_actual = datetime.date.today()
                            fecha_venta = input("Ingresa la fecha de la venta(YYYY-MM-DD): \n")
                            fecha_venta_procesada = datetime.datetime.strptime(fecha_venta,"%Y-%m-%d").date()  
                            if fecha_venta_procesada <= fecha_actual:
                                print(separador)
                                break
                            else:
                                print("Esta fecha no es valida, favor de ingresar una fecha adecuada")
                                print(separador)
                    articulos = []
                    clave_venta = Claves(folio, fecha_venta, fecha_actual)
                    while True:
                        while True:
                            descripcion = input("Descipcion del articulo: ")
                            if len(descripcion) != 0 and descripcion.strip() != '':
                                break
                            else:
                                print("La descripcion ingresada no es valida, favor de ingresarla nuevamente")
                                input("Presione ENTER para continuar")

                        while True:
                            cantidad = int(input("Cantidad de piezas vendidas: "))
                            if cantidad > 0:
                                break
                            else:
                                print("Favor de ingresar una cantidad mayor a 0")
                                input("Presione ENTER para continuar")

                        while True:
                            precio = float(input("Precio del articulo: "))
                            if precio > 0:
                                break
                            else:
                                print("Favor de ingresar un precio valido para el articulo")
                                input("Presione ENTER para continuar")
                            
                        articulo_en_turno = Detalles(descripcion, cantidad, precio)
                        articulos.append(articulo_en_turno)

                        continuar_ticket = int(input("¿Seguir registrando ventas? Si=1, No=0: "))
                        if continuar_ticket == 1:
                            continue
                        elif continuar_ticket == 0:
                            total = 0
                            cursor.execute(f"INSERT INTO Claves VALUES(?,?,?)", (clave_venta.folio, clave_venta.fecha_venta, clave_venta.fecha_actual))

                            for articulo in articulos:
                                total_articulo = articulo.cantidad * articulo.precio
                                total = total + total_articulo
                                cursor.execute(f"INSERT INTO Detalles VALUES(?,?,?,?)", (clave_venta.folio, articulo.descripcion, articulo.cantidad, articulo.precio))
                    
                            print(f"El total a pagar es de: {total}")
                            input("Presione ENTER para continuar")
                            break
            except Error as e:
                print(e)
            except Exception:
                print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
            finally:
                if conn:
                    conn.close()
                    break

    elif opcion_usuario == 2:
        try:
            with sqlite3.connect("VentasPIA.db") as conn: 
                cursor = conn.cursor()
                while True:
                    fecha_actual = datetime.date.today()
                    fecha_a_consultar = input("Ingresa la fecha de las ventas a consultar(YYYY-MM-DD): \n")
                    dic_fecha_consulta = {'fecha': fecha_a_consultar }
                    cursor.execute("SELECT * FROM Claves WHERE fecha_venta = :fecha", dic_fecha_consulta)
                    ventas_fecha_consultar = cursor.fetchall() 
                    fecha_a_consultar_procesada = datetime.datetime.strptime(fecha_a_consultar,"%Y-%m-%d").date()  
                    if fecha_a_consultar_procesada <= fecha_actual:
                        if ventas_fecha_consultar:
                            print(separador)              
                            break
                        else:
                            print("No hay ventas en la fecha ingresada")
                            input("Presione ENTER para continuar")
                            print(separador)
                    else:
                        print("La fecha ingresada no es valida, favor de ingresar una fecha adecuada")
                        input("Presione ENTER para continuar")
                        print(separador)
                
                cursor.execute(f"""
                                SELECT Claves.folio_venta, Claves.fecha_venta, \
                                Detalles.descripcion, Detalles.cantidad, Detalles.precio \
                                FROM Claves \
                                INNER JOIN Detalles \
                                ON Claves.folio_venta = Detalles.folio_venta\
                                WHERE Claves.fecha_venta = :fecha """, dic_fecha_consulta)
                
                ventas_por_fecha = cursor.fetchall() 
                print(separador)
                total_ventas_fecha_consultar = 0
                for folio_venta, fecha_venta, fecha_actual in ventas_fecha_consultar: 
                    articulos_fecha = []
                    for detalle_folio, detalle_fecha, descripcion, cantidad, precio in ventas_por_fecha: 
                        if folio_venta == detalle_folio:
                            total = 0
                            articulo_en_turno = Detalles(descripcion, cantidad, precio)
                            articulos_fecha.append(articulo_en_turno)

                    print(f"El Folio de la venta es: {folio_venta}")
                    print(f"La Fecha de la venta es: {fecha_venta}")
                    print(f'\n{"Cantidad":<5} | {"Descripcion":<17} | {"Precio venta":<16} | {"Total":<20} \n')
                    for articulo in articulos_fecha:
                        print(f"{articulo.cantidad:<8} | {articulo.descripcion:<17} | ${articulo.precio:<15,.2f} | ${(articulo.cantidad) * (articulo.precio):,.2f}")
                        total_por_articulo = articulo.cantidad * articulo.precio
                        total = total + total_por_articulo
                    print('_' * 60)
                    print(f'Total de la venta: ${total:,.2f}\n')
                    print(separador)
                    total_ventas_fecha_consultar = total_ventas_fecha_consultar + total
                else:
                    print(f"El total de ventas en la fecha indicada es: {total_ventas_fecha_consultar}")  
                    input("Presione ENTER para continuar")
                           
                    
        except Exception:
            print(f"Ha ocurrido un problema: {sys.exc_info()[0]}")

    elif opcion_usuario == 3:
        confirmar_salida = int(input("¿Esta seguro de que desea salir? (1=Si, 0=No)"))
        if confirmar_salida == 1:
            break
    else:
        print("Ingresa una opcion valida")
        input("Presione ENTER para continuar")