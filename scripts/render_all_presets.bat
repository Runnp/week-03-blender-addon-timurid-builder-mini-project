@echo off
REM render_all_presets.bat
REM Renders all 4 presets at MID LOD with tile materials to demo_renders/
REM
REM Usage: render_all_presets.bat [path\to\blender.exe]
REM Default blender path assumes it's on PATH.

set BLENDER=%1
if "%BLENDER%"=="" set BLENDER=blender
 
set SCRIPT=%~dp0scripts\headless_render.py
set OUTDIR=%~dp0demo_renders
 
echo [Registan] Rendering Timurid...
%BLENDER% --background --python "%SCRIPT%" -- --preset Timurid  --lod MID --tiles --outdir "%OUTDIR%"
 
echo [Registan] Rendering Bukharan...
%BLENDER% --background --python "%SCRIPT%" -- --preset Bukharan --lod MID --tiles --outdir "%OUTDIR%"
 
echo [Registan] Rendering Safavid...
%BLENDER% --background --python "%SCRIPT%" -- --preset Safavid  --lod MID --tiles --outdir "%OUTDIR%"
 
echo [Registan] Rendering Minimal...
%BLENDER% --background --python "%SCRIPT%" -- --preset Minimal  --lod LOW         --outdir "%OUTDIR%"
 
echo [Registan] All renders complete. Output: %OUTDIR%
pause
 
