# Blockchain-Lab
Herzlich Willkommen!

## Einleitung
Dies ist die Realisierung einer einfachen Blockchain für das Modul Blockchain Lab des Studiengangs
Wirtschaftsinformatik und digitale Medien an der Hochschule der Medien im Wintersemester 21/22. Das Projekt
wird in einem Team bestehend aus zwei Personen bearbeitet und zeigt als Endprodukt eine einfache Implementierung 
einer Blockchain mit einem Peer-to-Peer Netzwerk.

## Inhalt
Wir haben zu Ihrer Unterstützung einige Markdown-Dokumente angelegt, die weitere Informationen
enthalten.

- [RUN.md](RUN.md) erklärt wie Sie die Blockhain und das Peer-to-Peer Netzwerk starten.
- [LICENSE.md](LICENSE.md) gibt lizenzrechtliche Hinweise.
- [/src](/src): In diesem Verzeichnis finden Sie den Source Code des Projekts.

## Folgende Funktionen sind prototypisch umgesetzt:
- Automatisches Peer-Discovery: Beim Start verbindet sich ein Node automatisch mit dem Rest des Netzwerkes
- Verteilte Validierung von Transaktionen, durch ein Protokoll angelehnt an das 2-Phase-Commit-Protokoll
- Transaktionen können über die Command-Line erstellt werden und werden an das ganze Netzwek gesendet und 
in der Blockchain aller Nodes gespecihert, wenn valide
- Invalide Transaktionen werden nicht von den Nodes gespeichert
- Teile der Blockchain oder die ganze Blockchain von anderen Nodes können heruntergeladen werden, durch eine vereinfachte Version des Initial Block Downloads von Bitcoin
- Resynchronisation der Nodes nach einem Fork in bestimmten Situationen
