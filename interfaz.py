from datetime import datetime
from pathlib import Path
import threading

from PIL import Image
import customtkinter as ctk

from microfono import escuchar_consulta
from voz import hablar


from eduia import (
    crear_contexto_conversacional,
    es_consulta_internet,
    procesar_consulta,
    procesar_consulta_internet,
)
from base_datos import (
    buscar_estudiante,
    guardar_retroalimentacion,
    obtener_historial_por_estudiante,
)

RUTA_PROYECTO = Path(__file__).resolve().parent
RUTA_LOGO = RUTA_PROYECTO / "assets" / "logo_eduia.png"
RUTA_ICONO = RUTA_PROYECTO / "assets" / "icono_eduia.ico"

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
        self.minsize(850, 650)
        self.configure(fg_color=COLOR_FONDO)

        self.after(
            200,
            lambda: self.iconbitmap(
                str(RUTA_ICONO)
            ),
        )

        with Image.open(RUTA_LOGO) as imagen:
            imagen_logo = imagen.copy()

        self.logo_acceso = ctk.CTkImage(
            light_image=imagen_logo,
            size=(170, 170),
        )

        self.logo_chat = ctk.CTkImage(
            light_image=imagen_logo,
            size=(105, 105),
        )

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.estudiante_actual = None
        self.entrada_matricula = None
        self.etiqueta_error = None
        self.contenedor_mensajes = None
        self.entrada_consulta = None
        self.animacion_id = None
        self.boton_microfono = None
        self.escuchando = False
        self.busqueda_internet_activa = False
        self.token_busqueda_internet = None
        self.voz_activada = ctk.BooleanVar(
            value=True
        )
        self.contexto_conversacion = (
            crear_contexto_conversacional()
        )

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

        logo_acceso = ctk.CTkLabel(
            tarjeta,
            text="",
            image=self.logo_acceso,
        )
        logo_acceso.pack(
            padx=45,
            pady=(25, 5),
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
            text="",
            image=self.logo_chat,
        ).pack(
            padx=25,
            pady=(15, 15),
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

        ctk.CTkLabel(
            barra_lateral,
            text="Consultas rápidas",
            text_color=COLOR_VERDE_OSCURO,
            font=ctk.CTkFont(
                size=14,
                weight="bold",
            ),
        ).pack(
            padx=25,
            pady=(8, 10),
        )

        consultas_rapidas = [
            (
                "Mi horario",
                "¿Cuál es mi horario?",
            ),
            (
                "Mis calificaciones",
                "¿Cuáles son mis calificaciones?",
            ),
            (
                "Mis exámenes",
                "¿Qué exámenes tengo?",
            ),
            (
                "Avisos escolares",
                "¿Hay avisos escolares?",
            ),
        ]

        for texto_boton, consulta in consultas_rapidas:
            ctk.CTkButton(
                barra_lateral,
                text=texto_boton,
                width=210,
                height=34,
                corner_radius=10,
                fg_color="#CBE8D4",
                hover_color=COLOR_VERDE_PRINCIPAL,
                text_color=COLOR_VERDE_OSCURO,
                command=lambda pregunta=consulta: (
                    self.enviar_consulta_rapida(
                        pregunta
                    )
                ),
            ).pack(
                padx=25,
                pady=4,
            )

        ctk.CTkSwitch(
            barra_lateral,
            text="Respuestas por voz",
            variable=self.voz_activada,
            onvalue=True,
            offvalue=False,
            progress_color=COLOR_VERDE_PRINCIPAL,
            button_color=COLOR_VERDE_OSCURO,
            button_hover_color=COLOR_VERDE_PRINCIPAL,
            text_color=COLOR_VERDE_OSCURO,
            font=ctk.CTkFont(size=13),
        ).pack(
            padx=25,
            pady=(18, 10),
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
            side="bottom",
            padx=25,
            pady=(15, 30),
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

        cabecera = ctk.CTkFrame(
            area_chat,
            fg_color="transparent",
        )
        cabecera.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=30,
            pady=(18, 14),
        )
        cabecera.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            cabecera,
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
        )

        ctk.CTkButton(
            cabecera,
            text="Historial",
            width=110,
            height=36,
            corner_radius=12,
            fg_color="transparent",
            hover_color=COLOR_VERDE_CLARO,
            border_width=1,
            border_color=COLOR_VERDE_PRINCIPAL,
            text_color=COLOR_VERDE_OSCURO,
            command=self.mostrar_historial,
        ).grid(
            row=0,
            column=1,
            sticky="e",
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

        self.boton_microfono = ctk.CTkButton(
            area_entrada,
            text="Hablar",
            width=115,
            height=50,
            corner_radius=15,
            fg_color=COLOR_VERDE_PRINCIPAL,
            hover_color=COLOR_VERDE_OSCURO,
            command=self.iniciar_escucha,
        )
        self.boton_microfono.grid(
            row=0,
            column=1,
            padx=(0, 12),
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
            column=2,
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

        return etiqueta_mensaje

    def agregar_metadatos_respuesta(
        self,
        tipo,
        categoria,
        confianza,
        fecha_hora=None,
        fue_util=None,
        mostrar_valoracion=False,
    ):
        
        partes = [
            f"Tipo: {tipo}",
            f"Categoría: {categoria}",
            f"Confianza: {confianza:.0%}",
        ]

        if fecha_hora is not None:
            partes.insert(
                0,
                f"Fecha: {fecha_hora}",
            )

        if mostrar_valoracion:
            if fue_util is None:
                valoracion = "Sin evaluar"
            elif fue_util == 1:
                valoracion = "Útil"
            else:
                valoracion = "No útil"

            partes.append(
                f"Valoración: {valoracion}"
            )

        texto_metadatos = "  ·  ".join(partes)

        fila = ctk.CTkFrame(
            self.contenedor_mensajes,
            fg_color="transparent",
        )
        fila.pack(
            fill="x",
            padx=20,
            pady=(0, 5),
        )

        ctk.CTkLabel(
            fila,
            text=texto_metadatos,
            wraplength=650,
            justify="left",
            anchor="w",
            text_color=COLOR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=11),
        ).pack(
            side="left",
            padx=10,
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

    def iniciar_escucha(self):
        if self.escuchando:
            return

        self.escuchando = True

        self.boton_microfono.configure(
            text="Preparando...",
            state="disabled",
            fg_color="#D59A3A",
        )

        hilo = threading.Thread(
            target=self.escuchar_en_segundo_plano,
            daemon=True,
        )
        hilo.start()

    def escuchar_en_segundo_plano(self):
        try:
            texto = escuchar_consulta(
                al_escuchar=lambda: self.after(
                    0,
                    self.mostrar_escuchando,
                ),
                al_reconocer=lambda: self.after(
                    0,
                    self.mostrar_reconociendo,
                ),
            )

            self.after(
                0,
                lambda: self.finalizar_escucha(
                    texto=texto
                ),
            )

        except RuntimeError as error:
            mensaje = str(error)

            self.after(
                0,
                lambda: self.finalizar_escucha(
                    error=mensaje
                ),
            )

    def mostrar_escuchando(self):
        if self.boton_microfono is None:
            return

        self.boton_microfono.configure(
            text="Escuchando...",
            fg_color="#C85C5C",
        )

    def mostrar_reconociendo(self):
        if self.boton_microfono is None:
            return

        self.boton_microfono.configure(
            text="Reconociendo...",
            fg_color="#4F86C6",
        )
        
    def finalizar_escucha(
        self,
        texto=None,
        error=None,
    ):
        self.escuchando = False

        self.boton_microfono.configure(
            text="Hablar",
            state="normal",
            fg_color=COLOR_VERDE_PRINCIPAL,
            hover_color=COLOR_VERDE_OSCURO,
        )

        if error is not None:
            self.agregar_mensaje(
                "EduIA",
                error,
            )
            return

        self.entrada_consulta.delete(0, "end")
        self.entrada_consulta.insert(0, texto)
        self.enviar_consulta()

    def iniciar_busqueda_internet(self, consulta):
        self.busqueda_internet_activa = True
        token = object()
        self.token_busqueda_internet = token

        etiqueta_estado = self.agregar_mensaje(
            "EduIA",
            "Buscando en Wikipedia...",
        )

        hilo = threading.Thread(
            target=self.ejecutar_busqueda_internet,
            args=(
                consulta,
                dict(self.estudiante_actual),
                self.contexto_conversacion,
                etiqueta_estado,
                token,
            ),
            daemon=True,
        )
        hilo.start()

    def ejecutar_busqueda_internet(
        self,
        consulta,
        estudiante,
        contexto,
        etiqueta_estado,
        token,
    ):
        try:
            resultado = procesar_consulta_internet(
                consulta,
                estudiante,
                contexto,
            )
        except Exception:
            resultado = (
                "Ocurrió un problema inesperado al consultar Wikipedia.",
                "externa",
                "internet",
                0.0,
                None,
            )

        self.after(
            0,
            lambda: self.finalizar_busqueda_internet(
                resultado,
                etiqueta_estado,
                token,
            ),
        )

    def finalizar_busqueda_internet(
        self,
        resultado,
        etiqueta_estado,
        token,
    ):
        if token is not self.token_busqueda_internet:
            return

        self.busqueda_internet_activa = False
        self.token_busqueda_internet = None

        if not etiqueta_estado.winfo_exists():
            return

        (
            respuesta,
            tipo,
            categoria,
            confianza,
            historial_id,
        ) = resultado

        etiqueta_estado.configure(
            text=respuesta
        )
        self.desplazar_al_final()

        if self.voz_activada.get():
            respuesta_hablada = respuesta.split(
                "\n\nFuente: Wikipedia",
                1,
            )[0]

            hilo_voz = threading.Thread(
                target=hablar,
                args=(respuesta_hablada,),
                daemon=True,
            )
            hilo_voz.start()

        self.agregar_metadatos_respuesta(
            tipo,
            categoria,
            confianza,
        )

        if historial_id is not None:
            self.agregar_opciones_retroalimentacion(
                historial_id
            )

    def enviar_consulta_rapida(self, consulta):
        if self.entrada_consulta is None:
            return

        self.entrada_consulta.delete(0, "end")
        self.entrada_consulta.insert(0, consulta)

        self.enviar_consulta()

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

        if self.busqueda_internet_activa:
            self.agregar_mensaje(
                "EduIA",
                "Espera a que termine la búsqueda actual.",
            )
            return

        self.agregar_mensaje(
            "Tú",
            consulta,
        )
        self.entrada_consulta.delete(0, "end")

        if es_consulta_internet(consulta):
            self.iniciar_busqueda_internet(
                consulta
            )
            return

        (
            respuesta,
            tipo,
            categoria,
            confianza,
            historial_id,
        ) = procesar_consulta(
            consulta,
            self.estudiante_actual,
            self.contexto_conversacion,
        )

        self.agregar_mensaje(
            "EduIA",
            respuesta,
            animar=True,
        )

        if self.voz_activada.get():
            hilo_voz = threading.Thread(
                target=hablar,
                args=(respuesta,),
                daemon=True,
            )
            hilo_voz.start()

        self.agregar_metadatos_respuesta(
            tipo,
            categoria,
            confianza,
        )

        self.agregar_opciones_retroalimentacion(
            historial_id
        )

    def agregar_opciones_retroalimentacion(
        self,
        historial_id,
    ):
        fila = ctk.CTkFrame(
            self.contenedor_mensajes,
            fg_color="transparent",
        )
        fila.pack(
            fill="x",
            padx=20,
            pady=(0, 12),
        )

        panel = ctk.CTkFrame(
            fila,
            corner_radius=12,
            fg_color=COLOR_FONDO,
        )
        panel.pack(side="left")

        etiqueta_estado = ctk.CTkLabel(
            panel,
            text="¿Esta respuesta fue útil?",
            text_color=COLOR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=12),
        )
        etiqueta_estado.pack(
            side="left",
            padx=(12, 8),
            pady=8,
        )

        ctk.CTkButton(
            panel,
            text="Sí",
            width=48,
            height=28,
            corner_radius=9,
            fg_color="#F4D6C7",
            hover_color="#DFAF9B",
            text_color=COLOR_TEXTO,
            command=lambda: (
                self.registrar_retroalimentacion(
                    historial_id,
                    True,
                    etiqueta_estado,
                )
            ),
        ).pack(
            side="left",
            padx=4,
            pady=8,
        )

        ctk.CTkButton(
            panel,
            text="No",
            width=48,
            height=28,
            corner_radius=9,
            fg_color="#F4D6C7",
            hover_color="#DFAF9B",
            text_color=COLOR_TEXTO,
            command=lambda: (
                self.registrar_retroalimentacion(
                    historial_id,
                    False,
                    etiqueta_estado,
                )
            ),
        ).pack(
            side="left",
            padx=(4, 12),
            pady=8,
        )

        self.after(
            10,
            self.desplazar_al_final,
        )

    def registrar_retroalimentacion(
        self,
        historial_id,
        fue_util,
        etiqueta_estado,
    ):
        guardar_retroalimentacion(
            historial_id,
            fue_util,
        )

        seleccion = (
            "Sí"
            if fue_util
            else "No"
        )

        etiqueta_estado.configure(
            text=(
                "Gracias por tu opinión. "
                f"Seleccionaste: {seleccion}"
            )
        )

    def mostrar_historial(self):
        self.cancelar_animacion()

        if (
            self.contenedor_mensajes is None
            or self.estudiante_actual is None
        ):
            return

        for mensaje in (
            self.contenedor_mensajes.winfo_children()
        ):
            mensaje.destroy()

        historial = obtener_historial_por_estudiante(
            self.estudiante_actual["matricula"],
            limite=10,
        )

        if not historial:
            self.agregar_mensaje(
                "EduIA",
                (
                    "Todavía no tienes consultas "
                    "guardadas en el historial."
                ),
            )
            return

        self.agregar_mensaje(
            "EduIA",
            (
                f"Estas son tus últimas "
                f"{len(historial)} consultas."
            ),
        )

        for registro in reversed(historial):
            self.agregar_mensaje(
                "Tú",
                registro["consulta"],
            )

            fecha_hora = datetime.fromisoformat(
                registro["fecha_hora"]
            ).strftime(
                "%d/%m/%Y %H:%M:%S"
            )

            self.agregar_mensaje(
                "EduIA",
                registro["respuesta"],
            )

            self.agregar_metadatos_respuesta(
                registro["tipo"],
                registro["categoria"],
                registro["confianza"],
                fecha_hora=fecha_hora,
                fue_util=registro["fue_util"],
                mostrar_valoracion=True,
            )

        self.after(
            50,
            self.desplazar_al_final,
        )

    def nuevo_chat(self):
        self.cancelar_animacion()
        self.busqueda_internet_activa = False
        self.token_busqueda_internet = None
        self.contexto_conversacion = (
            crear_contexto_conversacional()
        )
        
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
        self.busqueda_internet_activa = False
        self.token_busqueda_internet = None
        self.contexto_conversacion = (
            crear_contexto_conversacional()
        )
        self.estudiante_actual = None
        self.mostrar_acceso()
