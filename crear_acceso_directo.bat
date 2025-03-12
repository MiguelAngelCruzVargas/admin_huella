@echo off
setlocal enabledelayedexpansion

:: Configuracion inicial
title Creador de Acceso Directo Python
color 0A

:: ==============================================================
:: PASO 1: Solicitar información básica
:: ==============================================================

:: Detectar escritorio (funciona en cualquier idioma)
for /f "tokens=*" %%a in ('powershell -Command "[Environment]::GetFolderPath('Desktop')"') do (
    set "desktop_path=%%a"
)

echo ========================================================
echo    CREADOR DE ACCESO DIRECTO PARA APLICACION PYTHON
echo ========================================================
echo Escritorio detectado en: %desktop_path%
echo.

:: ==============================================================
:: PASO 2: Seleccionar archivos y carpetas
:: ==============================================================

:: Seleccionar carpeta del proyecto
echo Seleccione la carpeta raiz del proyecto:
set /p dummy=Presione Enter para abrir el selector de carpeta...
for /f "tokens=*" %%a in ('powershell -Command "Add-Type -AssemblyName System.Windows.Forms; $FolderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog; $FolderBrowser.Description = 'Seleccione la carpeta raiz del proyecto'; $FolderBrowser.ShowDialog() | Out-Null; $FolderBrowser.SelectedPath"') do (
    set "project_path=%%a"
)

if "%project_path%"=="" (
    echo No se selecciono ninguna carpeta. Operacion cancelada.
    goto :EOF
)
echo Carpeta del proyecto: %project_path%
echo.

:: Seleccionar archivo Python
echo Seleccione el archivo Python que desea ejecutar:
set /p dummy=Presione Enter para abrir el selector de archivos...
for /f "tokens=*" %%a in ('powershell -Command "Add-Type -AssemblyName System.Windows.Forms; $FileBrowser = New-Object System.Windows.Forms.OpenFileDialog; $FileBrowser.InitialDirectory = '%project_path%'; $FileBrowser.Filter = 'Archivos Python (*.py)|*.py'; $FileBrowser.ShowDialog() | Out-Null; $FileBrowser.FileName"') do (
    set "python_file=%%a"
)

if "%python_file%"=="" (
    echo No se selecciono ningun archivo. Operacion cancelada.
    goto :EOF
)
echo Archivo Python: %python_file%
echo.

:: Seleccionar icono
echo Seleccione el archivo de icono (.ico):
set /p dummy=Presione Enter para abrir el selector de archivos...
for /f "tokens=*" %%a in ('powershell -Command "Add-Type -AssemblyName System.Windows.Forms; $FileBrowser = New-Object System.Windows.Forms.OpenFileDialog; $FileBrowser.InitialDirectory = '%project_path%'; $FileBrowser.Filter = 'Archivos de Icono (*.ico)|*.ico'; $FileBrowser.ShowDialog() | Out-Null; $FileBrowser.FileName"') do (
    set "icon_path=%%a"
)

if "%icon_path%"=="" (
    echo No se selecciono ningun icono. Operacion cancelada.
    goto :EOF
)
echo Archivo de icono: %icon_path%
echo.

:: Solicitar nombre del acceso directo
echo Ingrese el nombre para el acceso directo:
set /p app_name=Nombre: 

if "%app_name%"=="" (
    echo No se ingreso un nombre. Usando "Aplicacion Python" como nombre predeterminado.
    set "app_name=Aplicacion Python"
)

:: ==============================================================
:: PASO 3: Seleccionar versión de Python
:: ==============================================================

echo.
echo Seleccione la version de Python a utilizar:
echo 1. Usar Python 3.8.10 (recomendado)
echo 2. Buscar Python en una ubicacion especifica
echo 3. Usar Python predeterminado del sistema
set /p python_choice=Opcion (1-3): 

set "pythonw_path=pythonw.exe"

if "%python_choice%"=="1" (
    echo Configurando para usar Python 3.8.10...
    set "pythonw_path=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python38\pythonw.exe"
    
    :: Verificar si el archivo existe
    if not exist "!pythonw_path!" (
        set "pythonw_path=C:\Python38\pythonw.exe"
        if not exist "!pythonw_path!" (
            echo No se encontro Python 3.8.10 en la ubicacion estandar.
            echo Por favor, seleccione manualmente la ubicacion del ejecutable pythonw.exe
            set "python_choice=2"
        )
    )
)

if "%python_choice%"=="2" (
    echo Seleccione el archivo pythonw.exe de su instalacion de Python:
    set /p dummy=Presione Enter para abrir el selector de archivos...
    for /f "tokens=*" %%a in ('powershell -Command "Add-Type -AssemblyName System.Windows.Forms; $FileBrowser = New-Object System.Windows.Forms.OpenFileDialog; $FileBrowser.Filter = 'Ejecutable Python (pythonw.exe)|pythonw.exe'; $FileBrowser.ShowDialog() | Out-Null; $FileBrowser.FileName"') do (
        set "pythonw_path=%%a"
    )
    
    if "!pythonw_path!"=="" (
        echo No se selecciono ninguna version de Python. Usando la version predeterminada.
        set "pythonw_path=pythonw.exe"
    )
)

echo Usando Python de: !pythonw_path!
echo.

:: ==============================================================
:: PASO 4: Crear el acceso directo
:: ==============================================================

:: Verificar si el acceso directo ya existe
if exist "%desktop_path%\%app_name%.lnk" (
    echo.
    echo ADVERTENCIA: Ya existe un acceso directo con este nombre.
    choice /c SN /m "Desea sobrescribirlo? (S/N)"
    if errorlevel 2 (
        echo Operacion cancelada.
        goto :EOF
    )
    del /f /q "%desktop_path%\%app_name%.lnk" 2>nul
)

:: Crear carpeta oculta para el script de ejecución
set "script_dir=%APPDATA%\PyShortcuts\%app_name%"
if not exist "%script_dir%" mkdir "%script_dir%" 2>nul

:: Crear script bat que ejecuta el Python
echo @echo off > "%script_dir%\run.bat"
echo cd /d "%project_path%" >> "%script_dir%\run.bat"
echo start "" "!pythonw_path!" "%python_file%" >> "%script_dir%\run.bat"

:: Crear acceso directo usando VBScript (más confiable)
echo Creando acceso directo...
echo Set WshShell = CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo Set lnk = WshShell.CreateShortcut("%desktop_path%\%app_name%.lnk") >> "%TEMP%\CreateShortcut.vbs"
echo lnk.TargetPath = "%script_dir%\run.bat" >> "%TEMP%\CreateShortcut.vbs"
echo lnk.WorkingDirectory = "%project_path%" >> "%TEMP%\CreateShortcut.vbs"
echo lnk.IconLocation = "%icon_path%" >> "%TEMP%\CreateShortcut.vbs"
echo lnk.WindowStyle = 7 >> "%TEMP%\CreateShortcut.vbs"
echo lnk.Description = "%app_name% (Python)" >> "%TEMP%\CreateShortcut.vbs"
echo lnk.Save >> "%TEMP%\CreateShortcut.vbs"
cscript //nologo "%TEMP%\CreateShortcut.vbs"
del "%TEMP%\CreateShortcut.vbs" 2>nul

:: Ocultar la carpeta del script
attrib +h "%script_dir%" /s /d 2>nul

:: Verificar que se haya creado correctamente
if exist "%desktop_path%\%app_name%.lnk" (
    echo.
    echo ========================================================
    echo    ACCESO DIRECTO CREADO EXITOSAMENTE
    echo ========================================================
    echo Nombre: %app_name%
    echo Ubicacion: %desktop_path%
    echo Python: !pythonw_path!
    echo Script: %python_file%
    echo.
    echo Ya puede hacer doble clic en el icono para ejecutar su aplicacion.
) else (
    echo.
    echo ERROR: No se pudo crear el acceso directo.
    echo Por favor, ejecute este script como administrador e intente nuevamente.
)

echo.
pause