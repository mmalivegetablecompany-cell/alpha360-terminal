$WshShell = New-Object -comObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Alpha360 Terminal.lnk"

$ExePath = "d:\New folder (5)\Alpha360_Terminal.exe"
$IconPath = "d:\New folder (5)\flutter_app\windows\runner\resources\app_icon.ico"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $ExePath
$Shortcut.WorkingDirectory = "d:\New folder (5)"
$Shortcut.Description = "Alpha360 - Institutional Indian Equities Terminal"
$Shortcut.IconLocation = "$IconPath,0"
$Shortcut.Save()

Write-Host "✅ Desktop shortcut created successfully at: $ShortcutPath" -ForegroundColor Green
