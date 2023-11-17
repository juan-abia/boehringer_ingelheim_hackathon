from gtts import gTTS
import os

def text_to_speech(text, language='en', output_file='output.mp3'):
    """
    Convierte texto a voz y guarda el resultado en un archivo de audio.

    :param text: Texto que se convertirá a voz.
    :param language: Idioma del texto (código de idioma ISO 639-1).
    :param output_file: Nombre del archivo de salida.
    """
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(output_file)
    print(f'Texto convertido a voz y guardado en "{output_file}"')

    # Reproducir el archivo de audio (opcional)
    #os.system(f"start {output_file}")  # Windows
    os.system(f"xdg-open {output_file}")  # Linux

if __name__ == "__main__":
    # Texto que deseas convertir a voz
    texto_a_convertir = "C'mon Juan, use Bumble."

    # Llama a la función para convertir texto a voz
    text_to_speech(texto_a_convertir)

