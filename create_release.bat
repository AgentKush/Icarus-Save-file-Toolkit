@echo off
cd /d "C:\Users\finla\Documents\GitHub\Icarus-Save-file-Toolkit"
echo Creating release...
gh release create v1.0.0 --title "v1.0.0 - Save Editor + Image Extractor v7" --notes-file RELEASE_NOTES.md
echo.
echo Uploading bundle zip (this may take a minute)...
gh release upload v1.0.0 "Icarus-Toolkit-Bundle.zip" --clobber
echo.
echo Done!
pause
