@echo off
REM ===================================================================
REM GitHub Push Script - E-newspaper Platform
REM ===================================================================
REM This script will:
REM 1. Check Git status
REM 2. Stage all changes
REM 3. Commit with timestamp
REM 4. Force push to replace old code
REM ===================================================================

echo.
echo ===================================================================
echo  E-newspaper - GitHub Deployment Script
echo ===================================================================
echo.

REM Check if Git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

REM Navigate to project directory
cd /d "%~dp0"

echo [Step 1/6] Checking Git status...
echo.
git status
echo.

REM Check if there are changes
git diff --quiet
if %ERRORLEVEL% EQU 0 (
    git diff --cached --quiet
    if %ERRORLEVEL% EQU 0 (
        echo [INFO] No changes to commit. Working tree is clean.
        pause
        exit /b 0
    )
)

echo.
echo [Step 2/6] Staging all changes...
git add .
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to stage changes
    pause
    exit /b 1
)
echo [OK] All changes staged
echo.

REM Get current timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%dt:~0,4%-%dt:~4,2%-%dt:~6,2% %dt:~8,2%:%dt:~10,2%"

echo [Step 3/6] Creating commit...
git commit -m "Production ready deployment - %timestamp%"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to create commit
    pause
    exit /b 1
)
echo [OK] Commit created
echo.

echo [Step 4/6] Checking remote repository...
git remote -v
echo.

REM Check if remote exists
git remote get-url origin >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [SETUP] No remote repository configured.
    echo.
    echo Please add your GitHub repository:
    echo   git remote add origin https://github.com/kashif2798/Et-Gen-AI-hackathon-26.git
    echo.
    pause
    exit /b 1
)

echo [Step 5/6] Fetching remote changes...
git fetch origin
echo.

echo.
echo ===================================================================
echo  WARNING: Force Push
echo ===================================================================
echo This will REPLACE all code in the remote repository!
echo The old code will be permanently deleted.
echo.
echo Remote repository: https://github.com/kashif2798/Et-Gen-AI-hackathon-26
echo Branch: main
echo.
set /p confirm="Are you sure you want to continue? (yes/no): "

if /i not "%confirm%"=="yes" (
    echo.
    echo [CANCELLED] Push operation cancelled by user.
    pause
    exit /b 0
)

echo.
echo [Step 6/6] Force pushing to GitHub...
echo.

git push --force origin main
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Push failed. Possible reasons:
    echo   - Network connection issue
    echo   - Authentication failed
    echo   - Repository URL is incorrect
    echo.
    echo Please check your credentials and try again.
    echo.
    echo If you need to set up authentication:
    echo   1. Generate a Personal Access Token at: https://github.com/settings/tokens
    echo   2. Use the token as your password when pushing
    echo.
    pause
    exit /b 1
)

echo.
echo ===================================================================
echo  SUCCESS! Code pushed to GitHub
echo ===================================================================
echo.
echo Your code is now available at:
echo https://github.com/kashif2798/Et-Gen-AI-hackathon-26
echo.
echo Next steps:
echo   1. Visit your GitHub repository
echo   2. Deploy frontend to Vercel
echo   3. Deploy backend to Railway
echo   4. See DEPLOYMENT_GUIDE.md for details
echo.
pause
