from base_datos import crear_base_datos
from interfaz import AplicacionEduIA


def main():
    crear_base_datos()

    aplicacion = AplicacionEduIA()
    aplicacion.mainloop()


if __name__ == "__main__":
    main()