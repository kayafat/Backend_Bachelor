# Prototypische Umsetzung eines MetaHuman-basierten Dozenten für interaktive Prüfungsvorbereitung in einer Unreal-Engine-Lernumgebung (Backend)

## Projektbasis

Dieses Repository enthält das **Backend** des im Rahmen der Bachelorarbeit
entwickelten MetaHuman-basierten virtuellen Dozenten. Es baut auf der
Systembasis der vorherigen Bachelorarbeit auf und wurde insbesondere um die
segmentierte Antwortverarbeitung, die Gestenauswahl, die Piper-basierte
Sprachausgabe sowie die Anbindung an den MetaHuman erweitert.

Das Backend verarbeitet Sprachaufnahmen, transkribiert diese mit Whisper,
erzeugt wissensbasierte Antworten mit LangChain, FAISS und Ollama und stellt
die segmentierten Antworten einschließlich der erzeugten WAV-Dateien für das
Unreal-Engine-Frontend bereit.

Für den vollständigen Betrieb werden zusätzlich das [Unreal-Engine-Frontend](https://github.com/kayafat/Bachelor_Frontend.git), eine PostgreSQL-Datenbank über Docker und ein Sprachmodell auf dem DACHS-Cluster der Hochschule Esslingen benötigt.

# Schritt 1: Installation des Backends

Hier wird zunächst nur das Backend-Setup beschrieben. Eine ausführliche Erklärung für das DACHS befindet sich weiter unten.

## Voraussetzungen für das Backend

Vor der erstmaligen Einrichtung werden folgende Komponenten benötigt:

- Windows 10 oder Windows 11
- [Git](https://git-scm.com/install/windows) und [Git LFS](https://git-lfs.com/)
- [Python 3.10.11](https://www.python.org/downloads/release/python-31011/)
- [Node.js und npm](https://nodejs.org/en/download/)
- Docker beziehungsweise [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)
- eine Entwicklungsumgebung, beispielsweise Visual Studio Code

> [!NOTE]
> Die in dieser Anleitung verwendete Angabe wie `D:` dient als Beispiel. Laufwerk und Verzeichnisse, müssen jeweils in der Entwicklungsumgebung angepasst werden.

## 1. Arbeitsordner anlegen und Backend herunterladen

Öffnen Sie ein Terminal und erstellen Sie mit folgenden Befehlen einen Ordner, oder im Explorer auf dem gewünschten Laufwerk.
```bash
mkdir Bachelorarbeit
cd Bachelorarbeit
```
**Anschließend das Backend-Repository im Terminal klonen:**
```
git clone https://github.com/kayafat/Backend_Bachelor.git
```

## 2. Dateipfade anpassen und .env Datei erstellen

Öffnen Sie den Backend-Ordner in einer Entwicklungsumgebung und erstellen Sie eine neue `.env`-Datei und kopieren Sie die Inhalte von der `.env.example`.

**Verzeichnisse in server2.mjs und piper_server.py anpassen.**

**server2.mjs**:
```
const audioDir = "D:/Bachelorarbeit/Backend_Bachelor/generated";
const audioDir = "<LAUFWERK>:/<ORDNER>/Backend_Bachelor/generated";
```
**piper_server.py**:
```
BASE_DIR = r"D:\Bachelorarbeit\Backend_Bachelor"
BASE_DIR = r"<LAUFWERK>:\<ORDNER>\Backend_Bachelor"
```

## 3. Python- und Node.js-Abhängigkeiten installieren

Öffnen Sie ein Terminal, und wechseln Sie zu dem Backend_Bachelor Ordner. Sie sollten sich in `...\Bachelorarbeit\Backend_Bachelor>` befinden.

Python-Abhängigkeiten installieren:
```bat
py -3.10 -m pip install -r backend_requirements.txt
```
Node.js-Abhängigkeiten installieren:
```bat
npm install
```
Falls vulnerabilities auftreten sollten, mit dem folgenden Befehl beheben: `npm audit fix`.

## 4. Docker und PostgreSQL vorbereiten

Docker Desktop starten. Im Terminal im Backend-Verzeichnis folgendes eingeben:

```bat
docker compose up -d
```

Der verwendete Container trägt in der Entwicklungsumgebung die Bezeichnung: `backend_bachelor`.

## 5. Piper-Server starten

Ein separates lokales PowerShell-Terminal öffnen und in Backend-Verzeichnis wechseln. Piper-Server starten:

```bat
py -3.10 piper_server.py
```

- Erwartete Ausgabe:
```text
Loading Piper voice: ...\Backend_Bachelor\voices\en_US-amy-medium.onnx
Piper voice loaded.
Piper server running at http://127.0.0.1:5005
```

Dieses Terminal bleibt geöffnet. Der Piper-Server erzeugt die segmentweisen WAV-Dateien, die anschließend vom Unreal-Engine-Frontend verwendet werden.

---

## 6. Node.js Backend starten

In einem weiteren lokalen Terminal in das Backend-Verzeichnis wechseln und Backend starten:
```bat
npm start
```
- Erwartete Ausgabe:
```text
> backend_v2@1.0.0 start
> node server2.mjs

postgres
ENV DEBUG {
  DB_TYPE: 'postgres',
  PG_USER: 'postgres',
  PG_PASSWORD: '<PASSWORT>',
  PG_HOST: 'localhost',
  PG_PORT: '5433',
  PG_DATABASE: 'smartdb'
}

Connected to PostgreSQL
Server running at http://localhost:3003
```

Das Terminal muss während der Verwendung des Systems geöffnet bleiben.

### Problembehebung im Backend

- Falls Docker keine Virtualisation aufzeigt, öffnen Sie PowerShell als Administrator und führen `wsl --install --no-distribution` aus.
- Falls bei `npm start` die connection refused ist, überprüfen Sie ob der Container `backend_bachelor` gestartet wurde.

# Schritt 2: DACHS vorbereiten und starten

## Voraussetzungen für DACHS

- Zugang zum DACHS-Cluster der Hochschule Esslingen
- aktive VPN-Verbindung zur Hochschule Esslingen

> [!NOTE]
> Die Angaben `es_fakait01` und `gpu136` dienen als Beispiele. Der
> Benutzername und der GPU-Hostname müssen an den persönlichen Zugang und die
> aktuelle GPU-Zuweisung angepasst werden.

## 1. Erstes PowerShell-Terminal: GPU-Knoten und Ollama-Server:

Vor der Verbindung muss die VPN-Verbindung zur Hochschule Esslingen aktiv sein.
Für den Betrieb werden zwei PowerShell-Terminals verwendet.

**Login:**
```
ssh es_fakait01@dachs-login.hs-esslingen.de
```
**Beim erstmaligen Einrichten sollte ein Workspace für die Ollama-Modelle angelegt werden:**
```bash
ws_allocate ollama_models 60
```
- Vorhandene Workspaces anzeigen: ```ws_list```
- Die Laufzeit des Workspaces kann bei Bedarf um X Tage verlängert werden:`ws_extend ollama_models X`

**Anschließend kann ein GPU-Knoten für beispielsweise vier Stunden reserviert werden:**
```bash
srun --time=04:00:00 --gres=gpu:1 --partition=gpu1 --pty /bin/bash
```

> [!Important]
> Nach erfolgreicher Zuweisung ändert sich der Hostname beispielsweise zu **gpu136**. Der tatsächliche GPU-Hostname muss für die nachfolgenden Befehle übernommen werden.

**Ollama-Modul laden und den Server zunächst starten:**
```
module load cs/ollama
export OLLAMA_HOST=0.0.0.0:11434
ollama serve
```
> [!Important]
> Dieses Terminal bleibt geöffnet, solange das Sprachmodell benötigt wird.

## 2. Zweites PowerShell-Terminal: SSH-Tunnel und Modelle

**Login mit der gpu136:**
```bash
ssh -L 11434:gpu136:11434 es_fakait01@dachs-login.hs-esslingen.de
```

**Nach der Anmeldung das Ollama-Modul laden:**
```bash
module load cs/ollama
```

**Die verwendeten Modelle herunterladen:**

```bash
ollama pull llama3.1:8b
ollama pull llama3.1:70b
```
- Installierte Modelle kann man mit `ollama list` anzeigen.

## 3. Sprachmodell in `langchain_query.py` auswählen

In `langchain_query.py` wird festgelegt, welches Ollama-Modell verwendet wird.

Beispiel für das 8B- und 70B-Modell:
- `llm = Ollama(model="llama3.1:8b", base_url="http://localhost:11434")`
- `llm = Ollama(model="llama3.1:70b", base_url="http://localhost:11434")`

> [!Important]
> Nur die gewünschte Konfiguration darf aktiv sein. Andere Modellkonfigurationen bleiben auskommentiert. Nach der Anpassung wird die Datei gespeichert.
> Die lokale Adresse `http://localhost:11434` verweist über den SSH-Tunnel auf den Ollama-Server des zugewiesenen GPU-Knotens.

## 4. Ollama-Server mit Laufzeitparametern starten (Erstes Terminal)

> Ab hier startet man dann immer wieder sobald man mit DACHS arbeitet. Login und GPU-Knoten zuweisen lassen, und die Modelle in die GPU mit `module load cs/ollama` laden.

Falls im **ersten Terminal** noch `ollama serve` ausgeführt wird, den Prozess zunächst mit `Strg+C` beenden.
Anschließend Ollama mit den für die verwendeten Modelle vorgesehenen Laufzeitparametern erneut starten:

```bash
module load cs/ollama

OLLAMA_HOST=0.0.0.0:11434 \
OLLAMA_LOAD_TIMEOUT=0 \
OLLAMA_CONTEXT_LENGTH=4096 \
OLLAMA_MAX_LOADED_MODELS=1 \
OLLAMA_NUM_PARALLEL=1 \
OLLAMA_DEBUG=1 \
ollama serve 2>&1 | tee ~/ollama-server.log
```
**Die Einstellungen legen unter anderem fest:**
- keine Begrenzung des Modell-Lade-Timeouts
- Kontextlänge von 4096 Tokens
- maximal ein gleichzeitig geladenes Modell
- eine parallele Anfrage
- aktivierte Debug-Ausgaben
- Speicherung der Serverausgaben in `~/ollama-server.log`

> [!Important]
> Das erste Terminal muss während der Verwendung des Systems geöffnet bleiben.

## 5. Sprachmodell erstmalig laden (Zweites Terminal)

Im zweiten PowerShell-Terminal kann das gewählte Modell durch eine kurze Testanfrage geladen werden.

```bash
curl http://gpu136:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:70b",
    "prompt": "Antworte nur mit OK.",
    "stream": false,
    "keep_alive": "60m",
    "options": {
      "num_ctx": 4096,
      "num_predict": 8
    }
  }'
```

- Für das 8B-Modell wird lediglich der Modellname geändert: `"model": "llama3.1:8b"`
- `gpu136` muss durch den aktuell zugewiesenen GPU-Host ersetzt werden.

## 6. Ladezustand prüfen (Zweites Terminal)

```
curl -s http://gpu136:11434/api/ps | python3 -m json.tool
```

- Enthält die Ausgabe das ausgewählte Modell, wurde es erfolgreich geladen.

Beispiel:

```json
{
  "models": [
    {
      "name": "llama3.1:70b",
      "model": "llama3.1:70b",
      "details": {
        "format": "gguf",
        "family": "llama",
        "parameter_size": "70.6B",
        "quantization_level": "Q4_K_M"
      },
      "context_length": 4096
    }
  ]
}
```

> [!IMPORTANT]
> Auch das zweite Terminal mit dem SSH-Tunnel muss während der Verwendung des Systems geöffnet bleiben. Wird eines der beiden Terminals geschlossen, kann das Backend das Sprachmodell nicht mehr erreichen.

### Wichtige Informationen:

- Beim erstmaligen Laden des 70B-Modells kann eine Wartezeit von etwa fünf bis zehn Minuten auftreten. Dauert der Vorgang länger als zehn Minuten, kann er mit `Strg+C` abgebrochen und erneut gestartet werden.
- Durch `"keep_alive": "60m"` bleibt das Modell nach der Anfrage für 60 Minuten im Speicher. Die Dauer kann an die vorgesehene Test- oder Nutzungszeit angepasst werden.


# Schritt 3: Backend + DACHS Cluster

Wenn alles erfolgreich läuft, kann man...
- ... in `..\Bachelorarbeit\Backend_Bachelor>` mit `npm start` im einem Terminal das Backend starten,
- ... in `..\Bachelorarbeit\Backend_Bachelor>` in einem anderen Terminal mit `py -3.10 piper_server.py` den Piper Server starten,
- ... Docker Desktop den Container `backend_bachelor` starten,
- ... DACHS mit den jeweiligen Terminals erfolgreich bedienen.

Als nächstes muss man das Frontend starten: Das GitHub zum Frontend befindet sich [hier](https://github.com/kayafat/Bachelor_Frontend.git).

### Autor
- **Fatih Kaya**
- Bachelorarbeit, Hochschule Esslingen
