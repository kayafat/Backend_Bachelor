# Backend_Bachelor

## Projektbasis

Dieses Backend baut auf der im Rahmen der vorherigen Bachelorarbeit
entwickelten Systembasis auf. Im Rahmen dieser Arbeit wurde das Backend
insbesondere um die segmentierte Antwortverarbeitung, die Gestenauswahl,
die Piper-basierte Sprachausgabe und die Anbindung an den
MetaHuman-basierten Dozenten erweitert.

Dieses Repository enthält das Backend des im Rahmen der Bachelorarbeit entwickelten MetaHuman-basierten virtuellen Dozenten. Das Backend übernimmt unter anderem die Verarbeitung von Sprachaufnahmen, die Transkription mit Whisper, die wissensbasierte Antwortgenerierung mit LangChain, FAISS und Ollama, die Segmentierung der Modellantwort sowie die Erzeugung der Sprachausgabe mit Piper.

Für den vollständigen Betrieb werden zusätzlich das Unreal-Engine-Frontend ([GitHub zum Frontend](https://github.com/kayafat/Bachelor_Frontend.git)), eine PostgreSQL-Datenbank über Docker und ein Sprachmodell auf dem DACHS-Cluster der Hochschule Esslingen benötigt.

## Vorraussetzungen

Vor der erstmaligen Einrichtung werden folgende Komponenten benötigt:

- Windows 10 oder Windows 11
- Git und Git LFS
- Python 3.10
- Node.js und npm
- Docker beziehungsweise Docker Desktop
- eine Entwicklungsumgebung, beispielsweise Visual Studio Code
- Zugang zum DACHS-Cluster der Hochschule Esslingen
- aktive VPN-Verbindung zur Hochschule Esslingen
- Berechtigung zur Nutzung eines GPU-Knotens
- Ollama-Modul auf dem DACHS-Cluster
- Frontend-Repository mit Unreal Engine 5.6

1. Arbeitsordner anlegen und Backend herunterladen

```bash
D:
mkdir Bachelorarbeit
cd Bachelorarbeit
```

Oder gewünschten Ordner erstellen: 

```bash
D:/Bachelorarbeit
```

Anschließend das Backend-Repository im Terminal klonen:

```bash
D:\>cd Bachelorarbeit
D:\Bachelorarbeit>git clone https://github.com/kayafat/Backend_Bachelor.git
```
