<#
.SYNOPSIS
    Baut TPF3 Map Studio als .exe und packt das Release-Paket.

.DESCRIPTION
    1. baut mit PyInstaller (build.spec) nach dist\TPF3-Map-Studio
    2. prueft, dass die .exe und die Symbole im Paket liegen
    3. legt START-HIER.txt, LICENSE und THIRD_PARTY_NOTICES.md (und, falls vorhanden, den Ordner
       licenses) neben die .exe, damit sie gleich sichtbar sind
    4. packt den ganzen Ordner als TPF3-Map-Studio-v<Version>-win64.zip
    5. schreibt die SHA-256-Pruefsumme daneben

    Aufruf im Projektordner (die virtuelle Umgebung .venv muss existieren):
    powershell -ExecutionPolicy Bypass -File tools\make_release.ps1 -Version 0.3.0
#>

param(
    [string]$Version = "0.3.0"
)

$ErrorActionPreference = "Stop"

# tools\ -> Projektordner
Set-Location -Path (Split-Path -Parent $PSScriptRoot)

$python = ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "Die virtuelle Umgebung .venv fehlt. Bitte zuerst die Schritte 1 bis 5 der Anleitung im README ausfuehren."
}

Write-Host "PyInstaller installieren/pruefen..."
& $python -m pip install --quiet pyinstaller
if ($LASTEXITCODE -ne 0) { throw "pip install pyinstaller ist fehlgeschlagen." }

Write-Host "Baue die .exe (das dauert einige Minuten)..."
& $python -m PyInstaller build.spec --noconfirm
if ($LASTEXITCODE -ne 0) { throw "PyInstaller ist fehlgeschlagen." }

$app = "dist\TPF3-Map-Studio"

if (-not (Test-Path "$app\TPF3-Map-Studio.exe")) {
    throw "TPF3-Map-Studio.exe wurde nicht gebaut."
}

# Die Symbole muessen im Paket liegen (Studio-Oberflaeche und Karte)
$icons = @(Get-ChildItem $app -Recurse -Filter "strassen_hell.png")
if ($icons.Count -lt 2) {
    throw "Die Symbole fehlen im Paket (gefunden: $($icons.Count), erwartet: 2). Prueft build.spec (datas)."
}

# Dateien neben die .exe legen (START-HIER.txt, Lizenz, Quellenangaben)
foreach ($file in @("tools\START-HIER.txt", "LICENSE", "THIRD_PARTY_NOTICES.md")) {
    if (-not (Test-Path $file)) {
        throw "Datei fehlt: $file"
    }
    Copy-Item $file $app -Force
}

if (Test-Path "licenses") {
    Copy-Item "licenses" "$app\licenses" -Recurse -Force
}

$zip = "TPF3-Map-Studio-v$Version-win64.zip"

if (Test-Path $zip) { Remove-Item $zip }

Write-Host "Packe $zip ..."
Compress-Archive -Path $app -DestinationPath $zip

$hash = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
$sizeMb = [math]::Round((Get-Item $zip).Length / 1MB, 1)

Set-Content -Path "$zip.sha256.txt" -Value "$hash  $zip" -Encoding ascii

Write-Host ""
Write-Host "Fertig."
Write-Host "  Datei:     $zip ($sizeMb MB)"
Write-Host "  SHA-256:   $hash"
Write-Host "  Naechster Schritt: auf GitHub unter Releases ein neues Release v$Version anlegen und die ZIP anhaengen."
