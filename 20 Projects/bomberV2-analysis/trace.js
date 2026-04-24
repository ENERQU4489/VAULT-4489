// Automatycznie przechwytuj moment, w którym program prosi o nową pamięć
Interceptor.attach(Module.findExportByName(null, "VirtualAlloc"), {
    onLeave: function (retval) {
        var addr = retval;
        // Zrzucamy pierwsze 16 bajtów nowej pamięci, żeby sprawdzić co tam wpisano
        console.log("[AUTOMAT] Nowa pamięć pod: " + addr);
        try {
            console.log(hexdump(addr, { length: 16, header: false, ansi: true }));
        } catch(e) {}
    }
});