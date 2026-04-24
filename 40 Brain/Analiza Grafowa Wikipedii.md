# 🕸️ Analiza Grafowa Wikipedii

Przetwarzanie Wikipedii jako grafu pozwala na zrozumienie struktury ludzkiej wiedzy.

## 📊 Dane techniczne (plwiki)
- **Liczba artykułów**: ~2.3 mln
- **Liczba linków**: ~119 mln
- **Format dumpów**: SQL (`page`, `pagelinks`)

## 🛠️ Stack projektu [[20 Projects/WikiSfera/README|WikiSfera]]
1. **SQLite**: Służy jako silnik do JOINowania ID z tytułami.
2. **NetworkX**: Implementacja algorytmu `spring_layout` (Fruchterman-Reingold).
3. **Sigma.js**: Renderowanie po stronie klienta (Canvas/WebGL).

## 💡 Wnioski
- Największe skupiska (huby) to zazwyczaj: Geografia (Państwa), Czas (Lata/Dni), oraz Biografia.
- Grafy o takiej skali wymagają redukcji (np. top N wierzchołków) dla zachowania płynności wizualizacji.
