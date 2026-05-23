Add-Type -AssemblyName System.Drawing

$sourcePath = "c:\Users\ravir\Desktop\bd modern\stitch_modern_claymorphic_school_portal\school portal\pwa-icon.jpg"
$dest192 = "c:\Users\ravir\Desktop\bd modern\stitch_modern_claymorphic_school_portal\school portal\pwa-icon-192.png"
$dest512 = "c:\Users\ravir\Desktop\bd modern\stitch_modern_claymorphic_school_portal\school portal\pwa-icon-512.png"

$img = [System.Drawing.Image]::FromFile($sourcePath)

# 192x192
$bmp192 = New-Object System.Drawing.Bitmap 192, 192
$g192 = [System.Drawing.Graphics]::FromImage($bmp192)
$g192.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g192.DrawImage($img, 0, 0, 192, 192)
$bmp192.Save($dest192, [System.Drawing.Imaging.ImageFormat]::Png)
$g192.Dispose()
$bmp192.Dispose()

# 512x512
$bmp512 = New-Object System.Drawing.Bitmap 512, 512
$g512 = [System.Drawing.Graphics]::FromImage($bmp512)
$g512.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g512.DrawImage($img, 0, 0, 512, 512)
$bmp512.Save($dest512, [System.Drawing.Imaging.ImageFormat]::Png)
$g512.Dispose()
$bmp512.Dispose()

$img.Dispose()

Write-Output "Successfully generated 192x192 and 512x512 PNGs!"
