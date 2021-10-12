# Map of Knowledge

## Official release:
https://map-of-knowledge.herokuapp.com/

## Zielsetzung

Unser Ziel war eine Visualisierung der Verbindung zwischen Wissensbereichen. Dafür wollten wir eine Suchmaschine entwickeln, die anhand eines eingegebenen Suchbegriffs einen Graphen erstellt.
Die Knotenpunkte ergeben sich aus den Artikeln, auf die der ursprüngliche Suchbegriff verlinkt. Diese sollte das Programm aus einer Wissensbibliothek lesen, zum Beispiel Wikipedia. Voraussichtliche Bestandteile unseres Projekts waren also die Visualisierung von Artikeln und ihrer Verweise aufeinander, also der Links sowie ein geeignetes User Interface, um den Suchbegriff, die Sprache und die Suchtiefe festzulegen.

## Fazit

Zusammenfassend lässt sich sagen, dass wir mit unserem Ergebnis ziemlich zufrieden sind. Wir konnten viele unserer Ideen umsetzen und sind so unserem Ziel recht nah gekommen, auch wenn sich die Zielsetzung immer wieder leicht verändert hat und sich den Gegebenheiten anpasste.

Unser wichtigstes Ziel war es, den Suchbegriff individuell eingeben zu können. Außerdem wollten wir eine einfach bedienbare Benutzeroberfläche gestalten, mithilfe derer man Parameter wie Sprache und Suchtiefe festlegen kann. Aber auch etwas verstecktere Features, wie die Möglichkeiten heranzuzoomen oder Knotenpunkte zu verschieben, sind integriert. Gleichzeitig gibt es aber auch vorausgewählte Möglichkeiten, die die Nutzung erleichtern.
Über unsere anfängliche Zielsetzung hinaus konnten wir außerdem einige weitere Eigenschaften einbauen wie die Möglichkeit, sich durch Hovern über den Knoten die Zusammenfassung der Artikel anzeigen zu lassen oder die Anzahl der Verzweigungen einzustellen.

### ToDo:

* Verschiedene Sprachen reparieren (bisher geht ja nur Englisch)
* Zusammenfassung beim Hovern über Artikel schöner machen
* Heroku crasht noch manchmal: Auswertung der Links vom Server geht unendlich weiter, wenn der Nutzer während der Erstellung die Seite verlässt/neu lädt 
