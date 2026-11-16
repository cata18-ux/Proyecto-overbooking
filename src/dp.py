from mdp import *

def programacion_dinamica():
    valor = {}
    politica = {}

    valor[DIAS] = {}  #ultimo dia, solo queda la recompensa final
    for n_bajas in range(MAX_RESERVAS + 1):
        for n_altas in range(MAX_RESERVAS + 1 - n_bajas):
            valor[DIAS][(n_bajas, n_altas)] = recompensa_final_esperada(n_bajas, n_altas)

    for dia in range(DIAS - 1, -1, -1):  #dias anteriores, de atras hacia adelante
        valor_al_decidir = {}  #valor de quedar con (n_bajas, n_altas) despues de decidir, promediando con las cancelaciones del dia
        for (n_bajas, n_altas) in valor[dia + 1]:
            suma = 0
            for prob, bajas_restantes, altas_restantes in distribucion_cancelaciones(n_bajas, n_altas):
                suma += prob * valor[dia + 1][(bajas_restantes, altas_restantes)]
            valor_al_decidir[(n_bajas, n_altas)] = suma

        valor[dia] = {}  #elige la mejor accion para cada estado y solicitud
        for (n_bajas, n_altas) in valor_al_decidir:
            valor_del_dia = 0
            for solicitud in [NINGUNA, BAJA, ALTA]:
                mejor_valor = None
                mejor_accion = RECHAZAR
                for accion in [RECHAZAR, ACEPTAR]:
                    bajas, altas = reservas_al_decidir(n_bajas, n_altas, solicitud, accion)
                    valor_accion = valor_al_decidir[(bajas, altas)]
                    if mejor_valor is None or valor_accion > mejor_valor:
                        mejor_valor = valor_accion
                        mejor_accion = accion
                politica[(dia, n_bajas, n_altas, solicitud)] = mejor_accion
                valor_del_dia += prob_solicitud(dia)[solicitud] * mejor_valor
            valor[dia][(n_bajas, n_altas)] =valor_del_dia
    
    return valor, politica

def simular_politica(politica, episodios):  #ejecuta episodios siguiendo la politica y retorna recompensa promedio
    total = 0
    for t in range(episodios):
        estado = estado_inicial()
        terminado = False
        while not terminado:
            accion = politica[estado]
            estado, recompensa, terminado = paso(estado, accion)
            total += recompensa
    return total/episodios

if __name__ == "__main__":
    valor, politica = programacion_dinamica()
    print("Valor esperado optimo: ", round(valor[0][(0, 0)], 2))
    print("\n Politica ante una solicitud baja")
    print("Cada letra es un n_bajas de 0 a", MAX_RESERVAS, "(A = aceptar y R = rechazar)")
    
    for dia in [0, 10, 20, 29]:
        letras = ""
        for n_bajas in range(MAX_RESERVAS + 1):
            accion = politica[(dia, n_bajas, 0, BAJA)]
            letras += "A" if accion == ACEPTAR else "R"
        print("dia", dia, ":", letras)
    promedio = simular_politica(politica, 5000)
    print("\n Promedio simulando la politica optima (5000 episodios): ", round(promedio, 2))
    
    

