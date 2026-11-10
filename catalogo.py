"""
Catálogo de síntomas.

Aquí vive el conocimiento sobre QUÉ se le puede preguntar al usuario:
  - qué síntomas existen y para qué dispositivos aplican,
  - cuáles aparecen en la lista principal ("raiz"),
  - qué preguntas de seguimiento se hacen cuando un síntoma está presente,
  - con qué palabras puede describirlo el usuario con sus propias palabras.

Las reglas de diagnóstico están aparte, en reglas.py.
"""
import re
import unicodedata

TODOS = ("celular", "tablet", "laptop", "pc")
PORTATIL = ("celular", "tablet", "laptop")
MOVIL = ("celular", "tablet")
CON_VENTILADOR = ("laptop", "pc")

DISPOSITIVOS = {
    "celular": "Celular",
    "tablet": "Tablet",
    "laptop": "Laptop",
    "pc": "PC de escritorio",
}

CATEGORIAS = [
    "Energía", "Batería", "Pantalla", "Rendimiento", "Temperatura",
    "Almacenamiento", "Red", "Audio y puertos", "Daño físico",
]


def normalizar(texto):
    """Minúsculas, sin acentos y con espacios limpios (para comparar textos)."""
    t = unicodedata.normalize("NFD", texto.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"wi[\s\-]?fi", "wifi", t)
    return re.sub(r"\s+", " ", t).strip()


def _s(id, categoria, texto, pregunta, dispositivos,
       raiz=False, seguimiento=(), palabras=()):
    return {
        "id": id,
        "categoria": categoria,
        "texto": texto,              # cómo se muestra en la lista
        "pregunta": pregunta,        # cómo se pregunta en la consulta
        "dispositivos": tuple(dispositivos),
        "raiz": raiz,                # True = aparece en la lista principal
        "seguimiento": list(seguimiento),  # qué preguntar si este síntoma está presente
        "palabras": [normalizar(p) for p in palabras],
    }


SINTOMAS = [
    # ───────────── Energía ─────────────
    _s("no_enciende", "Energía", "No enciende",
       "¿El equipo no enciende en absoluto?", TODOS, raiz=True,
       seguimiento=["no_carga", "sin_luces", "tras_golpe_o_agua", "olor_quemado"],
       palabras=["no enciende", "no se enciende", "no prende", "no se prende",
                 "no da señal de vida", "está muerto", "esta muerto"]),
    _s("sin_luces", "Energía", "No se enciende ninguna luz ni ventilador",
       "¿Al presionar encendido no se ve ninguna luz ni se oye el ventilador?",
       CON_VENTILADOR,
       palabras=["sin luces", "ninguna luz", "no hay luces"]),
    _s("olor_quemado", "Energía", "Huele a quemado o sale humo",
       "¿Percibes olor a quemado, o has visto humo o chispas?", TODOS, raiz=True,
       palabras=["huele a quemado", "olor a quemado", "humo", "chispa"]),
    _s("se_apaga_solo", "Energía", "Se apaga solo",
       "¿El equipo se apaga de repente sin que tú lo apagues?", TODOS, raiz=True,
       seguimiento=["sobrecalentamiento", "bateria_dura_poco"],
       palabras=["se apaga solo", "se apaga sola", "se apaga de repente",
                 "se apaga sin avisar", "se reinicia solo", "se reinicia sola"]),
    _s("pitidos", "Energía", "Emite pitidos al encender",
       "¿Emite pitidos al encenderse?", CON_VENTILADOR, raiz=True,
       palabras=["pitidos", "pitido", "beep"]),

    # ───────────── Batería ─────────────
    _s("no_carga", "Batería", "No carga la batería",
       "¿El equipo no carga al conectarlo (o no indica que esté cargando)?",
       PORTATIL, raiz=True, seguimiento=["puerto_flojo"],
       palabras=["no carga", "no esta cargando", "no se carga", "no marca carga"]),
    _s("puerto_flojo", "Batería", "Cable flojo o carga intermitente",
       "¿El cable queda flojo, o solo carga si lo mueves o lo acomodas?", PORTATIL,
       palabras=["cable flojo", "carga intermitente", "carga y descarga",
                 "solo carga si"]),
    _s("bateria_dura_poco", "Batería", "La batería dura muy poco",
       "¿La batería se agota mucho más rápido que antes?", PORTATIL, raiz=True,
       seguimiento=["equipo_antiguo"],
       palabras=["bateria dura poco", "bateria dura muy poco", "dura poco la bateria",
                 "se descarga rapido", "se descarga muy rapido", "bateria se acaba",
                 "no dura la bateria"]),
    _s("equipo_antiguo", "Batería", "Tiene más de 3 años de uso",
       "¿El equipo tiene más de 3 años de uso?", TODOS,
       palabras=["es viejo", "muy viejo", "equipo viejo", "antiguo"]),
    _s("bateria_hinchada", "Batería", "Batería hinchada (tapa o pantalla levantada)",
       "¿Notas la tapa, la pantalla o el trackpad levantados, como si algo se "
       "hinchara por dentro?", PORTATIL, raiz=True,
       palabras=["bateria hinchada", "hinchada", "inflada", "tapa levantada",
                 "pantalla levantada", "se hincho"]),
    _s("se_calienta_cargando", "Batería", "Se calienta mucho al cargar",
       "¿Se calienta de forma excesiva mientras carga?", PORTATIL, raiz=True,
       palabras=["se calienta al cargar", "se calienta cargando", "caliente al cargar",
                 "calienta cuando carga", "se calienta mucho al cargar"]),

    # ───────────── Pantalla ─────────────
    _s("pantalla_negra", "Pantalla", "Pantalla negra",
       "¿La pantalla se ve completamente negra?", TODOS, raiz=True,
       seguimiento=["equipo_responde", "pitidos", "tras_golpe_o_agua"],
       palabras=["pantalla negra", "pantalla en negro", "no da imagen", "sin imagen",
                 "no hay imagen", "no se ve nada"]),
    _s("equipo_responde", "Pantalla", "El equipo parece encendido",
       "¿El equipo parece encendido (luces, ventiladores, sonidos o vibración)?", TODOS,
       palabras=["parece encendido", "se oye el ventilador", "se escucha el ventilador",
                 "vibra"]),
    _s("lineas_pantalla", "Pantalla", "Líneas, manchas o colores raros",
       "¿Ves líneas, manchas o colores extraños en la pantalla?", TODOS, raiz=True,
       seguimiento=["tras_golpe_o_agua"],
       palabras=["lineas", "manchas", "rayas", "colores raros", "parpadea"]),
    _s("tactil_no_responde", "Pantalla", "El táctil no responde",
       "¿La pantalla táctil no responde, o toca cosas sola?", MOVIL, raiz=True,
       seguimiento=["tras_golpe_o_agua"],
       palabras=["tactil", "touch no responde", "no responde al tacto", "toca sola"]),

    # ───────────── Rendimiento ─────────────
    _s("sistema_lento", "Rendimiento", "Está muy lento",
       "¿El equipo va muy lento al abrir programas o aplicaciones?", TODOS, raiz=True,
       seguimiento=["almacenamiento_lleno", "equipo_antiguo", "ruido_disco",
                    "sobrecalentamiento"],
       palabras=["muy lento", "esta lento", "va lento", "lentitud", "tarda mucho",
                 "se arrastra"]),
    _s("se_congela", "Rendimiento", "Se congela o se traba",
       "¿Se congela o se queda trabado por momentos?", TODOS, raiz=True,
       seguimiento=["sobrecalentamiento", "ruido_disco", "almacenamiento_lleno"],
       palabras=["se congela", "se traba", "se cuelga", "se queda pegado"]),
    _s("apps_cierran", "Rendimiento", "Las apps se cierran solas",
       "¿Las aplicaciones se cierran solas?", MOVIL, raiz=True,
       seguimiento=["almacenamiento_lleno"],
       palabras=["apps se cierran", "aplicaciones se cierran", "se cierran las apps",
                 "se cierran las aplicaciones"]),

    # ───────────── Temperatura ─────────────
    _s("sobrecalentamiento", "Temperatura", "Se calienta demasiado",
       "¿Se calienta más de lo normal al usarlo?", TODOS, raiz=True,
       seguimiento=["ventilador_ruidoso", "ventilador_parado", "calienta_en_reposo"],
       palabras=["se calienta", "sobrecalienta", "sobrecalentamiento",
                 "esta muy caliente", "calienta mucho", "hirviendo"]),
    _s("ventilador_ruidoso", "Temperatura", "Ventilador muy ruidoso",
       "¿El ventilador hace mucho ruido o gira a máxima velocidad todo el tiempo?",
       CON_VENTILADOR, raiz=True,
       palabras=["ventilador ruidoso", "ruido del ventilador", "ventilador suena",
                 "ventilador hace ruido", "ventilador a todo"]),
    _s("ventilador_parado", "Temperatura", "El ventilador no gira",
       "¿El ventilador no gira o no se oye funcionando?", CON_VENTILADOR,
       palabras=["ventilador no gira", "ventilador parado", "no gira el ventilador",
                 "ventilador no funciona"]),
    _s("calienta_en_reposo", "Temperatura", "Se calienta aun sin usarlo",
       "¿Se calienta incluso cuando no lo estás usando?", TODOS,
       palabras=["se calienta sin usar", "caliente sin usarlo", "se calienta en reposo",
                 "se calienta aunque no lo use"]),

    # ───────────── Almacenamiento ─────────────
    _s("almacenamiento_lleno", "Almacenamiento", "Almacenamiento casi lleno",
       "¿El almacenamiento está casi lleno (más del 90%)?", TODOS, raiz=True,
       palabras=["memoria llena", "almacenamiento lleno", "disco lleno", "sin espacio",
                 "falta de espacio", "almacenamiento casi lleno"]),
    _s("no_arranca_sistema", "Almacenamiento", "Enciende pero no inicia el sistema",
       "¿Enciende, pero se queda en el logo, muestra un error o se reinicia sin parar?",
       TODOS, raiz=True, seguimiento=["cambio_reciente", "ruido_disco"],
       palabras=["no arranca el sistema", "se queda en el logo", "se queda en la manzana",
                 "no inicia windows", "no carga windows", "no arranca windows",
                 "bucle de reinicio", "bootloop", "reinicio infinito", "pantalla azul"]),
    _s("cambio_reciente", "Almacenamiento", "Pasó tras instalar o actualizar",
       "¿Empezó justo después de una actualización o de instalar algo?", TODOS,
       palabras=["despues de actualizar", "tras actualizar", "despues de instalar",
                 "luego de actualizar", "actualizacion"]),
    _s("ruido_disco", "Almacenamiento", "Clics o golpeteos del disco",
       "¿Se oyen clics, golpeteos o zumbidos raros del disco duro?", CON_VENTILADOR,
       raiz=True,
       palabras=["clic", "click", "golpeteo", "zumbido del disco", "ruido del disco",
                 "disco hace ruido"]),

    # ───────────── Red ─────────────
    _s("sin_wifi", "Red", "No se conecta al Wi-Fi",
       "¿No logra conectarse al Wi-Fi, o no hay internet por Wi-Fi?", TODOS, raiz=True,
       seguimiento=["otros_conectan"],
       palabras=["no se conecta al wifi", "no conecta al wifi", "sin wifi", "no hay wifi",
                 "no tengo wifi", "no tengo internet", "wifi no funciona",
                 "no detecta el wifi", "no encuentra redes", "no tiene internet",
                 "sin internet"]),
    _s("otros_conectan", "Red", "Otros equipos sí se conectan",
       "¿Otros dispositivos sí se conectan sin problema a esa misma red?", TODOS,
       palabras=["otros si se conectan", "otros dispositivos si", "los demas si se conectan"]),
    _s("sin_senal", "Red", "Sin señal móvil o no reconoce la SIM",
       "¿Muestra «sin servicio» o no reconoce la SIM?", MOVIL, raiz=True,
       seguimiento=["sim_falla_otro"],
       palabras=["sin senal", "sin servicio", "no reconoce la sim", "no detecta la sim",
                 "sin sim", "no hay senal", "no tiene senal"]),
    _s("sim_falla_otro", "Red", "La SIM tampoco funciona en otro equipo",
       "¿La SIM también falla al probarla en otro equipo?", MOVIL),

    # ───────────── Audio y puertos ─────────────
    _s("sin_sonido", "Audio y puertos", "Sin sonido",
       "¿No sale sonido por el altavoz?", TODOS, raiz=True,
       seguimiento=["tras_golpe_o_agua"],
       palabras=["sin sonido", "no suena", "no se escucha", "no hay sonido",
                 "altavoz no funciona", "bocina no funciona"]),
    _s("usb_no_funciona", "Audio y puertos", "Puertos USB sin funcionar",
       "¿Los puertos USB no reconocen ningún dispositivo?", CON_VENTILADOR, raiz=True,
       palabras=["usb no funciona", "usb no reconoce", "no reconoce el usb",
                 "no reconoce mi usb", "puertos usb"]),

    # ───────────── Daño físico ─────────────
    _s("tras_golpe_o_agua", "Daño físico", "Sufrió golpe, caída o líquido",
       "¿El equipo sufrió una caída, un golpe o contacto con líquido?", TODOS, raiz=True,
       palabras=["se cayo", "caida", "golpe", "se mojo", "liquido", "derrame",
                 "le cayo agua", "cayo cafe"]),
]

SINTOMAS_POR_ID = {s["id"]: s for s in SINTOMAS}


def sintomas_de(tipo):
    """Todos los síntomas que aplican a un tipo de dispositivo."""
    return [s for s in SINTOMAS if tipo in s["dispositivos"]]


def raices_por_categoria(tipo):
    """[(categoría, [síntomas])] de la lista principal para ese dispositivo."""
    resultado = []
    for cat in CATEGORIAS:
        lista = [s for s in SINTOMAS
                 if s["raiz"] and s["categoria"] == cat and tipo in s["dispositivos"]]
        if lista:
            resultado.append((cat, lista))
    return resultado
