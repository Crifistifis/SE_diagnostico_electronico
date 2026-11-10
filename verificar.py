"""
Revisa que el catálogo (catalogo.py) y las reglas (reglas.py) sean coherentes.
Ejecútalo después de cambiar cualquiera de los dos:  python verificar.py
"""
import re
from collections import Counter

from catalogo import CATEGORIAS, SINTOMAS, SINTOMAS_POR_ID

with open("reglas.py", encoding="utf-8") as f:
    fuente = f.read()

errores, avisos = [], []

usados = set(re.findall(r'\bS\("([a-z_]+)"\)', fuente))
ids_reglas = re.findall(r'self\.hallazgo\(\s*"(R\d+)"', fuente)
ids_catalogo = set(SINTOMAS_POR_ID)

# 1. Las reglas solo usan síntomas que existen en el catálogo
for sid in sorted(usados - ids_catalogo):
    errores.append(f"reglas.py usa el síntoma '{sid}', que no existe en catalogo.py")

# 2. Todo síntoma del catálogo sirve para alguna regla
for sid in sorted(ids_catalogo - usados):
    avisos.append(f"el síntoma '{sid}' se pregunta, pero ninguna regla lo usa")

# 3. Los seguimientos existen y todo síntoma no principal es alcanzable
alcanzables = set()
for s in SINTOMAS:
    if s["categoria"] not in CATEGORIAS:
        errores.append(f"'{s['id']}' tiene una categoría desconocida: {s['categoria']}")
    for hijo in s["seguimiento"]:
        if hijo not in ids_catalogo:
            errores.append(f"'{s['id']}' tiene un seguimiento inexistente: '{hijo}'")
        else:
            alcanzables.add(hijo)
for s in SINTOMAS:
    if not s["raiz"] and s["id"] not in alcanzables:
        errores.append(f"'{s['id']}' no es principal ni seguimiento de nadie: nunca se preguntaría")

# 4. Ids de regla únicos
for rid, veces in Counter(ids_reglas).items():
    if veces > 1:
        errores.append(f"el id de regla {rid} está repetido")

print(f"{len(SINTOMAS)} síntomas, {len(ids_reglas)} reglas.")
for a in avisos:
    print("AVISO :", a)
for e in errores:
    print("ERROR :", e)
if not errores and not avisos:
    print("Todo coherente.")
