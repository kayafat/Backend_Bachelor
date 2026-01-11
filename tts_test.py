import pyttsx3
engine = pyttsx3.init()
for v in engine.getProperty("voices"):
    langs = getattr(v, "languages", [])
    print("NAME:", getattr(v,"name",""), "| ID:", v.id, "| LANGS:", langs)

