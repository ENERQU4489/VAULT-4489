# 🧠 Vexa-C Project Memory (2026-05-27)

## ✅ CO DZIAŁA (Status: STABLE)
- **Silnik CUDA FP16/FP32**: Mixed Precision działa. Wagi w FP16, akumulacja gradientów i stany AdamW w FP32. Oszczędność VRAM na RTX 4070 potwierdzona.
- **Word-Level Tokenizer**: Skrypt Python poprawnie buduje słownik (5000+ słów) i eksportuje binarne dane (`vocab.bin`, `data.bin`).
- **Autograd (Backward Pass)**: Udowodniona zbieżność matematyczna. Model potrafi uczyć się na pamięć (Overfitting Test Passed: "created by Michal").
- **AdamW Optimizer**: Własny kernel CUDA działa stabilnie, nie dopuszcza do eksplozji wag przy odpowiednim LR (0.0001 - 0.0005).
- **Zintegrowany Pipeline Trinity**: Plik `vexa_all_in_one.cu` łączy trening i inferencję, eliminując błędy przesyłu wag.

## ❌ CO NIE DZIAŁA / DO POPRAWY (Status: TODO)
- **Multi-Head Attention (MHA)**: W ostatniej wersji Trinity została uproszczona/wyłączona dla debugowania Head-a. Należy przywrócić pełną pętlę warstw atencji z poprawnym backwardem.
- **Problem "Kropek" (Statistical Bias)**: Model przy dużych datasetach (Szekspir) wpada w pułapkę najczęstszych znaków. Wymaga wdrożenia `Token Blocking` dla interpunkcji lub dłuższego treningu.
- **Repetitive Looping**: Model zapętla się ("created by Michal created by..."). Rozwiązanie: Wdrożenie tokena `EOS` (End Of Sentence) i mechanizmu `KV Cache` dla lepszej generacji.
- **GGUF Export**: Obecny zapis to surowy binairek. Trzeba dopisać nagłówek GGUF v3, aby pliki były czytane przez profesjonalne narzędzia.

## 🎯 CEL NA JUTRO
1. Reintegracja pełnego bloku **VexaAttention** (MHA + WavePos).
2. Trening na zbalansowanym zbiorze (Shakespeare + Identity) z użyciem tokena **EOS**.
3. Implementacja **Temperature Sampling** z prawdziwym **Repetition Penalty**.

[[SYSTEM]]
