@echo off
cd /d "C:\Users\finla\Documents\GitHub\Icarus-Save-file-Toolkit"
dotnet build "Icarus Toolkit.sln" --nologo -v q 2>&1
echo EXIT_CODE=%ERRORLEVEL%
