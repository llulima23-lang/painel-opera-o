@echo off
:: Muda para a pasta onde o arquivo .bat esta localizado
cd /d "%~dp0"

:: Inicia o watcher em modo silencioso (sem janela)
start /b pythonw watcher.pyw

:: Sai da janela de comando
exit
