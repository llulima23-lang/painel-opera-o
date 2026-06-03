$WshShell = New-Object -ComObject WScript.Shell
$StartupFolder = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$ShortcutPath = Join-Path $StartupFolder "PainelOperacaoWatcher.lnk"
$TargetPath = "c:\Users\sup.luciana\Desktop\AntiGravity\PAINEL OPERAÇÃO\INICIAR_MONITORAMENTO.bat"
$WorkingDir = "c:\Users\sup.luciana\Desktop\AntiGravity\PAINEL OPERAÇÃO"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $WorkingDir
$Shortcut.IconLocation = "shell32.dll, 238"
$Shortcut.Save()

Write-Host "Atalho de inicialização criado com sucesso em: $ShortcutPath"
