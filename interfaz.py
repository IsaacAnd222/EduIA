import customtkinter as ctk

from base_datos import (
    buscar_estudiante,
    crear_base_datos,
)


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
        self.mostrar_bienvenida()

    def mostrar_bienvenida(self):
        self.limpiar_ventana()

        tarjeta = ctk.CTkFrame(
            self,
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

        ctk.CTkLabel(
            tarjeta,
            text="Acceso correcto",
            text_color=COLOR_VERDE_OSCURO,
            font=ctk.CTkFont(
                size=30,
                weight="bold",
            ),
        ).pack(
            padx=50,
            pady=(45, 15),
        )

        ctk.CTkLabel(
            tarjeta,
            text=self.estudiante_actual["nombre"],
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(
                size=20,
                weight="bold",
            ),
        ).pack(pady=(0, 8))

        informacion = (
            f"{self.estudiante_actual['carrera']}\n"
            f"Semestre {self.estudiante_actual['semestre']} · "
            f"Grupo {self.estudiante_actual['grupo']}"
        )

        ctk.CTkLabel(
            tarjeta,
            text=informacion,
            justify="center",
            text_color=COLOR_TEXTO_SECUNDARIO,
            font=ctk.CTkFont(size=15),
        ).pack(
            padx=50,
            pady=(0, 30),
        )

        ctk.CTkButton(
            tarjeta,
            text="Cerrar sesión",
            width=280,
            height=46,
            corner_radius=14,
            fg_color=COLOR_VERDE_PRINCIPAL,
            hover_color=COLOR_VERDE_OSCURO,
            command=self.cerrar_sesion,
        ).pack(
            padx=50,
            pady=(0, 45),
        )

    def cerrar_sesion(self):
        self.estudiante_actual = None
        self.mostrar_acceso()


if __name__ == "__main__":
    crear_base_datos()

    aplicacion = AplicacionEduIA()
    aplicacion.mainloop()