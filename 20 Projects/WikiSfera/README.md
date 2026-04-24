# 🌐 WikiSfera

Projekt mający na celu wizualizację powiązań między artykułami polskiej Wikipedii w formie grafu/mapy punktów.

## 🎯 Cele
- Przetworzenie dumpu tekstowego polskiej Wikipedii (bez grafik).
- Ekstrakcja linków wewnętrznych między artykułami.
- Wygenerowanie mapy punktów (grafu), gdzie:
  - **Wierzchołki** to artykuły.
  - **Krawędzie** to linki między nimi.
- Wizualizacja klastrów tematycznych.

## 🛠️ Stan Projektu (v2.2 - Deep Space Explorer)
- **Baza danych**: Przetworzono `plwiki` (119M linków, 2.3M artykułów).
- **Rdzeń grafu**: Wizualizacja top 10,000 najważniejszych artykułów.
- **Interakcja**: 
  - Fizyka na żywo (**ForceAtlas2**) w przeglądarce.
  - Logarytmiczne skalowanie wielkości węzłów (im więcej linków, tym większy punkt).
  - Dynamiczne podświetlanie powiązań po najechaniu myszką.

## 🚀 Jak uruchomić?
Odpalsz `src/visualizer.py`, który:
1. Pobiera topologię z SQLite.
2. Przygotowuje dane JSON.
3. Startuje lokalny serwer i otwiera `output/map.html`.

## 📂 Pliki klucze
- `data/wiki_graph.db` - Twoja lokalna kopia powiązań Wikipedii.
- `src/processor.py` - Silnik importu SQL -> SQLite.
- `output/map.html` - Finałowa wizualizacja.
