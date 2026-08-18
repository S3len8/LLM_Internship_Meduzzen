import os
import subprocess


class TextToSpeech:
    """Speak text through the built-in Windows Speech API."""

    def speak(self, text: str) -> None:
        text = text.strip()
        if not text:
            return

        if os.name != "nt":
            raise RuntimeError("The built-in TTS backend is available on Windows only.")

        script = (
            "Add-Type -AssemblyName System.Speech; "
            "$synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            "$text = [Console]::In.ReadToEnd(); "
            "$synthesizer.Speak($text); "
            "$synthesizer.Dispose();"
        )

        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", script],
            input=text,
            text=True,
            capture_output=True,
            encoding="utf-8",
        )

        if result.returncode != 0:
            error = result.stderr.strip() or "Unknown TTS error."
            raise RuntimeError(f"TTS failed: {error}")
