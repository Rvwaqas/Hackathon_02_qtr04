# Install Helm for Windows
$ErrorActionPreference = "Stop"

$helmUrl = "https://get.helm.sh/helm-v3.17.1-windows-amd64.zip"
$downloadPath = "$env:TEMP\helm.zip"
$extractPath = "$env:USERPROFILE\helm"

Write-Host "Creating directory..." -ForegroundColor Cyan
if (-not (Test-Path $extractPath)) {
    New-Item -Path $extractPath -ItemType Directory -Force | Out-Null
}

Write-Host "Downloading Helm..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $helmUrl -OutFile $downloadPath -UseBasicParsing

Write-Host "Extracting..." -ForegroundColor Cyan
Expand-Archive -Path $downloadPath -DestinationPath $extractPath -Force

Write-Host "Finding helm.exe..." -ForegroundColor Cyan
$helmExe = Get-ChildItem -Path $extractPath -Recurse -Filter "helm.exe" | Select-Object -First 1
Write-Host "Helm location: $($helmExe.FullName)" -ForegroundColor Green

# Add to PATH for current session
$helmDir = $helmExe.DirectoryName
$env:PATH = "$helmDir;$env:PATH"

# Verify
Write-Host "Verifying installation..." -ForegroundColor Cyan
& $helmExe.FullName version
