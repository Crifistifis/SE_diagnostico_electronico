"""
Base de reglas (if-then) y motor de inferencia con Experta.

Cada regla dice: SI el dispositivo es de cierto tipo Y se cumplen ciertos
síntomas, ENTONCES hay una falla probable (con confianza, solución y
explicación de por qué se llegó a ella).
"""
from experta import KnowledgeEngine, Rule, P
from hechos import Dispositivo, Sintoma, Hallazgo

PORTATILES = P(lambda t: t in ("celular", "tablet", "laptop"))
MOVILES = P(lambda t: t in ("celular", "tablet"))
CON_VENTILADOR = P(lambda t: t in ("laptop", "pc"))
SOLO_PC = P(lambda t: t == "pc")
SOLO_LAPTOP = P(lambda t: t == "laptop")


def S(nombre):
    """Atajo para escribir la condición «el síntoma X está presente»."""
    return Sintoma(nombre=nombre)


class Diagnostico(KnowledgeEngine):

    def hallazgo(self, regla, falla, solucion, confianza, porque, urgente=False):
        self.declare(Hallazgo(regla=regla, falla=falla, solucion=solucion,
                              confianza=confianza, porque=porque, urgente=urgente))

    # ═════════════════════════ ENERGÍA ═════════════════════════

    @Rule(S("olor_quemado"))
    def r01_quemado(self):
        self.hallazgo(
            "R01", "Componente quemado o cortocircuito",
            "Apaga y desconecta el equipo de inmediato, retira la batería si es "
            "posible y no lo vuelvas a encender. Llévalo a servicio técnico.",
            0.95, "Reportaste olor a quemado, humo o chispas.", urgente=True)

    @Rule(Dispositivo(tipo=PORTATILES), S("no_enciende"), S("no_carga"))
    def r02_cargador_o_puerto(self):
        self.hallazgo(
            "R02", "Cargador, cable o puerto de carga defectuoso",
            "Prueba con otro cargador y cable (de preferencia originales) y limpia "
            "el puerto con cuidado usando un palillo de madera. Si sigue igual, el "
            "puerto o la batería necesitan revisión.",
            0.80, "No enciende y además no carga.")

    @Rule(Dispositivo(tipo=SOLO_PC), S("no_enciende"), S("sin_luces"))
    def r03_fuente_pc(self):
        self.hallazgo(
            "R03", "Fuente de poder dañada",
            "Revisa el cable de corriente, el interruptor trasero y la toma de "
            "corriente; prueba con otra fuente de poder.",
            0.85, "La PC no enciende y no muestra ninguna luz ni ventilador.")

    @Rule(Dispositivo(tipo=SOLO_LAPTOP), S("no_enciende"), S("sin_luces"))
    def r04_adaptador_laptop(self):
        self.hallazgo(
            "R04", "Adaptador de corriente, batería o placa madre",
            "Prueba con otro adaptador, retira la batería (si es extraíble) y "
            "mantén presionado el botón de encendido 30 segundos. Si no responde, "
            "requiere servicio técnico.",
            0.75, "La laptop no enciende y no muestra ninguna luz ni ventilador.")

    @Rule(S("no_enciende"), S("tras_golpe_o_agua"))
    def r05_dano_interno(self):
        self.hallazgo(
            "R05", "Daño interno por golpe o líquido",
            "No lo conectes ni intentes encenderlo repetidamente. Apágalo, sécalo "
            "si hubo líquido y llévalo a servicio técnico cuanto antes.",
            0.75, "No enciende y sufrió un golpe, caída o contacto con líquido.")

    @Rule(Dispositivo(tipo=CON_VENTILADOR), S("pitidos"), S("pantalla_negra"))
    def r06_ram(self):
        self.hallazgo(
            "R06", "Memoria RAM mal asentada o dañada",
            "Apaga y desconecta, reinserta los módulos de RAM, límpialos con un "
            "borrador suave y pruébalos de uno en uno.",
            0.85, "Emite pitidos al encender y la pantalla queda en negro.")

    @Rule(Dispositivo(tipo=CON_VENTILADOR), S("pitidos"))
    def r07_pitidos(self):
        self.hallazgo(
            "R07", "Falla de hardware detectada al arrancar (RAM, video o placa)",
            "Cuenta los pitidos y consulta el manual del fabricante; reinserta la "
            "RAM y revisa la tarjeta de video.",
            0.65, "Los pitidos al encender indican una falla que el equipo detecta solo.")

    @Rule(S("se_apaga_solo"), S("sobrecalentamiento"))
    def r08_proteccion_termica(self):
        self.hallazgo(
            "R08", "Apagado por protección térmica",
            "Limpia las ventilas y el ventilador (si aplica), usa el equipo sobre "
            "una superficie dura y ventilada y evita dejarlo al sol.",
            0.80, "Se apaga solo y además se calienta demasiado.")

    @Rule(Dispositivo(tipo=PORTATILES), S("se_apaga_solo"), S("bateria_dura_poco"))
    def r09_bateria_no_sostiene(self):
        self.hallazgo(
            "R09", "Batería degradada que ya no sostiene la carga",
            "Pruébalo conectado al cargador: si funciona bien así, la batería es "
            "la causa y conviene reemplazarla.",
            0.80, "Se apaga solo y la batería dura muy poco.")

    # ═════════════════════════ BATERÍA ═════════════════════════

    @Rule(Dispositivo(tipo=PORTATILES), S("bateria_hinchada"))
    def r10_bateria_hinchada(self):
        self.hallazgo(
            "R10", "Batería hinchada (riesgo de incendio)",
            "Deja de usar y de cargar el equipo ya, no lo perfores ni lo presiones "
            "y llévalo a servicio para cambiar la batería. No lo dejes cargando "
            "sin supervisión.",
            0.95, "Una tapa, pantalla o trackpad levantados indican gas dentro de la batería.",
            urgente=True)

    @Rule(Dispositivo(tipo=PORTATILES), S("bateria_dura_poco"), S("equipo_antiguo"))
    def r11_desgaste_bateria(self):
        self.hallazgo(
            "R11", "Desgaste natural de la batería",
            "Revisa el estado de la batería en los ajustes del sistema; si está "
            "por debajo del 80% de su capacidad, conviene reemplazarla.",
            0.85, "La batería dura poco y el equipo tiene más de 3 años.")

    @Rule(Dispositivo(tipo=PORTATILES), S("bateria_dura_poco"))
    def r12_bateria_o_apps(self):
        self.hallazgo(
            "R12", "Batería degradada o apps consumiendo en segundo plano",
            "Revisa qué apps consumen más batería, baja el brillo y activa el "
            "ahorro de energía. Si no mejora, evalúa cambiar la batería.",
            0.50, "La batería se agota mucho más rápido que antes.")

    @Rule(Dispositivo(tipo=PORTATILES), S("no_carga"), S("puerto_flojo"))
    def r13_puerto_desgastado(self):
        self.hallazgo(
            "R13", "Puerto de carga desgastado o sucio",
            "Limpia el puerto con cuidado; si el cable sigue flojo, el conector "
            "está desgastado y debe reemplazarse.",
            0.85, "No carga y el cable queda flojo o carga de forma intermitente.")

    @Rule(Dispositivo(tipo=PORTATILES), S("no_carga"))
    def r14_no_carga(self):
        self.hallazgo(
            "R14", "Cargador, cable o puerto de carga",
            "Prueba otro cargador, otro cable y otra toma de corriente. Reinicia "
            "el equipo.",
            0.50, "El equipo no carga.")

    @Rule(Dispositivo(tipo=PORTATILES), S("se_calienta_cargando"))
    def r15_cargador_defectuoso(self):
        self.hallazgo(
            "R15", "Cargador no original o defectuoso, o batería con falla",
            "Usa un cargador original o certificado y evita cargar con funda "
            "gruesa o usando apps pesadas. Si persiste, haz revisar la batería.",
            0.65, "Se calienta de forma excesiva mientras carga.")

    # ═════════════════════════ PANTALLA ═════════════════════════

    @Rule(Dispositivo(tipo=SOLO_PC), S("pantalla_negra"), S("equipo_responde"))
    def r16_video_pc(self):
        self.hallazgo(
            "R16", "Cable de video, monitor o tarjeta gráfica",
            "Revisa el cable de video en ambos extremos, prueba otro monitor o "
            "cable y, si tienes tarjeta gráfica, reinsértala.",
            0.70, "La PC parece encendida pero no da imagen.")

    @Rule(Dispositivo(tipo=PORTATILES), S("pantalla_negra"), S("equipo_responde"))
    def r17_pantalla_portatil(self):
        self.hallazgo(
            "R17", "Pantalla o cable interno de video dañado",
            "Haz un reinicio forzado y déjalo cargar un rato. En una laptop, "
            "conéctala a un monitor externo: si hay imagen, falla la pantalla o su "
            "cable interno.",
            0.70, "El equipo parece encendido pero la pantalla está negra.")

    @Rule(S("lineas_pantalla"), S("tras_golpe_o_agua"))
    def r18_panel_golpeado(self):
        self.hallazgo(
            "R18", "Panel de pantalla dañado por golpe o líquido",
            "Hay que reemplazar la pantalla; evita seguir usándolo para que el "
            "daño no se extienda.",
            0.90, "Hay líneas o manchas en la pantalla tras un golpe o contacto con líquido.")

    @Rule(S("lineas_pantalla"))
    def r19_lineas(self):
        self.hallazgo(
            "R19", "Panel, cable de video o controlador gráfico",
            "Reinicia y actualiza el sistema o los controladores; en PC o laptop "
            "prueba un monitor externo. Si las líneas persisten, la pantalla o su "
            "cable requieren reemplazo.",
            0.70, "Se ven líneas, manchas o colores extraños en la pantalla.")

    @Rule(Dispositivo(tipo=MOVILES), S("tactil_no_responde"), S("tras_golpe_o_agua"))
    def r20_digitalizador(self):
        self.hallazgo(
            "R20", "Digitalizador (panel táctil) dañado",
            "Requiere reemplazo de pantalla; haz un respaldo si aún puedes usar "
            "el equipo.",
            0.80, "El táctil falla tras un golpe, caída o contacto con líquido.")

    @Rule(Dispositivo(tipo=MOVILES), S("tactil_no_responde"))
    def r21_tactil_software(self):
        self.hallazgo(
            "R21", "Falla de software, protector o suciedad en la pantalla",
            "Limpia la pantalla, retira el protector, reinicia y actualiza el "
            "sistema; prueba en modo seguro.",
            0.50, "El táctil no responde bien, sin antecedentes de golpe o líquido.")

    # ═════════════════════════ RENDIMIENTO ═════════════════════════

    @Rule(S("sistema_lento"), S("almacenamiento_lleno"))
    def r22_almacenamiento_saturado(self):
        self.hallazgo(
            "R22", "Almacenamiento saturado",
            "Libera al menos un 15–20% de espacio: borra archivos y apps que no "
            "uses y limpia descargas y caché.",
            0.80, "Está lento y el almacenamiento está casi lleno.")

    @Rule(Dispositivo(tipo=CON_VENTILADOR), S("sistema_lento"), S("ruido_disco"))
    def r23_disco_lento(self):
        self.hallazgo(
            "R23", "Disco duro con desgaste o fallas",
            "Respalda tu información de inmediato y cambia el disco, de "
            "preferencia por uno SSD.",
            0.85, "Está lento y el disco hace clics o ruidos extraños.")

    @Rule(S("sistema_lento"), S("equipo_antiguo"))
    def r24_hardware_insuficiente(self):
        self.hallazgo(
            "R24", "Hardware insuficiente para la carga actual",
            "Cierra programas innecesarios y desactiva los de inicio; en laptop o "
            "PC considera ampliar la RAM o cambiar a un SSD.",
            0.55, "Está lento y el equipo tiene más de 3 años.")

    @Rule(S("se_congela"), S("sobrecalentamiento"))
    def r25_throttling(self):
        self.hallazgo(
            "R25", "Reducción de velocidad por temperatura",
            "Mejora la ventilación y limpia el equipo: el sistema baja su "
            "velocidad para enfriarse y por eso se traba.",
            0.70, "Se congela y además se calienta demasiado.")

    @Rule(Dispositivo(tipo=MOVILES), S("apps_cierran"), S("almacenamiento_lleno"))
    def r26_memoria_movil(self):
        self.hallazgo(
            "R26", "Memoria insuficiente",
            "Libera espacio, borra la caché y desinstala apps que no uses.",
            0.75, "Las apps se cierran solas y el almacenamiento está casi lleno.")

    # ═════════════════════════ TEMPERATURA ═════════════════════════

    @Rule(Dispositivo(tipo=CON_VENTILADOR), S("sobrecalentamiento"), S("ventilador_ruidoso"))
    def r27_polvo_pasta(self):
        self.hallazgo(
            "R27", "Polvo acumulado o pasta térmica seca",
            "Limpia ventiladores y disipador con aire comprimido y cambia la "
            "pasta térmica.",
            0.75, "Se calienta demasiado y el ventilador trabaja al máximo con ruido.")

    @Rule(Dispositivo(tipo=CON_VENTILADOR), S("sobrecalentamiento"), S("ventilador_parado"))
    def r28_ventilador_danado(self):
        self.hallazgo(
            "R28", "Ventilador dañado o desconectado",
            "Reemplaza el ventilador y, mientras tanto, evita usar el equipo con "
            "cargas altas.",
            0.85, "Se calienta demasiado y el ventilador no gira.")

    @Rule(S("sobrecalentamiento"), S("calienta_en_reposo"))
    def r29_procesos_malware(self):
        self.hallazgo(
            "R29", "Procesos en segundo plano o software malicioso",
            "Revisa el administrador de tareas (o el uso de batería), desinstala "
            "apps sospechosas y ejecuta un análisis antimalware.",
            0.65, "Se calienta incluso sin usarlo, lo que sugiere trabajo oculto.")

    # ═════════════════════════ ALMACENAMIENTO ═════════════════════════

    @Rule(Dispositivo(tipo=CON_VENTILADOR), S("ruido_disco"))
    def r30_disco_mecanico(self):
        self.hallazgo(
            "R30", "Disco duro con fallas mecánicas",
            "Respalda tu información cuanto antes y reemplaza el disco.",
            0.75, "El disco hace clics, golpeteos o zumbidos anormales.")

    @Rule(S("no_arranca_sistema"), S("cambio_reciente"))
    def r31_actualizacion_danada(self):
        self.hallazgo(
            "R31", "Actualización o instalación que dañó el sistema",
            "Arranca en modo seguro o de recuperación y restaura a un punto "
            "anterior; si no, reinstala el sistema.",
            0.80, "No inicia el sistema y el problema comenzó tras actualizar o instalar.")

    @Rule(Dispositivo(tipo=CON_VENTILADOR), S("no_arranca_sistema"), S("ruido_disco"))
    def r32_disco_no_arranca(self):
        self.hallazgo(
            "R32", "Disco dañado: no puede cargar el sistema",
            "Respalda lo que puedas desde otro medio y reemplaza el disco; "
            "después reinstala el sistema.",
            0.90, "No inicia el sistema y el disco hace ruidos anormales.")

    @Rule(S("no_arranca_sistema"))
    def r33_sistema_corrupto(self):
        self.hallazgo(
            "R33", "Sistema operativo corrupto",
            "Prueba el modo de recuperación o seguro; si no funciona, restablece "
            "o reinstala el sistema (respaldando antes si puedes).",
            0.45, "Enciende pero no termina de iniciar el sistema.")

    # ═════════════════════════ RED ═════════════════════════

    @Rule(S("sin_wifi"), S("otros_conectan"))
    def r34_adaptador_wifi(self):
        self.hallazgo(
            "R34", "Adaptador Wi-Fi o configuración de red del equipo",
            "Activa y desactiva el modo avión, olvida la red y vuelve a "
            "conectarla, reinicia el equipo y actualiza los controladores. Si "
            "falla, puede ser el adaptador.",
            0.80, "No se conecta al Wi-Fi, pero otros dispositivos sí: el problema está en este equipo.")

    @Rule(S("sin_wifi"))
    def r35_router(self):
        self.hallazgo(
            "R35", "Router, proveedor de internet o contraseña",
            "Reinicia el router, verifica la contraseña y prueba cerca del router.",
            0.50, "No se conecta al Wi-Fi.")

    @Rule(Dispositivo(tipo=MOVILES), S("sin_senal"), S("sim_falla_otro"))
    def r36_sim_danada(self):
        self.hallazgo(
            "R36", "SIM dañada o línea suspendida",
            "Contacta a tu operador para reponer la SIM y verificar tu línea.",
            0.85, "No hay señal y la SIM también falla en otro equipo.")

    @Rule(Dispositivo(tipo=MOVILES), S("sin_senal"))
    def r37_red_movil(self):
        self.hallazgo(
            "R37", "Ajustes de red, bandeja de SIM o antena",
            "Reinicia, apaga el modo avión, reinserta la SIM y restablece los "
            "ajustes de red. Si no mejora, prueba la SIM en otro equipo.",
            0.50, "Sin señal o no reconoce la SIM.")

    # ═════════════════════════ AUDIO Y PUERTOS ═════════════════════════

    @Rule(S("sin_sonido"), S("tras_golpe_o_agua"))
    def r38_altavoz_danado(self):
        self.hallazgo(
            "R38", "Altavoz o circuito de audio dañado",
            "Prueba con audífonos: si suenan, el altavoz está dañado y debe "
            "reemplazarse.",
            0.75, "No hay sonido tras un golpe, caída o contacto con líquido.")

    @Rule(S("sin_sonido"))
    def r39_config_audio(self):
        self.hallazgo(
            "R39", "Volumen, salida de audio incorrecta o controlador",
            "Revisa el volumen y el modo silencio, selecciona la salida de audio "
            "correcta, reinicia y actualiza o reinstala los controladores.",
            0.50, "No sale sonido.")

    @Rule(Dispositivo(tipo=CON_VENTILADOR), S("usb_no_funciona"))
    def r40_usb(self):
        self.hallazgo(
            "R40", "Controladores USB o puertos dañados",
            "Prueba otro puerto y otro dispositivo, reinicia, reinstala los "
            "controladores USB y revisa el administrador de dispositivos.",
            0.60, "Los puertos USB no reconocen nada.")
