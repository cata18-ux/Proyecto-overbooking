import random
from math import comb

DIAS = 30  #dias de venta antes de la noche
CAPACIDAD = 10  #habitaciones disponibles
OVERBOOKING = 5  #reservas extra 
MAX_RESERVAS = CAPACIDAD + OVERBOOKING

PRECIO_BAJO = 100
PRECIO_ALTO = 200
COSTO_COMPENSACION = 300  #costo si un huesped se queda sin habitacion

PROB_CANCELAR = 0.02  #probabilidad de que una reserva se cancele cada dia 
PROB_APARECER = 0.9  #probabilidad de que un huesped si llegue

NINGUNA, BAJA, ALTA = 0, 1, 2
RECHAZAR, ACEPTAR = 0, 1

def prob_solicitud(dia):  #retorna la probababilidad de ese dia
    avance = dia / DIAS
    prob_alta = 0.05 + 0.25 * avance
    prob_baja = 0.40 - 0.20 * avance
    prob_ninguna = 1 - prob_alta - prob_baja
    return [prob_ninguna, prob_baja, prob_alta]

def prob_binomial(n, k, p): #probabilidad de que k en n eventos ocurran, cada uno con probabilidad p
    return comb(n, k) * p**k * (1 - p) ** (n - k)

def reservas_al_decidir(n_bajas, n_altas, solicitud, accion):  #reservas que se mantienen despues de aceptar o rechazar la solicitud
    if accion == ACEPTAR and n_bajas + n_altas < MAX_RESERVAS:
        if solicitud == BAJA:
            n_bajas += 1
        elif solicitud == ALTA:
            n_altas +=1
    return n_bajas, n_altas

def distribucion_cancelaciones(n_bajas, n_altas):  #lista probabilidades
    resultados = []
    for cancelacion_baja in range(n_bajas + 1):
        p_bajas = prob_binomial(n_bajas, cancelacion_baja, PROB_CANCELAR)
        for cancelacion_alta in range(n_altas + 1):
            p_altas = prob_binomial(n_altas, cancelacion_alta, PROB_CANCELAR)
            resultados.append((p_bajas * p_altas, n_bajas - cancelacion_baja, n_altas - cancelacion_alta))
    return resultados

def recompensa_final(llegadas_bajas, llegadas_altas):  #recompensa de cuantos huespedes llegan, las tarifas altas tienen mas prioridad
    altas_con_habitacion = min(llegadas_altas, CAPACIDAD)
    bajas_con_habitacion = min(llegadas_bajas, CAPACIDAD - altas_con_habitacion)
    ingreso = PRECIO_ALTO * altas_con_habitacion + PRECIO_BAJO * bajas_con_habitacion
    sin_habitacion = llegadas_bajas + llegadas_altas - altas_con_habitacion - bajas_con_habitacion
    return ingreso - COSTO_COMPENSACION * sin_habitacion

def recompensa_final_esperada(n_bajas, n_altas):  #recompensa promedio de quien llega y quien no
    total = 0
    for llegadas_bajas in range(n_bajas + 1):
        p_bajas = prob_binomial(n_bajas, llegadas_bajas, PROB_APARECER)
        for llegadas_altas in range(n_altas + 1):
            p_altas = prob_binomial(n_altas, llegadas_altas, PROB_APARECER)
            total += p_bajas * p_altas * recompensa_final(llegadas_bajas, llegadas_altas)
    return total

#simulacion para monte carlo
def contar_exitos(n, p):  #cuantos n eventos ocurren con probabilidad p 
    return sum(1 for t in range(n) if random.random() < p)

def sortear_solicitud(dia):
    return random.choices([NINGUNA, BAJA, ALTA], weights=prob_solicitud(dia))[0]

def estado_inicial():  #estado = (dia, n_bajas, n_altas, solicitud)
    return(0, 0, 0, sortear_solicitud(0))

def paso(estado, accion):  #simula un dia, retorna (nuevo_estado, recompensa, terminado)
    dia, n_bajas, n_altas, solicitud = estado
    n_bajas, n_altas = reservas_al_decidir(n_bajas, n_altas, solicitud, accion)
    n_bajas -= contar_exitos(n_bajas, PROB_CANCELAR)
    n_altas -= contar_exitos(n_altas, PROB_CANCELAR)
    dia += 1
    if dia == DIAS:
        llegadas_bajas = contar_exitos(n_bajas, PROB_APARECER)
        llegadas_altas = contar_exitos(n_altas, PROB_APARECER)
        recompensa = recompensa_final(llegadas_bajas, llegadas_altas)
        return(dia, n_bajas, n_altas, NINGUNA), recompensa, True
    return(dia, n_bajas, n_altas, sortear_solicitud(dia)), 0, False

