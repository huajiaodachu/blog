@echo off
cd /d "%~dp0"
echo 正在重新生成网站...
python build.py
if errorlevel 1 (
  echo.
  echo 【出错】请确认电脑已安装 Python，且本文件夹完整。
  echo 若不会弄，直接把要发的文章发给我，我来帮你生成。
)
echo.
echo 生成完成，刷新过的网页在 public\ 文件夹里。
pause
