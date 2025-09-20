@echo off
REM Windows build script for background.cpp
REM Requires Visual Studio Build Tools or MinGW-w64

echo Building background.cpp...

REM Check if Visual Studio compiler is available
where cl >nul 2>nul
if %errorlevel% == 0 (
    echo Using Visual Studio compiler...
    cl /EHsc /std:c++11 background.cpp /Fe:background.exe
    goto :end
)

REM Check if MinGW-w64 is available
where g++ >nul 2>nul
if %errorlevel% == 0 (
    echo Using MinGW-w64 compiler...
    g++ -std=c++11 -Wall -Wextra -O2 -o background.exe background.cpp -lcurl -ljsoncpp
    goto :end
)

REM Check if Clang is available
where clang++ >nul 2>nul
if %errorlevel% == 0 (
    echo Using Clang compiler...
    clang++ -std=c++11 -Wall -Wextra -O2 -o background.exe background.cpp -lcurl -ljsoncpp
    goto :end
)

echo No C++ compiler found!
echo Please install one of the following:
echo - Visual Studio Build Tools
echo - MinGW-w64
echo - Clang
echo.
echo For MinGW-w64, you can download from: https://www.mingw-w64.org/
echo For Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/
goto :end

:end
if exist background.exe (
    echo Build successful! Executable: background.exe
) else (
    echo Build failed!
)
pause
