param(
    [string]$Python = 'python'
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

Push-Location $ProjectRoot
try {
    & $Python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw 'Runtime dependency installation failed.'
    }

    & $Python -m pip install -r requirements-dev.txt
    if ($LASTEXITCODE -ne 0) {
        throw 'Build dependency installation failed.'
    }

    & $Python -m PyInstaller --noconfirm --clean CodexTierWidget.spec
    if ($LASTEXITCODE -ne 0) {
        throw 'EXE build failed.'
    }

    $Executable = Join-Path $ProjectRoot 'dist\CodexTierWidget.exe'
    if (-not (Test-Path -LiteralPath $Executable)) {
        throw 'Build completed but dist\CodexTierWidget.exe was not found.'
    }

    $Checksum = (Get-FileHash -LiteralPath $Executable -Algorithm SHA256).Hash.ToLower()
    $ChecksumFile = Join-Path $ProjectRoot 'dist\CodexTierWidget.sha256'
    "$Checksum  CodexTierWidget.exe" | Set-Content -LiteralPath $ChecksumFile -Encoding ascii

    Write-Host "Build completed: $Executable"
    Write-Host "Checksum: $ChecksumFile"
}
finally {
    Pop-Location
}
