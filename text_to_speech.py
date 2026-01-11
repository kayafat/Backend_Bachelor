# text_to_speech.py
# Tiny CLI helper: turn a text string into a spoken WAV file using pyttsx3 (offline TTS).

import sys
import pyttsx3
import textwrap

VOICE_EN_ZIRA = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"
VOICE_EN_DAVID = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0"

def synthesize(text, output_path):
    engine = pyttsx3.init()
    engine.setProperty("rate", 160)

 
    engine.setProperty("voice", VOICE_EN_ZIRA)  
    # engine.setProperty("voice", VOICE_EN_DAVID)  

    chunks = textwrap.wrap(text, width=200)
    safe_text = " ".join(chunks)

    engine.save_to_file(safe_text, output_path)
    engine.runAndWait()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python text_to_speech.py "text" output.wav')
        sys.exit(1)

    synthesize(sys.argv[1], sys.argv[2])