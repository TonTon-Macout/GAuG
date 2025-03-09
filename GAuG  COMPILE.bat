@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: Имя исходного файла Python
set "SOURCE_FILE=GZIP_ARRAY_UnGZIP.py"
:: Имя итогового exe файла (без версии пока)
set "BASE_NAME=GAuG_v"

:: Извлечение версии из файла
for /f "tokens=2 delims==" %%v in ('findstr /B "VERSION" %SOURCE_FILE%') do (
    set "VERSION=%%v"
)
:: Удаление пробелов и кавычек из версии
set "VERSION=%VERSION: =%"
set "VERSION=%VERSION:"=%"

:: Полное имя exe файла
set "EXE_NAME=%BASE_NAME%%VERSION%.exe"

:: Проверка, найден ли номер версии
if "%VERSION%"=="" (
    echo Ошибка: Не удалось найти версию в файле %SOURCE_FILE%. Ожидается строка вида "VERSION = X.Y"
    exit /b 1
)

:: Компиляция с PyInstaller
echo Компиляция %SOURCE_FILE% в %EXE_NAME%...
pyinstaller --onefile --clean -n %EXE_NAME% %SOURCE_FILE%

:: Удаление временных файлов
echo Удаление временных файлов...
rd /s /q build
del /q %EXE_NAME%.spec

:: Проверка успешности компиляции
if exist "dist\%EXE_NAME%" (
    echo Компиляция завершена успешно! Файл: dist\%EXE_NAME%
    :: Перемещение exe в текущую директорию
    move "dist\%EXE_NAME%" .
    rd /s /q dist
) else (
    echo Ошибка: Компиляция не удалась.
    exit /b 1
)

echo Готово!
pause