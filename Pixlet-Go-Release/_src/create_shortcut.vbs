' VBScript para criar atalho com ícone personalizado
' Salve como create_shortcut.vbs e execute: cscript create_shortcut.vbs

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Configuração
strDesktop = objShell.SpecialFolders("Desktop")
strRepoDir = "%REPO_DIR_PLACEHOLDER%"
strQtBrowser = strRepoDir & "\qt_browser.py"
strIcon = strRepoDir & "\Pixlet.ico"
strPython = "%PYTHON_EXE_PLACEHOLDER%"
strShortcutPath = strDesktop & "\Pixlet Browser.lnk"

' Criar atalho
Set objLink = objShell.CreateShortcut(strShortcutPath)
objLink.TargetPath = strPython
objLink.Arguments = strQtBrowser
objLink.WorkingDirectory = strRepoDir
objLink.Description = "Pixlet Browser - Navegador embarcado"
objLink.WindowStyle = 1

' Aplicar ícone se existir
If objFSO.FileExists(strIcon) Then
    objLink.IconLocation = strIcon
End If

' Guardar atalho
objLink.Save

' Mensagem de sucesso
MsgBox "Atalho criado com sucesso: " & strShortcutPath, vbInformation, "Pixlet Browser"
