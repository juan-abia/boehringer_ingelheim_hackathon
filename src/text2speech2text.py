import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
import azure.cognitiveservices.speech as speechsdk
from gtts import gTTS
import os
import logging
logging.basicConfig(level = logging.INFO)

def text_to_speech(text, language='es', output_file='output.mp3'):
    """
    Convierte texto a voz y guarda el resultado en un archivo de audio.

    :param text: Texto que se convertirá a voz.
    :param language: Idioma del texto (código de idioma ISO 639-1).
    :param output_file: Nombre del archivo de salida.
    """
    tts = gTTS(text=text, lang=language, slow=False, tld='com.mx')
    tts.save(output_file)
    print(f'Texto convertido a voz y guardado en "{output_file}"')

    # Reproducir el archivo de audio (opcional)
    #os.system(f"start {output_file}")  # Windows
    os.system(f"xdg-open {output_file}")  # Linux

def micro_to_text():
    # Inicializar el reconocedor
    r = sr.Recognizer()

    # Capturar el audio del micrófono
    with sr.Microphone() as source:
        print("Habla algo:")
        audio = r.listen(source)

    # Intentar reconocer el audio
    try:
        text = r.recognize_google(audio, language="es-ES")
        return text
    except sr.UnknownValueError:
        return ("No pude entender el audio")
    except sr.RequestError as e:
        return ("No se pudo obtener resultados; {0}".format(e))

def mp3_to_text(mp3_file):
    # Convertir el archivo MP3 a formato WAV (requerido por SpeechRecognition)
    audio = AudioSegment.from_mp3(mp3_file)
    audio.export("output.wav", format="wav")
    if os.path.exists(mp3_file):
        os.remove(mp3_file)

    # Utilizar SpeechRecognition para reconocimiento de voz
    recognizer = sr.Recognizer()

    with sr.AudioFile("output.wav") as source:
        # Ajustar para condiciones de ruido si es necesario
        #recognizer.adjust_for_ambient_noise(source)

        # Reconocer el audio
        audio_data = recognizer.record(source)

        try:
            # Utilizar Google Web Speech API para reconocimiento de voz
            text = recognizer.recognize_google(audio_data)
            print(f'Texto reconocido: {text}')
        except sr.UnknownValueError:
            print('No se pudo reconocer el audio')
        except sr.RequestError as e:
            print(f'Error en la solicitud a Google Web Speech API: {e}')

def text_to_speech_azure(text, language="es-ES", region="Your_Region", key="Your_Subscription_Key"):
    """
    Convierte texto a voz usando Azure Text-to-Speech.

    :param text: Texto a convertir.
    :param language: Código de idioma (por defecto en-US).
    :param region: Región de tu recurso Azure.
    :param key: Clave de suscripción de tu recurso Azure.
    """
    # Configurar la conexión con el servicio Azure TTS
    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.speech_synthesis_language = language
    speech_config.speech_synthesis_voice_name = "es-ES-AlvaroNeural"

    logging.info("Using voice: " + speech_config.speech_synthesis_voice_name)
    logging.info("Using language: " + speech_config.speech_synthesis_language)
    
    # Crear un sintetizador de voz
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

    # Sintetizar el texto
    result = speech_synthesizer.speak_text_async(text).get()
    logging.info("Done")

    # Verificar si la síntesis fue exitosa
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        logging.info("Texto convertido a voz con éxito.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation = result.cancellation_details
        logging.error(f"Error de síntesis de voz: {cancellation.reason}")
        if cancellation.reason == speechsdk.CancellationReason.Error:
            logging.error(f"Código de error: {cancellation.error_code}")
            logging.error(f"Detalles del error: {cancellation.error_details}")
    else:
        logging.error("KAPASAAAAAOOO")
        logging.error(f"Error de síntesis de voz: {result.reason}")


if __name__ == "__main__":
    print(micro_to_text())