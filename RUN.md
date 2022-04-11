# Wie man die Blockchain lokal startet

## Installation der Dependencies:
Installieren Sie alle Dependencies in der requirements.txt Datei.

## Nodes starten
Um einen Node zu starten führen sie `python main.py 80` im
`/src` Verzeichnis aus. `80` ist der Port auf dem der Node ausgeführt
werden soll. Der erste Node den Sie starten muss immer auf dem Port 80 laufen, die Ports 
aller weiteren Nodes können Sie frei wählen.

Um einen weiteren Node zu starten erstellen Sie eine Kopie das ganzen
Projektes (den blockchain-lab Ordner) und führen die oben genannten Schritte dort erneut aus
(für jeden weiteren Node wählen Sie einen neuen Port).

Auf diese Weise können Sie beliebig viele Nodes starten, aber beachten Sie für jeden Node 
eine neue Kopie des Projektes zu erstellen und einen neuen Port zu benutzen.
