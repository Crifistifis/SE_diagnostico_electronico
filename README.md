# SE_diagnostico_electronico
Proyecto de la materia de Ing. del Conocimiento en donde se busca realizar un Sistema Experto para el diagnóstico de fallas en equipos electricos y mecánicos

Documentación rápida del proyecto
Tecnologías usadas
Tecnología	Versión	Para qué se usa
Python	3.9.13	Lenguaje del proyecto
Experta	1.9.4	Motor de inferencia (reglas if-then), equivalente en Python a CLIPS
frozendict	1.2	Dependencia de Experta (se instala sola)
Tkinter	incluido en Python	Interfaz gráfica
venv	incluido en Python	Entorno virtual aislado
IDE	VS Code / Antigravity	Editor y terminal

Se eligió Python 3.9 porque Experta depende de frozendict 1.2, que falla en Python 3.10 o superior (error module 'collections' has no attribute 'Mapping').

Crear el entorno virtual (Windows, PowerShell)
Instalar Python 3.9.13 con el instalador .exe de python.org (no el .tar, que es código fuente). Verifica con:
   py -0

Debe aparecer -V:3.9.

Crear el entorno dentro de la carpeta del proyecto:
   py -3.9 -m venv venv39
Activarlo (debe aparecer (venv39) al inicio de la línea):
   venv39\Scripts\activate

Si PowerShell bloquea el script, ejecuta una vez:

   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
Verificar la versión:
   python --version

Debe decir Python 3.9.13.

Instalar Experta y comprobarlo:
   pip install experta
   python -c "import experta; print('Experta OK')"
Seleccionar el intérprete en el IDE: Ctrl+Shift+P → Python: Select Interpreter → el de venv39.
Guardar dependencias:
   pip freeze > requirements.txt
Crear .gitignore con estas líneas:
   venv39/
   .venv/
Ejecutar el proyecto
python verificar.py    # revisa que catálogo y reglas sean coherentes
python app.py          # abre la interfaz gráfica
Estructura de archivos
SE_diagnostico_electronico/
├── hechos.py          # tipos de hechos (Dispositivo, Sintoma, Hallazgo)
├── catalogo.py        # síntomas, preguntas y palabras clave
├── reglas.py          # 40 reglas + motor Experta
├── dialogo.py         # flujo de preguntas y llamada al motor
├── app.py             # interfaz gráfica (Tkinter)
├── verificar.py       # chequeo de coherencia
├── requirements.txt
└── README.md

Instalar en otra computadora

Con Python 3.9 instalado, dentro de la carpeta del proyecto:

py -3.9 -m venv venv39
venv39\Scripts\activate
pip install -r requirements.txt
python app.py
