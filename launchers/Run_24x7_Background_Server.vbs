' VBScript to launch live_price_server.py silently in background without terminal window
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\.."
WshShell.Run "python live_price_server.py", 0, False
Set WshShell = Nothing
