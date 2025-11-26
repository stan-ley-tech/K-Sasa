# K-Sasa: Hugging Face Cache Cleanup & Setup (Windows)

# 1️⃣ Define the default HF datasets cache path
$hfLocalAppData = $env:LOCALAPPDATA
$hfCachePath = Join-Path $hfLocalAppData "huggingface\datasets"
Write-Host "HF datasets cache folder path: $hfCachePath"

# 2️⃣ Create the datasets folder if it does not exist
if (-Not (Test-Path $hfCachePath)) {
    New-Item -ItemType Directory -Path $hfCachePath -Force | Out-Null
    Write-Host "Created HF datasets cache folder at: $hfCachePath"
} else {
    Write-Host "HF datasets cache folder already exists."
}

# 3️⃣ Delete old FLORES caches (if any)
$floresPattern = "facebook___flores*"
$floresCacheItems = Get-ChildItem -Path $hfCachePath -Directory -Filter $floresPattern -ErrorAction SilentlyContinue

if ($null -eq $floresCacheItems -or $floresCacheItems.Count -eq 0) {
    Write-Host "No FLORES cached datasets found to delete."
} else {
    foreach ($item in $floresCacheItems) {
        Remove-Item -Recurse -Force $item.FullName
        Write-Host "Deleted cached dataset: $($item.FullName)"
    }
}

# 4️⃣ Delete old LAFAND caches (if any)
$lafandPattern = "davlan___lafand*"
$lafandCacheItems = Get-ChildItem -Path $hfCachePath -Directory -Filter $lafandPattern -ErrorAction SilentlyContinue

if ($null -eq $lafandCacheItems -or $lafandCacheItems.Count -eq 0) {
    Write-Host "No LAFAND cached datasets found to delete."
} else {
    foreach ($item in $lafandCacheItems) {
        Remove-Item -Recurse -Force $item.FullName
        Write-Host "Deleted cached dataset: $($item.FullName)"
    }
}

# 5️⃣ Verify cache folder
Write-Host "`nHF datasets cache folder is ready for fresh downloads."
Write-Host "Full path: $hfCachePath"
