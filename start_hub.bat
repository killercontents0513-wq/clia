@echo off
chcp 65001 >nul
title LG AI Content Hub Launcher

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║     LG AI Content Hub  — 시작 중...      ║
echo  ╚══════════════════════════════════════════╝
echo.

:: 현재 디렉토리 설정
cd /d "%~dp0"

:: Node.js 확인
where node >nul 2>&1
if %errorlevel% neq 0 (
  echo  [오류] Node.js가 설치되어 있지 않습니다.
  echo  https://nodejs.org 에서 설치 후 재시도하세요.
  pause
  exit /b 1
)

:: 이미 서버 실행 중인지 확인 (포트 3001)
netstat -ano | find ":3001 " | find "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
  echo  ✅ 서버가 이미 실행 중입니다 (port 3001)
  goto open_html
)

:: node_modules 확인
if not exist "node_modules" (
  echo  📦 패키지 설치 중...
  npm install --silent
  if %errorlevel% neq 0 (
    echo  [오류] npm install 실패
    pause
    exit /b 1
  )
)

:: 서버 백그라운드 시작
echo  🚀 크롤 서버 시작 중 (port 3001)...
start "CLIA Crawl Server" /min node server.js

:: 서버 준비 대기
timeout /t 2 /nobreak >nul

:open_html
echo  🌐 브라우저에서 Content Hub 열기...
start "" "LG_AI_Content_Hub_v6_23.html"

echo.
echo  ✅ 완료! 브라우저에서 Content Hub가 열립니다.
echo  ✅ Make 탭 → eBay 크롤 → URL 입력 → Crawl
echo.
echo  ℹ️  이 창을 닫아도 서버는 계속 실행됩니다.
echo  ℹ️  서버 종료: 작업 관리자에서 "CLIA Crawl Server" 종료
echo.
timeout /t 5 /nobreak >nul
exit /b 0
