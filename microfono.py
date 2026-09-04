import speech_recognition as sr


INDICE_MICROFONO = 1


def escuchar_consulta(
    al_escuchar=None,
    al_reconocer=None,
):
    reconocedor = sr.Recognizer()
    reconocedor.dynamic_energy_threshold = True
    reconocedor.pause_threshold = 1.0
    reconocedor.phrase_threshold = 0.3
    reconocedor.non_speaking_duration = 0.5

    try:
        with sr.Microphone(
            device_index=INDICE_MICROFONO
        ) as fuente:
            reconocedor.adjust_for_ambient_noise(
                fuente,
                duration=1,
            )

            if al_escuchar is not None:
                al_escuchar()

            audio = reconocedor.listen(
                fuente,
                timeout=10,
                phrase_time_limit=12,
            )

            if al_reconocer is not None:
                al_reconocer()

        return reconocedor.recognize_google(
            audio,
            language="es-MX",
        )

    except sr.WaitTimeoutError as error:
        raise RuntimeError(
            "No se detectó voz. Intenta nuevamente."
        ) from error

    except sr.UnknownValueError as error:
        raise RuntimeError(
            "Se escuchó audio, pero no se pudo entender."
        ) from error

    except sr.RequestError as error:
        raise RuntimeError(
            "No fue posible acceder al reconocimiento de voz. "
            "Revisa tu conexión a Internet."
        ) from error

    except (AttributeError, OSError) as error:
        raise RuntimeError(
            "No fue posible abrir el micrófono."
        ) from error


def main():
    print("Calibrando el micrófono...")
    print("Habla cuando estés listo.")

    try:
        texto = escuchar_consulta()
        print(f"Texto reconocido: {texto}")
        print("PRUEBA CORRECTA.")
    except RuntimeError as error:
        print(f"ERROR: {error}")


if __name__ == "__main__":
    main()