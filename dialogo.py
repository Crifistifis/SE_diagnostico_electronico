"""
Lógica de la consulta (sin interfaz gráfica):
  - detectar síntomas a partir de texto libre,
  - decidir qué pregunta de seguimiento sigue,
  - lanzar el motor de inferencia con los hechos reunidos.
"""
import re

from catalogo import SINTOMAS_POR_ID, normalizar, sintomas_de

# «no», «sin», «nunca»... justo antes de una palabra clave => el síntoma se niega
_NEGACION = re.compile(r"\b(no|nunca|ni|sin|tampoco)\s+(?:\w+\s+)?$")


def detectar_sintomas(texto, tipo):
    """Devuelve los ids de síntomas que se mencionan en el texto libre.

    Es una detección sencilla por palabras clave: no entiende frases complejas,
    por eso la interfaz deja al usuario revisar y corregir lo detectado.
    """
    t = normalizar(texto)
    encontrados = []
    for s in sintomas_de(tipo):
        for palabra in s["palabras"]:
            inicio = 0
            while True:
                i = t.find(palabra, inicio)
                if i == -1:
                    break
                if not _NEGACION.search(t[max(0, i - 15):i]):
                    encontrados.append(s["id"])
                    break
                inicio = i + 1
            if s["id"] in encontrados:
                break
    return encontrados


class Consulta:
    """Estado de una consulta: qué se sabe y qué falta por preguntar."""

    def __init__(self, tipo, sintomas_iniciales):
        self.tipo = tipo
        self.conocidos = {}      # id -> True (sí) / False (no) / None (no sé)
        self.cola = []           # ids pendientes de preguntar
        self.actual = None       # síntoma que se está preguntando ahora
        self.hechas = 0          # preguntas ya respondidas

        for sid in sintomas_iniciales:
            self.conocidos[sid] = True
        for sid in sintomas_iniciales:
            self._encolar_seguimiento(sid)
        self._siguiente()

    # ---------- flujo de preguntas ----------
    def _encolar_seguimiento(self, sid):
        for hijo in SINTOMAS_POR_ID[sid]["seguimiento"]:
            h = SINTOMAS_POR_ID[hijo]
            if (self.tipo in h["dispositivos"]
                    and hijo not in self.conocidos
                    and hijo not in self.cola):
                self.cola.append(hijo)

    def _siguiente(self):
        self.actual = None
        while self.cola:
            sid = self.cola.pop(0)
            if sid not in self.conocidos:
                self.actual = SINTOMAS_POR_ID[sid]
                return

    def terminada(self):
        return self.actual is None

    def responder(self, respuesta):
        """respuesta: 'si', 'no' o 'no_se'."""
        sid = self.actual["id"]
        if respuesta == "si":
            self.conocidos[sid] = True
            self._encolar_seguimiento(sid)
        elif respuesta == "no":
            self.conocidos[sid] = False
        else:
            self.conocidos[sid] = None
        self.hechas += 1
        self._siguiente()

    def presentes(self):
        return [sid for sid, valor in self.conocidos.items() if valor is True]

    # ---------- inferencia ----------
    def diagnosticar(self):
        """Carga los hechos en el motor Experta y devuelve los diagnósticos."""
        from experta import Fact  # noqa: F401  (falla aquí si no está instalado)
        from hechos import Dispositivo, Sintoma, Hallazgo
        from reglas import Diagnostico

        motor = Diagnostico()
        motor.reset()
        motor.declare(Dispositivo(tipo=self.tipo))
        for sid in self.presentes():
            motor.declare(Sintoma(nombre=sid))
        motor.run()

        resultados = [f for f in motor.facts.values() if isinstance(f, Hallazgo)]
        resultados.sort(key=lambda h: h["confianza"], reverse=True)
        return [
            {
                "regla": h["regla"],
                "falla": h["falla"],
                "solucion": h["solucion"],
                "confianza": h["confianza"],
                "porque": h["porque"],
                "urgente": h["urgente"],
            }
            for h in resultados
        ]
