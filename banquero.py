
class Estado:
    def __init__(self, total_recursos, demanda_maxima_procesos,
                recursos_disponibles=None, recursos_asignados=None):
        self.total_recursos = total_recursos
        self.demanda_maxima_procesos = demanda_maxima_procesos
        self.disponibles = recursos_disponibles
        self.asignados = recursos_asignados

        if recursos_disponibles is None or recursos_asignados is None:
            self.disponibles = {}
            self.asignados = {}
            for proceso, recursos in demanda_maxima_procesos.items():
                self.asignados[proceso] = {}
                for recurso in recursos:
                    self.asignados[proceso][recurso] = 0

            self.disponibles = total_recursos.copy()


def es_menor_igual(d1, d2):
    for i in d1:
        if d1[i] > d2[i]:
            return False

    return True

def sumar_diccionarios(d1, d2):
    nuevo = {}
    for i in d1:
        nuevo[i] = d1[i] + d2[i]
    return nuevo

def restar_diccionarios(d1, d2):
    nuevo = {}
    for i in d1:
        nuevo[i] = d1[i] - d2[i]
    return nuevo

def calcular_necesidad(m1, m2):
    """ Calcula la matriz de necesidad. Resta demanda_maxima - asignados """
    nueva = {}
    for i in m1:
        nueva[i] = {}
        for j in m1[i]:
            nueva[i][j] = m1[i][j] - m2[i][j]

    return nueva

def mostrar_estado(estado):
    """ Muestra las matrices """
    necesidad = calcular_necesidad(estado.demanda_maxima_procesos, estado.asignados)
    print("DEMANDA MÁXIMA\t\t\tASIGNADOS\t\t\tNECESITADOS")
    for i in estado.demanda_maxima_procesos:
        for j in estado.demanda_maxima_procesos[i]:
            print(estado.demanda_maxima_procesos[i][j], end="  ")

        print("\t\t\t", end="")
        for j in estado.asignados[i]:
            print(estado.asignados[i][j], end="  ")

        print("\t\t\t", end="")
        for j in necesidad[i]:
            print(necesidad[i][j], end="  ")

        print()

    print("\nDISPONIBLES\t\t\tRECURSOS ORIGINALES")
    for i in estado.disponibles:
        print(estado.disponibles[i], end="  ")

    print("\t\t\t", end="")
    for i in estado.total_recursos:
        print(estado.total_recursos[i], end="  ")
    print("\n")


def es_estado_seguro(estado):
    """ Determina si un estado es seguro. Retorna True de se así o False en caso contrario.
    También retorna la ruta """
    necesidad = calcular_necesidad(estado.demanda_maxima_procesos, estado.asignados)
    disponibles_actual = estado.disponibles.copy()
    resto = [i for i in estado.demanda_maxima_procesos.keys()]
    posible = True

    ruta = []
    while posible:
        encontrado = False
        proceso = None

        # encontrar un procesos al que se le puedan satisfacer sus necesidades
        for i in resto:
            # si la necesidad del proceso se puede satisfacer con los recursos actuales
            if es_menor_igual(necesidad[i], disponibles_actual):
                encontrado = True
                proceso = i
                ruta.append(proceso)
                break

        if encontrado:
            # el proceso devuelve los recursos que tenía asignados
            disponibles_actual = sumar_diccionarios(disponibles_actual, estado.asignados[i])
            resto.remove(proceso)
        else:
            posible = False

    return len(resto) == 0, ruta


# proceso: es el nombre del proceso que hace la solicitud
# solicitud: diccionario con los valores para la solicitud, ejem: {"r1": 2, "r2": 4,...}
def solicitar_recursos(estado, proceso, solicitud):
    # hacer copias
    necesidad = calcular_necesidad(estado.demanda_maxima_procesos, estado.asignados)

    # copias para no modificar a los originales
    recursos_disponibles_copia = estado.disponibles.copy()
    recursos_asignados_copia = estado.asignados.copy()


    if es_menor_igual(solicitud, necesidad[proceso]):
        if es_menor_igual(solicitud, recursos_disponibles_copia):
            recursos_disponibles_copia = restar_diccionarios(recursos_disponibles_copia, solicitud)
            recursos_asignados_copia[proceso] = sumar_diccionarios(recursos_asignados_copia[proceso], solicitud)
            necesidad[proceso] = restar_diccionarios(necesidad[proceso], solicitud)

            aux_estado = Estado(estado.total_recursos, estado.demanda_maxima_procesos,
                    recursos_disponibles_copia, recursos_asignados_copia)

            seguro, ruta = es_estado_seguro(aux_estado)
            if seguro:
                estado.asignados[proceso] = sumar_diccionarios(estado.asignados[proceso], solicitud)
                estado.disponibles = restar_diccionarios(estado.disponibles, solicitud)
                print("Asignados. Estado seguro. Ruta:", str(ruta))

                print()
                mostrar_estado(estado)

                # si el proceso tiene los recursos maximos que solicito tiene que devolverlos
                if estado.asignados[proceso] == estado.demanda_maxima_procesos[proceso]:
                    print("\nProceso: " + proceso + ", consumió sus recursos máximos por lo que los devuelve\n")
                    for i in estado.asignados[proceso]:
                        estado.disponibles[i] += estado.asignados[proceso][i]
                        estado.asignados[proceso][i] = 0
                        estado.demanda_maxima_procesos[proceso][i] = 0

                    mostrar_estado(estado)
                    print("\n-------------------------------------------------------------------------\n")

            else:
                print("ESTADO INSEGURO. No se puede llevar a cabo la asignación")
                #print("Es necesario suspender el proceso")

        else:
            pass
            print("No se puede llevar a cabo la asignación")
            # SUSPENDER AL PROCESO
    else:
        print("ERROR: el proceso excedio la cantidad máxima de recursos que había declarado")




recursos_totales = {}
demanda_maxima = {}


numero_recursos = int(input("Ingresa el numero de recursos: "))
for i in range(numero_recursos):
    recursos_totales["r" + str(i+1)] = int(input("\tTotal de instancias para el recurso r" + str(i+1) + ": "))

numero_procesos = int(input("\nIngresa el numero de procesos: "))

print()
for i in range(numero_procesos):
    proceso = "p" + str(i+1)
    demanda_maxima[proceso] = {}
    for j in range(numero_recursos):
        recurso = "r" + str(j+1)
        necesidad = int(input("\tDemanda maxima para proceso: " + proceso + ", recurso: " + recurso + ": "))
        while necesidad > recursos_totales[recurso]:
            necesidad = int(input("\tERROR: La demanda no puede ser mayor que los recursos totales. Intenta de nuevo: "))
        demanda_maxima[proceso][recurso] = necesidad
    print()


estado = Estado(recursos_totales, demanda_maxima)
mostrar_estado(estado)
print()

print("SOLICITAR RECURSOS")
while True:
    procesos = list(estado.demanda_maxima_procesos.keys())
    proceso = input("Ingresa el nombre del proceso " + str(procesos) + ": ")
    if not proceso in estado.demanda_maxima_procesos.keys():
        print("\tEse proceso no existe")
        continue

    # FALTA VALIDAR QUE EL PROCESO EXISTA

    solicitud = {}
    for recurso in estado.total_recursos.keys():
        solicitud[recurso] = int(input("\tSolicitud para el recurso " + recurso + ": "))

    print()
    solicitar_recursos(estado, proceso, solicitud)

    print("\n")