param(
    [string]$PlantUmlJar = (Join-Path $PSScriptRoot '..\.tools\plantuml.jar'),
    [string]$JavaExe = 'java'
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$diagramRoot = Join-Path $repoRoot 'docs\diagrams\uml'

if (-not (Test-Path -LiteralPath $PlantUmlJar -PathType Leaf)) {
    throw "PlantUML JAR not found: $PlantUmlJar"
}

$sources = Get-ChildItem -LiteralPath $diagramRoot -Recurse -Filter '*.puml' -File
if (-not $sources) {
    throw "No .puml source found in: $diagramRoot"
}

foreach ($source in $sources) {
    & $JavaExe -jar $PlantUmlJar -charset UTF-8 -failfast2 -tpng $source.FullName
    if ($LASTEXITCODE -ne 0) { throw "PNG render failed: $($source.FullName)" }
    & $JavaExe -jar $PlantUmlJar -charset UTF-8 -failfast2 -tsvg $source.FullName
    if ($LASTEXITCODE -ne 0) { throw "SVG render failed: $($source.FullName)" }
}

Write-Output "Rendered $($sources.Count) diagram(s) in $diagramRoot"
