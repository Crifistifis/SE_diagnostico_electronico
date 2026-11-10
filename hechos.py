from experta import Fact


class Dispositivo(Fact):
    """tipo: celular | tablet | laptop | pc"""


class Sintoma(Fact):
    """nombre: identificador del síntoma, p. ej. 'no_enciende'"""


class Hallazgo(Fact):
    """Diagnóstico generado: regla, falla, solucion, confianza, porque, urgente"""
