# Process Hollowing
Technika wstrzykiwania kodu (Code Injection), polegająca na:
1. Uruchomieniu legalnego procesu w stanie zawieszenia (Suspended).
2. Wyczyszczeniu jego pamięci (Unmapping).
3. Wpisaniu złośliwego kodu w miejsce oryginału.
4. Wznowieniu wątku.

**Przykład użycia:** Zaobserwowano w projekcie [[CERT-bomberV2]], gdzie celem był proces `AddInProcess32.exe`.
**Obrona:** ETW, monitoring wywołań API `NtWriteVirtualMemory`.
