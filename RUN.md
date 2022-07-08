# Wie man die Blockchain lokal startet

## Installation der Dependencies:
Installieren Sie alle Dependencies in der requirements.txt Datei.

```sh
pip install -r requirements.txt
```

## Nodes starten
Um einen Node zu starten führen sie `python main.py --port 80` im `/src` Verzeichnis aus. Alternativ kann statt `--port` auch `-p` verwendet werden.
`80` ist der Port auf dem der Node ausgeführt werden soll.
Der erste Node den Sie starten muss immer auf Port 80 laufen, die Ports aller weiteren Nodes können Sie frei wählen.

In einer Unix-Umgebung kann das Programm auch mit `./main.py <args>` gestartet werden. Unter Umständen sind `sudo` Rechte zum öffnen des Sockets notwendig.

Mit `--debug` kann das Debug-Logging aktiviert werden, um noch mehr informativen Output während der Programmausführung zu erhalten.
Für weiter Informationen kann das Hilfe-Menü kann mit `-h` oder `--help` aufgerufen werden.

Um einen weiteren Node zu starten erstellen Sie eine Kopie das ganzen Projektes (den blockchain-lab Ordner) und
führen die oben genannten Schritte dort erneut aus (für jeden weiteren Node wählen Sie einen neuen Port).
Auf diese Weise können Sie beliebig viele Nodes starten, aber beachten Sie für jeden Node 
eine neue Kopie des Projektes zu erstellen und einen neuen Port zu benutzen.
