import customtkinter as ctk

from eduia import procesar_consulta
from base_datos import buscar_estudiante

COLOR_FONDO = "#F4FAF6"
COLOR_TARJETA = "#FFFFFF"
COLOR_VERDE_CLARO = "#DDEFE3"
COLOR_VERDE_PRINCIPAL = "#79B791"
COLOR_VERDE_OSCURO = "#315A43"
COLOR_TEXTO = "#263D30"
COLOR_TEXTO_SECUNDARIO = "#698075"
COLOR_ERROR = "#B85C5C"


ctk.set_appearance_mode("light")


class AplicacionEduIA(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("EduIA - Asistente Virtual Universitario")
        self.geometry("1000x650")
        self.minsize(850, 550)
        self.configure(fg_color=COLOR_FONDO)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.estudiante_actual = None
        self.entrada_matricula = None
        self.etiqueta_error = None
        self.contenedor_mensajes = None
        self.entrada_consulta = None
        self.animacion_id = None

        self.mostrar_acceso()

    def limpiar_ventana(self):
        for elemento in self.winfo_children():
            elemento.destroy()

    def mostrar_acceso(self):
        self.limpiar_ventana()

        contenedor = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        contenedor.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)

        tarjeta = ctk.CTkFrame(
            contenedor,
            width=430,
            corner_radius=28,
            fg_color=COLOR_TARJETA,
            border_width=1,
            border_color=COLOR_VERDE_CLARO,
        )
        tarjeta.grid(
            row=0,
            column=0,
            padx=30,
            pady=30,
        )

        titulo = ctk.CTkLabel(
            tarjeta,
            text="EduIA",
            text_color=COLOR_VERDE_OSCURO,
            font=ctk.CTkFont(
                size=36,
                weight="bold",
            ),
        )
        titulo.pack(
            padx=45,
            pady=(45, 5),
        )

        subtitulo = ctk.CTkLabel(
            tarjeta,
            text="Asistente Virtual Universitario",
            text_color=COLOR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=15),
        )
        subtitulo.pack(pady=(0, 35))

        instruccion = ctk.CTkLabel(
            tarjeta,
            text="Ingresa tu matrícula",
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(
                size=17,
                weight="bold",
            ),
        )
        instruccion.pack(pady=(0, 12))

        self.entrada_matricula = ctk.CTkEntry(
            tarjeta,
            width=320,
            height=48,
            corner_radius=14,
            placeholder_text="Matrícula",
            fg_color=COLOR_FONDO,
            border_color=COLOR_VERDE_CLARO,
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(size=15),
        )
        self.entrada_matricula.pack(
            padx=45,
            pady=(0, 16),
        )
        self.entrada_matricula.bind(
            "<Return>",
            self.iniciar_sesion,
        )

        boton_ingresar = ctk.CTkButton(
            tarjeta,
            text="Ingresar",
            width=320,
            height=48,
            corner_radius=14,
            fg_color=COLOR_VERDE_PRINCIPAL,
            hover_color=COLOR_VERDE_OSCURO,
            text_color="#FFFFFF",
            font=ctk.CTkFont(
                size=15,
                weight="bold",
            ),
            command=self.iniciar_sesion,
        )
        boton_ingresar.pack(pady=(0, 15))

        self.etiqueta_error = ctk.CTkLabel(
            tarjeta,
            text="",
            width=320,
            wraplength=320,
            text_color=COLOR_ERROR,
            font=ctk.CTkFont(size=13),
        )
        self.etiqueta_error.pack(
            padx=45,
            pady=(0, 35),
        )

        self.after(
            150,
            self.entrada_matricula.focus_set,
        )

    def iniciar_sesion(self, evento=None):
        matricula = (
            self.entrada_matricula.get().strip()
        )

        if not matricula:
            self.etiqueta_error.configure(
                text="Escribe una matrícula para continuar."
            )
            return

        estudiante = buscar_estudiante(matricula)

        if estudiante is None:
            self.etiqueta_error.configure(
                text=(
                    "No se encontró un estudiante "
                    "con esa matrícula."
                )
            )
            return

        self.estudiante_actual = estudiante
        self.mostrar_chat()

    def mostrar_chat(self):
        self.limpiar_ventana()

        contenedor_principal = ctk.CTkFrame(
            self,
            fg_color=COLOR_FONDO,
        )
        contenedor_principal.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        contenedor_principal.grid_rowconfigure(
            0,
            weight=1,
        )
        contenedor_principal.grid_columnconfigure(
            1,
            weight=1,
        )

        barra_lateral = ctk.CTkFrame(
            contenedor_principal,
            width=260,
            corner_radius=0,
            fg_color=COLOR_VERDE_CLARO,
        )
        barra_lateral.grid(
            row=0,
            column=0,
            sticky="ns",
        )
        barra_lateral.grid_propagate(False)

        ctk.CTkLabel(
            barra_lateral,
            text="EduIA",
            text_color=COLOR_VERDE_OSCURO,
            font=ctk.CTkFont(
                size=30,
                weight="bold",
            ),
        ).pack(
            padx=25,
            pady=(35, 30),
        )

        ctk.CTkLabel(
            barra_lateral,
            text=self.estudiante_actual["nombre"],
            wraplength=210,
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(
                size=17,
                weight="bold",
            ),
        ).pack(
            padx=25,
            pady=(0, 8),
        )

        datos_estudiante = (
            f"Semestre "
            f"{self.estudiante_actual['semestre']}\n"
            f"Grupo {self.estudiante_actual['grupo']}"
        )

        ctk.CTkLabel(
            barra_lateral,
            text=datos_estudiante,
            text_color=COLOR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=14),
        ).pack(
            padx=25,
            pady=(0, 30),
        )

        ctk.CTkButton(
            barra_lateral,
            text="Nuevo chat",
            width=210,
            height=44,
            corner_radius=12,
            fg_color=COLOR_VERDE_PRINCIPAL,
            hover_color=COLOR_VERDE_OSCURO,
            command=self.nuevo_chat,
        ).pack(
            padx=25,
            pady=(0, 12),
        )

        espacio = ctk.CTkFrame(
            barra_lateral,
            fg_color="transparent",
        )
        espacio.pack(
            fill="both",
            expand=True,
        )

        ctk.CTkButton(
            barra_lateral,
            text="Cerrar sesión",
            width=210,
            height=44,
            corner_radius=12,
            fg_color="transparent",
            hover_color=COLOR_VERDE_PRINCIPAL,
            border_width=1,
            border_color=COLOR_VERDE_PRINCIPAL,
            text_color=COLOR_VERDE_OSCURO,
            command=self.cerrar_sesion,
        ).pack(
            padx=25,
            pady=(0, 30),
        )

        area_chat = ctk.CTkFrame(
            contenedor_principal,
            corner_radius=0,
            fg_color=COLOR_FONDO,
        )
        area_chat.grid(
            row=0,
            column=1,
            sticky="nsew",
        )
        area_chat.grid_rowconfigure(1, weight=1)
        area_chat.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            area_chat,
            text="Asistente académico",
            text_color=COLOR_VERDE_OSCURO,
            font=ctk.CTkFont(
                size=21,
                weight="bold",
            ),
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=30,
            pady=(22, 16),
        )

        self.contenedor_mensajes = (
            ctk.CTkScrollableFrame(
                area_chat,
                corner_radius=18,
                fg_color=COLOR_TARJETA,
            )
        )
        self.contenedor_mensajes.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=25,
            pady=(0, 15),
        )

        area_entrada = ctk.CTkFrame(
            area_chat,
            fg_color="transparent",
        )
        area_entrada.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=25,
            pady=(0, 25),
        )
        area_entrada.grid_columnconfigure(
            0,
            weight=1,
        )

        self.entrada_consulta = ctk.CTkEntry(
            area_entrada,
            height=50,
            corner_radius=15,
            placeholder_text="Escribe tu consulta...",
            fg_color=COLOR_TARJETA,
            border_color=COLOR_VERDE_CLARO,
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(size=15),
        )
        self.entrada_consulta.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 12),
        )
        self.entrada_consulta.bind(
            "<Return>",
            self.enviar_consulta,
        )

        ctk.CTkButton(
            area_entrada,
            text="Enviar",
            width=110,
            height=50,
            corner_radius=15,
            fg_color=COLOR_VERDE_PRINCIPAL,
            hover_color=COLOR_VERDE_OSCURO,
            command=self.enviar_consulta,
        ).grid(
            row=0,
            column=1,
        )

        self.nuevo_chat()
        self.entrada_consulta.focus_set()

    def agregar_mensaje(
        self,
        remitente,
        mensaje,
        animar=False,
    ):
        fila = ctk.CTkFrame(
            self.contenedor_mensajes,
            fg_color="transparent",
        )
        fila.pack(
            fill="x",
            padx=15,
            pady=8,
        )

        es_estudiante = remitente == "Tú"

        color_mensaje = (
            "#CBE8D4"
            if es_estudiante
            else "#E5F3E9"
        )

        burbuja = ctk.CTkFrame(
            fila,
            corner_radius=16,
            fg_color=color_mensaje,
        )
        burbuja.pack(
            side="right" if es_estudiante else "left",
            padx=5,
        )

        ctk.CTkLabel(
            burbuja,
            text=remitente,
            text_color=COLOR_VERDE_OSCURO,
            font=ctk.CTkFont(
                size=13,
                weight="bold",
            ),
            anchor="w",
        ).pack(
            fill="x",
            padx=16,
            pady=(11, 2),
        )

        etiqueta_mensaje = ctk.CTkLabel(
            burbuja,
            text="" if animar else mensaje,
            wraplength=570,
            justify="left",
            anchor="w",
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(size=14),
        )
        etiqueta_mensaje.pack(
            fill="x",
            padx=16,
            pady=(0, 12),
        )

        self.after(
            10,
            self.desplazar_al_final,
        )

        if animar:
            self.escribir_letra_por_letra(
                etiqueta_mensaje,
                mensaje,
            )

    def desplazar_al_final(self):
        if self.contenedor_mensajes is None:
            return

        self.update_idletasks()

        self.contenedor_mensajes._parent_canvas.yview_moveto(
            1.0
        )

    def escribir_letra_por_letra(
        self,
        etiqueta,
        mensaje,
        indice=1,
    ):
        if indice > len(mensaje):
            self.animacion_id = None
            self.desplazar_al_final()
            return

        etiqueta.configure(
            text=mensaje[:indice]
        )

        if indice % 8 == 0:
            self.desplazar_al_final()

        self.animacion_id = self.after(
            8,
            lambda: self.escribir_letra_por_letra(
                etiqueta,
                mensaje,
                indice + 1,
            ),
        )

    def cancelar_animacion(self):
        if self.animacion_id is None:
            return

        self.after_cancel(self.animacion_id)
        self.animacion_id = None

    def enviar_consulta(self, evento=None):
        consulta = (
            self.entrada_consulta.get().strip()
        )

        if not consulta:
            return

        comando = consulta.casefold()

        if comando == "salir":
            self.destroy()
            return

        if comando in {
            "cerrar sesión",
            "cerrar sesion",
            "cerrar secion",
            "cambiar sesión",
            "cambiar sesion",
            "cambiar secion",
        }:
            self.cerrar_sesion()
            return

        self.agregar_mensaje(
            "Tú",
            consulta,
        )
        self.entrada_consulta.delete(0, "end")

        (
            respuesta,
            tipo,
            categoria,
            confianza,
        ) = procesar_consulta(
            consulta,
            self.estudiante_actual,
        )

        respuesta_completa = (
            f"{respuesta}\n\n"
            f"Tipo: {tipo}\n"
            f"Categoría: {categoria}\n"
            f"Confianza: {confianza:.0%}"
        )

        self.agregar_mensaje(
            "EduIA",
            respuesta_completa,
            animar=True,
        )

    def nuevo_chat(self):
        self.cancelar_animacion()
        
        if self.contenedor_mensajes is None:
            return

        for mensaje in (
            self.contenedor_mensajes.winfo_children()
        ):
            mensaje.destroy()

        nombre = self.estudiante_actual[
            "nombre"
        ].split()[0]

        self.agregar_mensaje(
            "EduIA",
            (
                f"Hola, {nombre}. Soy EduIA. "
                "¿En qué puedo ayudarte?"
            ),
        )

    def cerrar_sesion(self):
        self.cancelar_animacion()
        self.estudiante_actual = None
        self.mostrar_acceso()
