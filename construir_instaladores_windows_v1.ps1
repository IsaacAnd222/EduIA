$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$raizProyecto = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $raizProyecto

$archivosNecesarios = @(
    ".\instalador_cliente_eduia_v1.iss",
    ".\instalador_servidor_eduia_v1.iss",
    ".\dist\EduIA\EduIA.exe",
    ".\dist\EduIA\configuracion_cliente.json",
    ".\dist\ServidorEduIA\ServidorEduIA.exe",
    ".\dist\ServidorEduIA\configuracion_servidor.json"
)

foreach ($archivo in $archivosNecesarios) {
    if (-not (Test-Path $archivo -PathType Leaf)) {
        throw "Falta el archivo requerido: $archivo"
    }
}

$candidatosCompilador = @()
$comandoIscc = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue

if ($comandoIscc) {
    $candidatosCompilador += $comandoIscc.Source
}

$carpetasProgramas = @(
    ${env:ProgramFiles(x86)},
    $env:ProgramFiles,
    "$env:LOCALAPPDATA\Programs"
) | Where-Object { $_ -and (Test-Path $_ -PathType Container) }

foreach ($carpetaProgramas in $carpetasProgramas) {
    $carpetasInno = Get-ChildItem `
        -Path $carpetaProgramas `
        -Directory `
        -Filter "Inno Setup *" `
        -ErrorAction SilentlyContinue

    foreach ($carpetaInno in $carpetasInno) {
        $rutaIscc = Join-Path $carpetaInno.FullName "ISCC.exe"
        if (Test-Path $rutaIscc -PathType Leaf) {
            $candidatosCompilador += $rutaIscc
        }
    }
}

$compiladorInno = $candidatosCompilador |
    Sort-Object -Unique -Descending |
    Select-Object -First 1

if (-not $compiladorInno) {
    throw "No se encontro Inno Setup. Instalalo y vuelve a ejecutar este archivo."
}

Write-Host "Compilador: $compiladorInno" -ForegroundColor DarkGray
New-Item -ItemType Directory -Path ".\installer" -Force | Out-Null

Write-Host "Construyendo el instalador del cliente..." -ForegroundColor Cyan
& $compiladorInno ".\instalador_cliente_eduia_v1.iss"
if ($LASTEXITCODE -ne 0) {
    throw "No fue posible construir el instalador del cliente."
}

Write-Host "Construyendo el instalador del servidor..." -ForegroundColor Cyan
& $compiladorInno ".\instalador_servidor_eduia_v1.iss"
if ($LASTEXITCODE -ne 0) {
    throw "No fue posible construir el instalador del servidor."
}

Write-Host ""
Write-Host "INSTALADORES CONSTRUIDOS CORRECTAMENTE" -ForegroundColor Green
Write-Host "Cliente:  $raizProyecto\installer\EduIA_Cliente_Setup_v1.8.0.exe"
Write-Host "Servidor: $raizProyecto\installer\EduIA_Servidor_Setup_v1.8.0.exe"
