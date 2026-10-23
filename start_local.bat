@echo off
chcp 65001 > nul
echo ==============================================
echo    자소서 메이트 (Jaso-Mate) 로컬 실행기
echo ==============================================
echo.
echo 로컬 서버를 시작합니다...
echo 브라우저가 자동으로 열립니다. (http://localhost:8000)
echo.
python server.py
if errorlevel 1 (
    echo.
    echo [오류] Python 실행 중 에러가 발생했습니다.
    pause
)
