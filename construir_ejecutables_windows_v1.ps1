$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$raizProyecto = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $raizProyecto

Write-Host "Verificando archivos necesarios..." -ForegroundColor Cyan

$archivosNecesarios = @(
    ".\main.py",
    ".\servidor_eduia.py",
    ".\EduIA_Cliente_v1.spec",
    ".\EduIA_Servidor_v1.spec",
    ".\assets\logo_eduia.png",
    ".\assets\icono_eduia.ico",
    ".\configuracion_cliente.json",
    ".\configuracion_servidor.json"
)

foreach ($archivo in $archivosNecesarios) {
    if (-not (Test-Path $archivo -PathType Leaf)) {
        throw "Falta el archivo requerido: $archivo"
    }
}

python -c "import PyInstaller" 2>$null
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller no está instalado en el entorno virtual activo."
}

Write-Host "Construyendo el cliente EduIA..." -ForegroundColor Cyan
python -m PyInstaller --noconfirm --clean ".\EduIA_Cliente_v1.spec"
if ($LASTEXITCODE -ne 0) {
    throw "No fue posible construir EduIA.exe."
}

Write-Host "Construyendo el servidor central..." -ForegroundColor Cyan
python -m PyInstaller --noconfirm --clean ".\EduIA_Servidor_v1.spec"
if ($LASTEXITCODE -ne 0) {
    throw "No fue posible construir ServidorEduIA.exe."
}

Copy-Item ".\configuracion_cliente.json" ".\dist\EduIA\configuracion_cliente.json" -Force
Copy-Item ".\configuracion_servidor.json" ".\dist\ServidorEduIA\configuracion_servidor.json" -Force

Write-Host "" 
Write-Host "EJECUTABLES CONSTRUIDOS CORRECTAMENTE" -ForegroundColor Green
Write-Host "Cliente:  $raizProyecto\dist\EduIA\EduIA.exe"
Write-Host "Servidor: $raizProyecto\dist\ServidorEduIA\ServidorEduIA.exe"
