from repositorio_datos import ErrorServidorDatos, crear_base_datos
from interfaz import AplicacionEduIA


def main():
    try:
        crear_base_datos()
    except ErrorServidorDatos:
        # La interfaz explicará el problema al intentar iniciar sesión.
        pass

    aplicacion = AplicacionEduIA()
    aplicacion.mainloop()


if __name__ == "__main__":
    main()
