"""Interfaz gráfica (Tkinter) del sistema experto de diagnóstico de dispositivos."""
import tkinter as tk
from tkinter import messagebox, ttk

from catalogo import DISPOSITIVOS, SINTOMAS_POR_ID, raices_por_categoria
from dialogo import Consulta, detectar_sintomas

FUENTE = "Segoe UI"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema experto – Diagnóstico de celulares, tablets, laptops y PCs")
        self.geometry("1060x720")
        self.minsize(940, 640)

        self.tipo = tk.StringVar(value="celular")
        self.checks = {}      # id de síntoma -> BooleanVar (lista principal)
        self.extra = set()    # síntomas detectados en el texto que no están en la lista
        self.consulta = None  # Consulta en curso (None = no hay ninguna)

        self._estilos()
        self._construir()
        self._cargar_lista()
        self._mensaje_inicial()

        self.bind_all("<MouseWheel>", self._rueda)
        self.bind_all("<Button-4>", self._rueda)   # Linux
        self.bind_all("<Button-5>", self._rueda)

    # ═════════════════════ construcción de la ventana ═════════════════════
    def _estilos(self):
        st = ttk.Style(self)
        try:
            st.theme_use("clam")
        except tk.TclError:
            pass
        st.configure("Accent.TButton", font=(FUENTE, 10, "bold"), padding=8)
        st.configure("Suave.TLabel", foreground="#666666")

    def _construir(self):
        cuerpo = ttk.Frame(self, padding=10)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.columnconfigure(0, weight=1, uniform="col")
        cuerpo.columnconfigure(1, weight=1, uniform="col")
        cuerpo.rowconfigure(0, weight=1)

        # ---------- columna izquierda: entrada ----------
        izq = ttk.Frame(cuerpo)
        izq.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        izq.columnconfigure(0, weight=1)
        izq.rowconfigure(2, weight=1)
        self.izq = izq

        f1 = ttk.LabelFrame(izq, text=" 1. ¿Qué dispositivo es? ", padding=8)
        f1.grid(row=0, column=0, sticky="ew")
        for i, (clave, nombre) in enumerate(DISPOSITIVOS.items()):
            ttk.Radiobutton(f1, text=nombre, value=clave, variable=self.tipo,
                            command=self._al_cambiar_tipo).grid(row=0, column=i, padx=6)

        f2 = ttk.LabelFrame(izq, text=" 2. Cuéntame qué le pasa (opcional) ", padding=8)
        f2.grid(row=1, column=0, sticky="ew", pady=8)
        f2.columnconfigure(0, weight=1)
        self.txt_desc = tk.Text(f2, height=4, wrap="word", font=(FUENTE, 10))
        self.txt_desc.grid(row=0, column=0, sticky="ew")
        ttk.Button(f2, text="Detectar síntomas en mi texto",
                   command=self._detectar).grid(row=1, column=0, sticky="e", pady=(6, 0))

        f3 = ttk.LabelFrame(izq, text=" 3. O marca lo que observas ", padding=8)
        f3.grid(row=2, column=0, sticky="nsew")
        f3.columnconfigure(0, weight=1)
        f3.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(f3, highlightthickness=0, borderwidth=0)
        sb = ttk.Scrollbar(f3, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")
        self.lista = ttk.Frame(self.canvas)
        self.lista_id = self.canvas.create_window((0, 0), window=self.lista, anchor="nw")
        self.lista.bind("<Configure>",
                        lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfigure(self.lista_id, width=e.width))

        self.btn_iniciar = ttk.Button(izq, text="Iniciar diagnóstico",
                                      style="Accent.TButton", command=self._iniciar)
        self.btn_iniciar.grid(row=3, column=0, sticky="ew", pady=(8, 0))

        # ---------- columna derecha: conversación y resultados ----------
        der = ttk.LabelFrame(cuerpo, text=" Consulta ", padding=8)
        der.grid(row=0, column=1, sticky="nsew")
        der.columnconfigure(0, weight=1)
        der.rowconfigure(0, weight=1)

        self.log = tk.Text(der, wrap="word", state="disabled", padx=8, pady=8,
                           relief="flat", font=(FUENTE, 10), background="#fafafa")
        sb2 = ttk.Scrollbar(der, command=self.log.yview)
        self.log.configure(yscrollcommand=sb2.set)
        self.log.grid(row=0, column=0, sticky="nsew")
        sb2.grid(row=0, column=1, sticky="ns")
        self.log.tag_configure("titulo", font=(FUENTE, 13, "bold"))
        self.log.tag_configure("sistema", foreground="#1b4f9c", font=(FUENTE, 10, "bold"))
        self.log.tag_configure("usuario", foreground="#2e7d32")
        self.log.tag_configure("falla", font=(FUENTE, 11, "bold"))
        self.log.tag_configure("alerta", foreground="#b00020", font=(FUENTE, 11, "bold"))
        self.log.tag_configure("suave", foreground="#666666")

        # panel de pregunta (aparece solo mientras se pregunta)
        self.panel_preg = ttk.Frame(der)
        self.panel_preg.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.lbl_preg = ttk.Label(self.panel_preg, text="", wraplength=440,
                                  font=(FUENTE, 11, "bold"), justify="left")
        self.lbl_preg.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))
        for i, (txt, valor) in enumerate((("Sí", "si"), ("No", "no"), ("No sé", "no_se"))):
            self.panel_preg.columnconfigure(i, weight=1)
            ttk.Button(self.panel_preg, text=txt,
                       command=lambda v=valor: self._responder(v)
                       ).grid(row=1, column=i, sticky="ew", padx=(0 if i == 0 else 6, 0))
        self.lbl_prog = ttk.Label(self.panel_preg, text="", style="Suave.TLabel")
        self.lbl_prog.grid(row=2, column=0, columnspan=3, sticky="w", pady=(6, 0))
        self.panel_preg.grid_remove()

        ttk.Button(der, text="Nueva consulta", command=self._nueva
                   ).grid(row=2, column=0, columnspan=2, sticky="e", pady=(8, 0))

    # ═════════════════════ lista de síntomas ═════════════════════
    def _cargar_lista(self):
        previos = {sid for sid, var in self.checks.items() if var.get()}
        for w in self.lista.winfo_children():
            w.destroy()
        self.checks = {}
        for categoria, sintomas in raices_por_categoria(self.tipo.get()):
            ttk.Label(self.lista, text=categoria,
                      font=(FUENTE, 10, "bold")).pack(anchor="w", pady=(8, 2))
            for s in sintomas:
                var = tk.BooleanVar(value=s["id"] in previos)
                ttk.Checkbutton(self.lista, text=s["texto"],
                                variable=var).pack(anchor="w", padx=14)
                self.checks[s["id"]] = var
        self.canvas.yview_moveto(0)

    def _al_cambiar_tipo(self):
        self.extra.clear()
        self._cargar_lista()

    def _rueda(self, event):
        """Rueda del ratón: solo desplaza la lista cuando el puntero está sobre ella."""
        try:
            w = self.winfo_containing(event.x_root, event.y_root)
        except (KeyError, tk.TclError):
            return
        if w is None or not str(w).startswith(str(self.canvas)):
            return
        if event.num == 4:
            paso = -1
        elif event.num == 5:
            paso = 1
        else:
            paso = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(paso, "units")

    # ═════════════════════ detección en texto libre ═════════════════════
    def _detectar(self, silencioso=False):
        texto = self.txt_desc.get("1.0", "end").strip()
        ids = detectar_sintomas(texto, self.tipo.get()) if texto else []
        self.extra = {i for i in ids if i not in self.checks}
        for i in ids:
            if i in self.checks:
                self.checks[i].set(True)

        if not silencioso:
            self._log_limpiar()
            if not texto:
                self._log("Escribe primero una descripción en el cuadro de la izquierda.\n",
                          "suave")
            elif ids:
                self._log("Detecté esto en tu descripción:\n", "sistema")
                for i in ids:
                    self._log(f"  • {SINTOMAS_POR_ID[i]['texto']}\n")
                self._log("\nLos síntomas principales quedaron marcados en la lista; "
                          "revísalos y corrige lo que no sea correcto.\n", "suave")
            else:
                self._log("No reconocí síntomas en tu texto. Prueba con otras palabras "
                          "o marca las opciones de la lista.\n", "suave")
        return ids

    # ═════════════════════ consulta ═════════════════════
    def _iniciar(self):
        if self.consulta is not None:
            return
        self._detectar(silencioso=True)
        iniciales = [sid for sid, var in self.checks.items() if var.get()]
        iniciales += [sid for sid in sorted(self.extra) if sid not in iniciales]
        if not iniciales:
            messagebox.showinfo(
                "Falta información",
                "Marca al menos un síntoma en la lista, o describe el problema "
                "con tus palabras.")
            return

        tipo = self.tipo.get()
        self._bloquear_entrada(True)
        self.consulta = Consulta(tipo, iniciales)

        self._log_limpiar()
        self._log(f"Diagnóstico para: {DISPOSITIVOS[tipo]}\n\n", "titulo")
        self._log("Síntomas de partida:\n", "sistema")
        for sid in iniciales:
            self._log(f"  • {SINTOMAS_POR_ID[sid]['texto']}\n")
        self._log("\nVoy a hacerte algunas preguntas para afinar el diagnóstico.\n\n",
                  "suave")
        self._avanzar()

    def _avanzar(self):
        c = self.consulta
        if c.terminada():
            self.panel_preg.grid_remove()
            self._mostrar_resultados()
            return
        pregunta = c.actual["pregunta"]
        self.panel_preg.grid()
        self.lbl_preg.config(text=pregunta)
        self.lbl_prog.config(text=f"Pregunta {c.hechas + 1}")
        self._log("Sistema: ", "sistema")
        self._log(pregunta + "\n")

    def _responder(self, valor):
        c = self.consulta
        if c is None or c.terminada():
            return
        etiqueta = {"si": "Sí", "no": "No", "no_se": "No sé"}[valor]
        self._log(f"   Tú: {etiqueta}\n\n", "usuario")
        c.responder(valor)
        self._avanzar()

    def _mostrar_resultados(self):
        c = self.consulta
        try:
            resultados = c.diagnosticar()
        except ImportError:
            self._log("\nNo se pudo cargar Experta. Activa el entorno virtual (venv39) "
                      "e instala la librería con: pip install experta\n", "alerta")
            self._terminar()
            return
        except Exception as e:  # error inesperado en el motor
            self._log(f"\nError en el motor de inferencia: {e}\n", "alerta")
            self._terminar()
            return

        self._log("─" * 46 + "\n", "suave")
        self._log("DIAGNÓSTICO\n", "titulo")

        if not resultados:
            self._log("\nCon los síntomas indicados no encontré una falla probable. "
                      "Prueba a describir más detalles, o consulta a un técnico.\n")
        for n, h in enumerate(resultados[:5], 1):
            llenos = round(h["confianza"] * 10)
            barra = "█" * llenos + "░" * (10 - llenos)
            self._log(f"\n{n}. {h['falla']}\n", "alerta" if h["urgente"] else "falla")
            self._log(f"   Confianza: {barra} {h['confianza']:.0%}\n", "suave")
            self._log("   Qué hacer: ", "sistema")
            self._log(h["solucion"] + "\n")
            self._log("   Por qué: ", "sistema")
            self._log(f"{h['porque']} (regla {h['regla']})\n")
        if len(resultados) > 5:
            self._log(f"\n…y {len(resultados) - 5} posibilidad(es) menos probables.\n", "suave")

        self._log("\nEsto es una orientación basada en reglas; no sustituye la revisión "
                  "de un técnico.\n", "suave")
        self._terminar()

    def _terminar(self):
        """Fin de la consulta: se puede ajustar la entrada y volver a diagnosticar."""
        self.consulta = None
        self._bloquear_entrada(False)

    def _nueva(self):
        self.consulta = None
        self.extra.clear()
        self.panel_preg.grid_remove()
        self._bloquear_entrada(False)
        self.txt_desc.delete("1.0", "end")
        for var in self.checks.values():
            var.set(False)
        self._mensaje_inicial()

    # ═════════════════════ utilidades ═════════════════════
    def _bloquear_entrada(self, bloquear):
        self._set_estado(self.izq, bloquear)

    def _set_estado(self, widget, bloquear):
        for hijo in widget.winfo_children():
            self._set_estado(hijo, bloquear)
        if isinstance(widget, (ttk.Button, ttk.Checkbutton, ttk.Radiobutton)):
            widget.state(["disabled"] if bloquear else ["!disabled"])
        elif isinstance(widget, tk.Text):
            widget.configure(state="disabled" if bloquear else "normal")

    def _log(self, texto, tag=None):
        self.log.configure(state="normal")
        self.log.insert("end", texto, (tag,) if tag else ())
        self.log.configure(state="disabled")
        self.log.see("end")

    def _log_limpiar(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _mensaje_inicial(self):
        self._log_limpiar()
        self._log("Bienvenido\n\n", "titulo")
        self._log("1. Elige el tipo de dispositivo.\n"
                  "2. Cuéntame con tus palabras qué le pasa y/o marca los síntomas "
                  "que observas.\n"
                  "3. Pulsa «Iniciar diagnóstico»: te iré haciendo preguntas para "
                  "afinar el resultado.\n")


if __name__ == "__main__":
    try:  # nitidez en pantallas con escala alta (Windows)
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    App().mainloop()
