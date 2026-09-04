import asyncio
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import voz


def probar_configuracion_edge_tts():
    comunicador = MagicMock()
    comunicador.save = AsyncMock()
    ruta = Path("audio_prueba.mp3")

    with patch.object(
        voz.edge_tts,
        "Communicate",
        return_value=comunicador,
    ) as constructor:
        asyncio.run(
            voz.generar_audio(
                "Hola desde EduIA",
                ruta,
            )
        )

    constructor.assert_called_once_with(
        "Hola desde EduIA",
        "es-MX-JorgeNeural",
    )
    comunicador.save.assert_awaited_once_with(
        str(ruta)
    )


def probar_reproductor_pygame():
    ruta = Path("audio_prueba.mp3")

    with (
        patch.object(voz.pygame.mixer, "init") as iniciar,
        patch.object(voz.pygame.mixer.music, "load") as cargar,
        patch.object(voz.pygame.mixer.music, "play") as reproducir,
        patch.object(
            voz.pygame.mixer.music,
            "get_busy",
            side_effect=[True, False],
        ),
        patch.object(voz.pygame.mixer.music, "stop") as detener,
        patch.object(voz.pygame.mixer.music, "unload") as descargar,
        patch.object(voz.pygame.mixer, "quit") as cerrar,
        patch.object(voz.time, "sleep") as esperar,
    ):
        voz.reproducir_audio(ruta)

    iniciar.assert_called_once_with()
    cargar.assert_called_once_with(str(ruta))
    reproducir.assert_called_once_with()
    esperar.assert_called_once_with(0.1)
    detener.assert_called_once_with()
    descargar.assert_called_once_with()
    cerrar.assert_called_once_with()


def probar_voz_local_configurada():
    motor = MagicMock()
    voz_instalada = SimpleNamespace(id="voz-local-0")
    motor.getProperty.return_value = [voz_instalada]

    with patch.object(
        voz.pyttsx3,
        "init",
        return_value=motor,
    ):
        voz.hablar_sin_internet(
            "Respuesta local"
        )

    motor.setProperty.assert_any_call(
        "voice",
        "voz-local-0",
    )
    motor.setProperty.assert_any_call(
        "rate",
        voz.VELOCIDAD_LOCAL,
    )
    motor.setProperty.assert_any_call(
        "volume",
        voz.VOLUMEN_LOCAL,
    )
    motor.say.assert_called_once_with(
        "Respuesta local"
    )
    motor.runAndWait.assert_called_once_with()
    motor.stop.assert_called_once_with()


def probar_voz_local_sin_voces_registradas():
    motor = MagicMock()
    motor.getProperty.return_value = []

    with patch.object(
        voz.pyttsx3,
        "init",
        return_value=motor,
    ):
        voz.hablar_sin_internet(
            "Respuesta predeterminada"
        )

    llamadas_voice = [
        llamada
        for llamada in motor.setProperty.call_args_list
        if llamada.args
        and llamada.args[0] == "voice"
    ]

    assert llamadas_voice == []
    motor.say.assert_called_once_with(
        "Respuesta predeterminada"
    )
    motor.runAndWait.assert_called_once_with()


def probar_texto_vacio():
    with patch.object(
        voz.tempfile,
        "mkstemp",
    ) as crear_temporal:
        assert voz.hablar("") is False
        assert voz.hablar("   ") is False

    crear_temporal.assert_not_called()


def probar_voz_en_linea_y_limpieza():
    rutas_creadas = []

    async def generar_simulado(texto, ruta_audio):
        assert texto == "Respuesta en línea"
        ruta_audio = Path(ruta_audio)
        rutas_creadas.append(ruta_audio)
        ruta_audio.write_bytes(b"audio simulado")

    with (
        patch.object(
            voz,
            "generar_audio",
            new=generar_simulado,
        ),
        patch.object(
            voz,
            "reproducir_audio",
        ) as reproducir,
        patch.object(
            voz,
            "hablar_sin_internet",
        ) as respaldo,
        patch("builtins.print"),
    ):
        resultado = voz.hablar(
            "Respuesta en línea"
        )

    assert resultado is True
    reproducir.assert_called_once()
    respaldo.assert_not_called()
    assert len(rutas_creadas) == 1
    assert rutas_creadas[0].suffix == ".mp3"
    assert not rutas_creadas[0].exists()


def probar_respaldo_local_y_limpieza():
    rutas_creadas = []

    async def fallar_en_linea(texto, ruta_audio):
        rutas_creadas.append(Path(ruta_audio))
        raise ConnectionError("Sin conexión simulada")

    with (
        patch.object(
            voz,
            "generar_audio",
            new=fallar_en_linea,
        ),
        patch.object(
            voz,
            "reproducir_audio",
        ) as reproducir,
        patch.object(
            voz,
            "hablar_sin_internet",
        ) as respaldo,
        patch("builtins.print"),
    ):
        resultado = voz.hablar(
            "Respuesta de respaldo"
        )

    assert resultado is True
    reproducir.assert_not_called()
    respaldo.assert_called_once_with(
        "Respuesta de respaldo"
    )
    assert len(rutas_creadas) == 1
    assert not rutas_creadas[0].exists()


def probar_fallo_de_ambos_motores():
    rutas_creadas = []

    async def fallar_en_linea(texto, ruta_audio):
        rutas_creadas.append(Path(ruta_audio))
        raise ConnectionError("Sin conexión simulada")

    with (
        patch.object(
            voz,
            "generar_audio",
            new=fallar_en_linea,
        ),
        patch.object(
            voz,
            "hablar_sin_internet",
            side_effect=RuntimeError(
                "Sin voz local simulada"
            ),
        ),
        patch("builtins.print"),
    ):
        resultado = voz.hablar(
            "Respuesta no disponible"
        )

    assert resultado is False
    assert len(rutas_creadas) == 1
    assert not rutas_creadas[0].exists()


PRUEBAS = [
    (
        "Configura la voz masculina Jorge",
        probar_configuracion_edge_tts,
    ),
    (
        "Controla correctamente el reproductor",
        probar_reproductor_pygame,
    ),
    (
        "Configura la voz local de respaldo",
        probar_voz_local_configurada,
    ),
    (
        "Tolera la ausencia de voces registradas",
        probar_voz_local_sin_voces_registradas,
    ),
    (
        "Rechaza textos vacíos sin crear archivos",
        probar_texto_vacio,
    ),
    (
        "Usa Edge TTS y elimina el temporal",
        probar_voz_en_linea_y_limpieza,
    ),
    (
        "Activa el respaldo local y elimina el temporal",
        probar_respaldo_local_y_limpieza,
    ),
    (
        "Maneja el fallo de ambos motores",
        probar_fallo_de_ambos_motores,
    ),
]


def main():
    correctas = 0
    errores = []

    for nombre, prueba in PRUEBAS:
        try:
            prueba()
            correctas += 1
            print(f"[CORRECTA] {nombre}")
        except Exception as error:
            errores.append((nombre, error))
            print(f"[ERROR] {nombre}: {error}")

    print("\n" + "=" * 70)
    print("RESUMEN DE PRUEBAS DE VOZ")
    print("=" * 70)
    print(f"Total de pruebas: {len(PRUEBAS)}")
    print(f"Respuestas correctas: {correctas}")
    print(f"Errores detectados: {len(errores)}")
    print(
        "Precisión: "
        f"{correctas / len(PRUEBAS):.2%}"
    )

    if errores:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
