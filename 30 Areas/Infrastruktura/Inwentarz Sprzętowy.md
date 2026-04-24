# Infrastruktura: Home Lab & PC

## 💻 Stacja Robocza (PC)
- **CPU:** [[AMD Ryzen 5 5500]] (6 rdzeni)
- **GPU:** [[NVIDIA GeForce RTX 4070]]
- **RAM:** 16 GB
- **OS:** Windows 11 (win32)

## 🖥️ Serwer: Dell PowerEdge R630 (server-lisia)
- **IP:** `192.168.1.24`
- **Dostęp:** Skonfigurowany klucz SSH (`id_ed25519`) - logowanie bezhasłowe aktywne.
- **CPU:** 2x [[Intel Xeon E5-2630 v3]] @ 2.40GHz
- **RAM:** 32 GB (użycie: ~20GB)
- **OS:** Ubuntu 24.04 LTS (Kernel 6.17)

### 📦 Kluczowe Kontenery ([[Docker]])
- **AI:** `open-webui` (port 3000), `jupyter-server`.
- **Media:** `immich-server` (zdjęcia, port 2283).
- **Gry:** `minecraft-zhrzg` (port 25565), `beammp-server`.
- **Sieć:** `mailcow` (pełny stack pocztowy), `cloudflare-tunnel`, `searxng`.
- **Zarządzanie:** `portainer`, `duplicati` (backupy), `glances`.

### ⚠️ Do sprawdzenia (Alerts)
- [ ] `cloudflare-ddns`: Ciągłe restarty.
- [ ] `immich-postgres`: Status unhealthy.

---
*Ostatnia synchronizacja: 2026-04-24*
