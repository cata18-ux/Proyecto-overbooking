import sys
sys.path.append("src")
from mdp import *

def test_probabilidades_suman_uno():
    for dia in range(DIAS):
        assert abs(sum(prob_solicitud(dia)) - 1) < 1e-9

def test_cancelaciones_suman_uno():
    total = sum(p for p, t, w in distribucion_cancelaciones(7, 5))
    assert abs(total - 1) < 1e-9

def test_episodio_termina():
    estado = estado_inicial()
    terminado = False
    pasos = 0
    while not terminado:
        estado, recompensa, terminado = paso(estado, ACEPTAR)
        pasos += 1
    assert pasos == DIAS