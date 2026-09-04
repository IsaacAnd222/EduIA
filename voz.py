import asyncio
import os
import tempfile
import threading
import time
from pathlib import Path

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import edge_tts
import pygame
import pyttsx3


VOZ_PRINCIPAL = "es-MX-JorgeNeural"
VELOCIDAD_LOCAL = 170
VOLUMEN_LOCAL = 1.0

BLOQUEO_VOZ = threading.Lock()


async def generar_audio(
    texto,
    ruta_audio,
):
    comunicador = edge_tts.Communicate(
        texto,
        VOZ_PRINCIPAL,
    )
    await comunicador.save(
        str(ruta_audio)
    )


def reproducir_audio(ruta_audio):
    pygame.mixer.init()

    try:
        pygame.mixer.music.load(
            str(ruta_audio)
        )
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

    finally:
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.quit()


def hablar_sin_internet(texto):
    motor = pyttsx3.init()
    voces = motor.getProperty("voices")

    if voces:
        motor.setProperty(
            "voice",
            voces[0].id,
        )

    motor.setProperty(
        "rate",
        VELOCIDAD_LOCAL,
    )
    motor.setProperty(
        "volume",
        VOLUMEN_LOCAL,
    )

    motor.say(texto)
    motor.runAndWait()
    motor.stop()


def hablar(texto):
    if not texto or not texto.strip():
        return False

    with BLOQUEO_VOZ:
        descriptor, ruta_temporal = (
            tempfile.mkstemp(
                suffix=".mp3"
            )
        )
        os.close(descriptor)

        ruta_audio = Path(ruta_temporal)

        try:
            asyncio.run(
                generar_audio(
                    texto,
                    ruta_audio,
                )
            )

            reproducir_audio(
                ruta_audio
            )

            print(
                "Respuesta reproducida con "
                "la voz de Jorge."
            )
            return True

        except Exception as error_principal:
            print(
                "No fue posible utilizar "
                "la voz en línea."
            )
            print(
                f"Detalle: {error_principal}"
            )
            print(
                "Utilizando la voz local "
                "de respaldo..."
            )

            try:
                hablar_sin_internet(texto)
                return True

            except Exception as error_local:
                print(
                    "No fue posible reproducir "
                    "la respuesta."
                )
                print(
                    f"Detalle: {error_local}"
                )
                return False

        finally:
            try:
                ruta_audio.unlink(
                    missing_ok=True
                )
            except PermissionError:
                pass


def main():
    texto_prueba = (
        "Hola Isaac. Soy EduIA. "
        "La voz principal es Jorge. "
        "Si no hay conexión a Internet, "
        "utilizaré una voz local de respaldo."
    )

    print("Iniciando prueba de voz...")
    hablar(texto_prueba)
    print("PRUEBA TERMINADA.")


if __name__ == "__main__":
    main()