# 📦 Стандартные библиотеки Python
import os
import sys
import time
import struct
import shutil
import zipfile
import datetime
import socket
import math
import re
import logging
from typing import Optional, List, Tuple, Dict, Any, Union
from collections import deque
import configparser
import webbrowser

# 🌐 Настройка Qt API
os.environ['QT_API'] = 'pyside6'

APP_VERSION = "2.3.0"
STABLE_VERSION = "2.3.0"
GITHUB_REPO   = "NorfaRu/NorfaTelemtry"

# ДЛЯ ТОГО ЧТОБЫ СОБРАТЬ ФАЙЛ В ТЕРМИНАЛЕ:
# pyinstaller tw.py --onefile --windowed --icon=logo.ico --upx-dir=upx-5.0.0-win64

from PySide6.QtCore import QPropertyAnimation, QObject, QMetaObject
from PySide6.QtGui  import QGuiApplication
from PySide6.QtWidgets import QMessageBox
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtCore import QUrl

from PySide6.QtGui import QShortcut
from PySide6.QtGui import QKeySequence

# 🖼️ PySide6 — Виджеты и интерфейс
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QGridLayout,
    QSizePolicy, QTextEdit, QLineEdit, QCheckBox, QFileDialog, QScrollArea,
    QGraphicsDropShadowEffect, QSpinBox, QStatusBar, QProgressBar
)

from PySide6.QtGui    import QDrag, QMouseEvent, QDropEvent, QDragEnterEvent, QDragMoveEvent
from PySide6.QtCore   import QByteArray, QMimeData
from PySide6.QtWidgets import QPlainTextEdit, QComboBox

# 🔄 Qt Core — Сигналы, Слоты, Таймеры, Потоки
from qtpy.QtCore import (
    Qt, QThread, Signal, Slot, QTimer, QRect
)


# 🎨 Qt GUI — Графика и Стили
from qtpy.QtGui import (
    QPalette, QColor, QFont, QPainter, QPen
)

from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat
from PySide6.QtCore import QRegularExpression

# 📈 Qt Charts — Графики
from qtpy.QtCharts import (
    QChart, QChartView, QLineSeries, QValueAxis
)

# 📊 PyQtGraph — Быстрая 2D и 3D визуализация
from pyqtgraph.opengl import MeshData

# === ПАРАМЕТРЫ ПАРСЕРА ===
#DEBUG = False
PL, R0 = 1000, 4000
NAKLON, SMESHENIE = -0.7565, 1.269
SCALE = math.pow(10, -SMESHENIE / NAKLON)
STRUCT_FMT = "<2HIhI6hBHBH4h3fB3HB"  # 60 bytes

# === ЦВЕТОВАЯ СХЕМА ===
COLORS = {
    "bg_main": "#1a1a1a",         # Main background (darker)
    "bg_dark": "#121212",         # Sidebar/darker areas
    "bg_card": "#252525",         # Card backgrounds
    "bg_panel": "#202020",        # Panel backgrounds
    "accent": "#81c784",         # светло-зелёный
    "accent_darker": "#66bb6a",  # чуть темнее
    "btn_normal": "#333333",      # Button normal state
    "btn_hover": "#444444",       # Button hover state
    "btn_active": "#555555",      # Button active state
    "text_primary": "#ffffff",    # Main text
    "text_secondary": "#aaaaaa",  # Secondary text
    "text_highlight": "#4fc3f7",  # Highlighted text (same as accent)
    "success": "#81c784",         # Success color
    "warning": "#ffb74d",         # Warning color
    "danger": "#e57373",          # Danger/error color
    "info": "#64b5f6",            # Info color
    "chart_grid": "#3a3a3a",      # Chart grid lines
    "chart_bg": "#242424"        # Chart background (slightly lighter than dark bg)
}

def version_tuple(v: str):
    """Преобразует строку 'v1.2.3' или '1.2.3' в кортеж (1,2,3)."""
    try:
        return tuple(int(x) for x in v.lstrip('vV').split('.'))
    except:
        return ()

def check_for_update():
        """Возвращает (True, download_url, latest_tag) если есть новая версия."""
        try:
            # Use a slightly longer timeout and allow redirects
            r = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest", timeout=5, allow_redirects=True)
            r.raise_for_status() # Raises HTTPError for bad responses (4XX, 5XX)
            data = r.json()
            latest = data.get("tag_name", "")
            # Ensure version comparison works even if tags have 'v' prefix
            if latest and version_tuple(latest) > version_tuple(APP_VERSION):
                for asset in data.get("assets", []):
                    # Look specifically for .exe files
                    if asset.get("name", "").lower().endswith(".exe"):
                        url = asset.get("browser_download_url")
                        if url:
                            print(f"[Update] Found new version {latest} at {url}")
                            return True, url, latest
                        else:
                            print("[Update] Found .exe asset but no download URL.")
                print(f"[Update] Found new version {latest} but no suitable .exe asset.")
            else:
                 print(f"[Update] No new version found (Current: {APP_VERSION}, Latest on GitHub: {latest})")

        except requests.exceptions.Timeout:
            print("[Update Check Error] Request timed out.")
        except requests.exceptions.ConnectionError as e:
            print(f"[Update Check Error] Connection error: {e}")
        except requests.exceptions.HTTPError as e:
            print(f"[Update Check Error] HTTP error: {e.response.status_code} {e.response.reason}")
        except requests.exceptions.JSONDecodeError:
            print("[Update Check Error] Failed to parse JSON response from GitHub API.")
        except Exception as e:
            # Catch any other unexpected errors during the update check
            print(f"[Update Check Error] An unexpected error occurred: {e}")

        return False, "", ""

import requests # Make sure requests is imported near the top
import tempfile # Make sure tempfile is imported near the top
import textwrap # Make sure textwrap is imported near the top
import ctypes   # Make sure ctypes is imported near the top

class UpdateThread(QThread):
        step = Signal(str)
        progress = Signal(int, int)
        finished = Signal(bool, str)  # (success, error_message)
        # Signal emitted right before quitting the app to apply update
        update_starting = Signal(str)

        def __init__(self, download_url, parent=None):
            super().__init__(parent)
            self.download_url = download_url

        def run(self):
            temp_dir = tempfile.gettempdir()
            # Use a more unique name for the downloaded file
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            new_exe_path = os.path.join(temp_dir, f"tw_update_{timestamp}.exe")
            # Use PowerShell script instead of batch
            updater_script_path = os.path.join(temp_dir, f"tw_updater_{timestamp}.ps1")
            log_file_path = os.path.join(temp_dir, f"tw_update_{timestamp}.log") # Log for the script

            try:
                # 1) Download the update
                self.step.emit("Начинаем загрузку обновления…")
                # Use requests for downloading as well, provides better control
                with requests.get(self.download_url, stream=True, timeout=30, allow_redirects=True) as r:
                    r.raise_for_status()
                    total_size = int(r.headers.get('content-length', 0))
                    downloaded_size = 0

                    dl_mb = total_size / (1024 * 1024) if total_size else 0
                    self.step.emit(f"Размер обновления: {dl_mb:.2f} МБ")

                    with open(new_exe_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk: # filter out keep-alive new chunks
                                f.write(chunk)
                                downloaded_size += len(chunk)
                                if total_size > 0:
                                    self.progress.emit(downloaded_size, total_size)

                dl_done_mb = downloaded_size / (1024 * 1024)
                self.step.emit(f"Загрузка завершена: {dl_done_mb:.2f} МБ")

                # 2) Prepare the PowerShell updater script
                self.step.emit("Подготовка установщика…")
                # Determine the correct path for the current executable
                if getattr(sys, 'frozen', False):
                    # If running as a bundled app (pyinstaller)
                    current_exe = sys.executable
                else:
                     # If running as a script
                    current_exe = os.path.abspath(sys.argv[0])

                pid = os.getpid()

                powershell_script = textwrap.dedent(f"""
                param(
                    [Parameter(Mandatory=$true)][int]$PidToWait,
                    [Parameter(Mandatory=$true)][string]$NewExePath,
                    [Parameter(Mandatory=$true)][string]$TargetExePath,
                    [Parameter(Mandatory=$true)][string]$LogFilePath
                )

                function Write-Log($message) {{
                    "[{{0}}] $message" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | Out-File -Append -Encoding UTF8 -FilePath $LogFilePath
                }}

                Write-Log "Updater script started."
                Write-Log " - NewExe: $NewExePath"
                Write-Log " - Target: $TargetExePath"
                Write-Log " - Log: $LogFilePath"
                Write-Log "Waiting for main process (PID: $PidToWait) to exit..."

                $process = Get-Process -Id $PidToWait -ErrorAction SilentlyContinue
                if ($process) {{
                    Wait-Process -Id $PidToWait -Timeout 30 # Wait up to 30 seconds
                    Start-Sleep -Milliseconds 500 # Brief pause after process *should* have exited
                    $process = Get-Process -Id $PidToWait -ErrorAction SilentlyContinue # Check again
                    if ($process) {{
                        Write-Log "Error: Main process did not exit within 30 seconds. Attempting to terminate."
                        try {{ Stop-Process -Id $PidToWait -Force -ErrorAction Stop }} catch {{ Write-Log "Failed to terminate process: $($_.Exception.Message)"}}
                        Start-Sleep -Milliseconds 500 # Pause after trying termination
                    }} else {{
                         Write-Log "Main process exited."
                    }}
                }} else {{
                    Write-Log "Main process (PID: $PidToWait) already exited or not found."
                }}

                # Extra check for file existence
                if (-not (Test-Path $NewExePath)) {{
                    Write-Log "Error: Downloaded file $NewExePath not found!"
                    Exit 1
                }}
                 if (-not (Test-Path $TargetExePath)) {{
                    Write-Log "Warning: Target file $TargetExePath not found (might be running from unexpected location?). Update will still proceed to place new file."
                    # Consider if this case should abort
                }}


                Write-Log "Attempting to replace '$TargetExePath' with '$NewExePath'..."

                try {{
                    # Ensure target directory exists
                    $TargetDir = Split-Path $TargetExePath -Parent
                    if (-not (Test-Path $TargetDir)) {{
                        Write-Log "Creating target directory: $TargetDir"
                        New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
                    }}
                    Move-Item -Path $NewExePath -Destination $TargetExePath -Force -ErrorAction Stop
                    Write-Log "Update successful: '$TargetExePath' replaced."
                }} catch {{
                    Write-Log "Error replacing file: $($_.Exception.Message)"
                    # Attempt to clean up the downloaded file even on error
                    if (Test-Path $NewExePath) {{ Remove-Item -Path $NewExePath -Force -ErrorAction SilentlyContinue }}
                    Write-Log "Update failed."
                    Exit 1 # Indicate failure
                }}

                Write-Log "Attempting to start the new version: '$TargetExePath'"
                try {{
                    Start-Process -FilePath $TargetExePath -WorkingDirectory (Split-Path $TargetExePath -Parent) -ErrorAction Stop
                    Write-Log "New version started."
                }} catch {{
                    Write-Log "Error starting new version: $($_.Exception.Message)"
                    # Don't exit here, let the script clean up first
                }}

                Write-Log "Update process finished. Cleaning up updater script..."
                # Self-delete the script
                Remove-Item -Path $MyInvocation.MyCommand.Path -Force -ErrorAction SilentlyContinue
                Exit 0 # Indicate success
                """)

                # Write the script file
                with open(updater_script_path, "w", encoding="utf-8") as f:
                    f.write(powershell_script)
                self.step.emit("Установщик готов.")

                # 3) Launch the PowerShell script (potentially elevated)
                self.step.emit("Запуск установщика (может потребоваться разрешение Администратора)…")
                try:
                    # Command to execute: powershell.exe -ExecutionPolicy Bypass -File "<script_path>" -PidToWait <pid> -NewExePath "<new_exe>" -TargetExePath "<current_exe>" -LogFilePath "<log_path>"
                    command_line = f'-ExecutionPolicy Bypass -File "{updater_script_path}" -PidToWait {pid} -NewExePath "{new_exe_path}" -TargetExePath "{current_exe}" -LogFilePath "{log_file_path}"'

                    # Use ShellExecuteW to request elevation if needed ('runas')
                    ret = ctypes.windll.shell32.ShellExecuteW(
                        None,
                        "runas",        # Verb: requests elevation
                        "powershell.exe", # Executable
                        command_line,   # Command line arguments
                        None,           # Working directory (None for current)
                        1               # Show command (SW_SHOWNORMAL)
                    )

                    # Check return code: > 32 indicates success in launching
                    if ret > 32:
                        self.step.emit("Установщик запущен. Приложение сейчас перезапустится.")
                        # Emit signal *before* quitting
                        self.update_starting.emit("Перезапуск для обновления...")
                        # Initiate clean application shutdown
                        QTimer.singleShot(500, QApplication.quit) # Short delay before quitting
                    else:
                        # User might have cancelled UAC prompt or other error
                        error_code = ctypes.get_last_error() # Get error if ShellExecute failed intrinsically
                        error_map = { 0: "The operating system is out of memory or resources.", 2: "The specified file was not found.", 3: "The specified path was not found.", 5: "Access denied.", 8: "Not enough memory resources are available to process this command.", 31: "No application is associated with the specified file name extension.", 1155: "No application is associated (alternate code).", 1223: "The operation was canceled by the user (UAC prompt)." }
                        error_msg = f"Не удалось запустить установщик. Код ошибки: {ret} (WinErr: {error_code} - {error_map.get(error_code, 'Unknown error')})"
                        print(f"[Update Error] {error_msg}")
                        self.step.emit(error_msg)
                        # Clean up downloaded file if script launch failed
                        if os.path.exists(new_exe_path): os.remove(new_exe_path)
                        if os.path.exists(updater_script_path): os.remove(updater_script_path)
                        self.finished.emit(False, error_msg)

                except Exception as e:
                     # Catch errors during script launch preparation/execution call
                    error_msg = f"Ошибка при запуске установщика: {e}"
                    print(f"[Update Error] {error_msg}")
                    self.step.emit(error_msg)
                    # Clean up downloaded file
                    if os.path.exists(new_exe_path): os.remove(new_exe_path)
                    if os.path.exists(updater_script_path): os.remove(updater_script_path)
                    self.finished.emit(False, error_msg)

            except requests.exceptions.RequestException as e:
                error_msg = f"Ошибка загрузки обновления: {e}"
                print(f"[Update Error] {error_msg}")
                self.step.emit(error_msg)
                # Clean up potentially partially downloaded file
                if os.path.exists(new_exe_path): os.remove(new_exe_path)
                self.finished.emit(False, error_msg)
            except IOError as e:
                error_msg = f"Ошибка записи файла обновления: {e}"
                print(f"[Update Error] {error_msg}")
                self.step.emit(error_msg)
                if os.path.exists(new_exe_path): os.remove(new_exe_path)
                self.finished.emit(False, error_msg)
            except Exception as e:
                # Generic catch-all for other errors during the process
                error_msg = f"Непредвиденная ошибка при обновлении: {e}"
                print(f"[Update Error] {error_msg}")
                self.step.emit(error_msg)
                # Clean up any temp files if they exist
                if os.path.exists(new_exe_path): os.remove(new_exe_path)
                if os.path.exists(updater_script_path): os.remove(updater_script_path)
                self.finished.emit(False, error_msg)

@Slot(str, str)
def _prompt_update(self, latest, url): # Keep url argument for compatibility, but don't use it directly for download
    mb = QMessageBox(self)
    mb.setWindowTitle("Доступно обновление")
    mb.setText(f"Найдена версия {latest} (у вас {APP_VERSION}). Открыть страницу загрузки?") # Changed text slightly
    mb.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    reply = mb.exec()
    if reply == QMessageBox.Yes:
        # Open the GitHub releases page in the browser
        releases_url = f"https://github.com/{GITHUB_REPO}/releases"
        print(f"[Splash] Opening GitHub releases page: {releases_url}")
        try:
            webbrowser.open(releases_url)
            self.loading_step.emit("Открываем страницу загрузки в браузере…") # Update status briefly
        except Exception as e:
            print(f"[Splash] Error opening browser: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть браузер. Посетите:\n{releases_url}")
        # Proceed to launch the main application after opening the browser or showing error
        self._launch_main()

        # Remove the old UpdateThread logic:
        # # Сбросить прогресс и показать бар
        # self.update_pb.setValue(0)
        # self.update_pb.show()
        #
        # self.upd_thread = UpdateThread(url) # url is the specific asset download URL, which we no longer use directly here
        # # текстовые шаги на статус-лейбл
        # self.upd_thread.step.connect(self.loading_step)
        # # обновление прогресса
        # self.upd_thread.progress.connect(
        #     lambda done, total: self.update_pb.setValue(int(done * 100 / total) if total else 0)
        # )
        # # по завершении *неудачного* обновления — скрыть прогресс-бар и показать ошибку
        # self.upd_thread.finished.connect(self._on_update_finished)
        # # Когда скрипт обновления запущен, показать сообщение перед выходом
        # self.upd_thread.update_starting.connect(self.loading_step) # Update status label
        # # Add a specific connection for the final message before quit
        # self.upd_thread.update_starting.connect(lambda msg: print(f"[Splash] {msg}"))
        # self.upd_thread.start()
        # # Don't return here, let the splash screen stay visible until update starts or fails
    else:
        print("[Splash] Пользователь отказался от обновления, запускаем приложение.")
        self._launch_main()

class SpinnerWidget(QWidget):
    def __init__(self, parent=None, radius=20, line_width=4):
        super().__init__(parent)
        self.radius = radius
        self.line_width = line_width
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timeout)
        self.timer.start(100)
        self.setFixedSize(radius * 2 + line_width * 2, radius * 2 + line_width * 2)

    def _on_timeout(self):
        self.angle = (self.angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        center = rect.center()
        p.translate(center)
        # + Рисуем статичный круг
        pen = QPen(QColor(COLORS["accent"]), self.line_width)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QRect(-self.radius, -self.radius, 2*self.radius, 2*self.radius))

        # + Вращающаяся полоска
        p.rotate(self.angle)
        p.setPen(QPen(QColor(COLORS["accent"]), self.line_width))
        pen = QPen(QColor(COLORS["accent"]), self.line_width)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.drawArc(QRect(-self.radius, -self.radius, 2*self.radius, 2*self.radius),
                  0 * 16, 90 * 16)  # 90° дуга

class SplashScreen(QWidget):
    loading_step = Signal(str)      # сигнал для обновления текста

    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # главный контейнер со стилем из вашей темы
        main = QWidget(self)
        main.setStyleSheet(f"""
            background-color: {COLORS['bg_dark']};
            border-radius: 20px;
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0,0,0,180))
        main.setGraphicsEffect(shadow)

        v = QVBoxLayout(main)
        v.setContentsMargins(30,30,30,30)
        v.setSpacing(15)

        title = QLabel("GRIB Telemetry Dashboard")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['accent']};")
        title.setAlignment(Qt.AlignCenter)
        v.addWidget(title)

        self.spinner = SpinnerWidget(self, radius=30, line_width=6)
        v.addWidget(self.spinner, alignment=Qt.AlignCenter)

        # здесь будем писать, что грузим
        self.status_label = QLabel("Подготовка…")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self.status_label.setAlignment(Qt.AlignCenter)
        # + Перенос строк, чтобы длинный текст влезал
        self.status_label.setWordWrap(True)
        v.addWidget(self.status_label)
        # ниже self.status_label: прогресс-бар для обновления
        self.update_pb = QProgressBar()
        self.update_pb.setRange(0, 100)
        self.update_pb.setValue(0)
        # показывать текст процентов и формат %p%
        self.update_pb.setTextVisible(True)
        self.update_pb.setFormat("%p%")
        v.addWidget(self.update_pb)
        self.update_pb.hide()

        # увеличиваем размер окна, чтобы прогресс-бар и текст влезали
        self.resize(700, 450)
        # сразу ставим "main" на весь размер сплэша
        main.resize(self.size())
        main.move(0, 0)

        # подпишемся на шаги загрузки
        self.loading_step.connect(self.status_label.setText)

        # + Создаём MainWindow сразу в главном потоке (но не показываем)
        self.main = MainWindow(self.config)  # Передаем конфигурацию в MainWindow
        # + Теперь запускаем фоновые задачи (только не-UI!) через InitWorker
        QTimer.singleShot(100, self._start_initialization)

    def show(self):
        super().show()
        self.center()
    def center(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        geom   = self.frameGeometry()
        geom.moveCenter(screen.center())
        self.move(geom.topLeft())
        # подгоняем главный контейнер под новое окно
        if hasattr(self, 'update_pb'):
            # main уже подогнан в __init__, но на всякий случай
            for w in self.children():
                if isinstance(w, QWidget) and w is not self:
                    w.resize(self.size()); w.move(0, 0)

    def _start_initialization(self):
        # Запускаем инициализацию в отдельном потоке, чтобы UI спиннера не подвис
        self.init_thread = QThread()
        # + Передаём ссылку на созданное окно в InitWorker
        self.init_worker = InitWorker(self.main)
        self.init_worker.moveToThread(self.init_thread)
        self.init_worker.step.connect(self.loading_step)
        self.init_worker.finished.connect(self._on_init_finished)
        self.init_thread.started.connect(self.init_worker.run)
        self.init_thread.start()

    @Slot(str, str)
    def _prompt_update(self, latest, url):
        mb = QMessageBox(self)
        mb.setWindowTitle("Доступно обновление")
        mb.setText(f"Найдена версия {latest} (у вас {APP_VERSION}). Открыть страницу загрузки?")
        mb.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        reply = mb.exec()
        if reply == QMessageBox.Yes:
            # Open the GitHub releases page in the browser
            releases_url = f"https://github.com/{GITHUB_REPO}/releases"
            print(f"[Splash] Opening GitHub releases page: {releases_url}")
            try:
                webbrowser.open(releases_url)
                self.loading_step.emit("Открываем страницу загрузки в браузере…")
            except Exception as e:
                print(f"[Splash] Error opening browser: {e}")
                QMessageBox.warning(self, "Ошибка", f"Не удалось открыть браузер. Посетите:\n{releases_url}")
            # Proceed to launch the main application after opening the browser or showing error
            self._launch_main()
        else:
            print("[Splash] Пользователь отказался от обновления, запускаем приложение.")
            self._launch_main()

    @Slot(object)
    def _on_init_finished(self):
        print("[Splash] Инициализация закончена, проверяем обновления…")
        self.init_thread.quit()
        self.init_thread.wait()

        avail, url, tag = check_for_update()
        if avail:
            print(f"[Splash] Есть новая версия {tag}, передаём в _prompt_update")
            self._prompt_update(tag, url)
            return

        print("[Splash] Обновлений нет — запускаем главное окно")
        self._launch_main()

    @Slot(bool, str)
    def _on_update_finished(self, success: bool, msg: str):
        print(f"[Splash] UpdateThread finished signal received: success={success}, msg={msg}")
        self.update_pb.hide()
        if not success:
            QMessageBox.critical(self, "Ошибка обновления", msg)
            # If update failed, proceed to launch the current version
            print("[Splash] Update failed, launching current version.")
            self._launch_main()
        # If success=True, it means the script was launched and the app will quit separately via update_starting signal + QTimer.
        # No need to call _launch_main() here in the success case.

    def _launch_main(self):
        print("[SplashScreen] Переходим к главному окну.")
        self.close()
        self.main.worker.start()
        self.main.show()

    def showEvent(self, event):
        super().showEvent(event)
        # центрируем сплэш окно
        self.adjustSize()
        screen = QGuiApplication.primaryScreen().availableGeometry()
        geom   = self.frameGeometry()
        geom.moveCenter(screen.center())
        self.move(geom.topLeft())

class InitWorker(QObject):
    step = Signal(str)
    finished = Signal()
    # + сигнал для передачи готовой MeshData в TestPage
    mesh_ready = Signal(object)

    # + Добавляем __init__, чтобы получить MainWindow
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window

    @Slot()
    def run(self):
        # + 1) Запускаем TelemetryWorker (UI-объект main.worker уже создан в главном потоке)
        self.step.emit("Запускаем телеметрию…")
        QMetaObject.invokeMethod(self.main.worker, "start", Qt.QueuedConnection)
        QThread.msleep(1000)

        # + 3) Любые другие тяжёлые не-UI задачи…
        self.step.emit("Выполняем пред-загрузку данных…")
        # …например чтение конфигов, подготовка массивов и т.п.
        QThread.msleep(1000)

        # 4) Завершаем
        self.step.emit("Готово, запускаем приложение…")
        QThread.msleep(500)
        # — убираем передачу несуществующей переменной main
        self.finished.emit()

class ExportLogsThread(QThread):
    finished = Signal(str, bool, str)

    def __init__(self, log_dir: str, parent=None):
        super().__init__(parent)
        self.log_dir = log_dir


    def run(self):
        # проверим, что папка существует и есть файлы
        if not os.path.isdir(self.log_dir):
            self.finished.emit("", False, f"Directory not found: {self.log_dir}")
            return
        files = [f for f in os.listdir(self.log_dir) if os.path.isfile(os.path.join(self.log_dir,f))]
        if not files:
            self.finished.emit("", False, f"No files in {self.log_dir} to zip")
            return
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        archive = os.path.join(self.log_dir, f"logs_{now}.zip")
        try:
            with zipfile.ZipFile(archive, 'w') as z:
                for fn in files:
                    z.write(os.path.join(self.log_dir, fn), arcname=fn)
            self.finished.emit(archive, True, "")
        except Exception as e:
            self.finished.emit("", False, str(e))

# === WORKER ДЛЯ UART + UDP + ЛОГОВ + CRC-ОШИБОК ===
class TelemetryWorker(QThread):
    data_ready    = Signal(dict)
    packet_ready  = Signal(list)
    log_ready     = Signal(str)
    error_crc     = Signal()
    sim_ended     = Signal()
    simulation_progress = Signal(int, int)
    def __init__(self, config, port_name="COM3", baud=9600, parent=None):
        super().__init__(parent)
        self.config = config
        self.packet_format = config["packet_structure"]["format"]
        self.fields = config["packet_structure"]["fields"]
        import time
        # Для Mahony AHRS
        self.qw, self.qx, self.qy, self.qz = 1.0, 0.0, 0.0, 0.0
        self.Kp, self.Ki = 1.0, 0.0   # Ki=0 → никакого «накопления»
        self.int_fb_x = self.int_fb_y = self.int_fb_z = 0.0
        self.last_fuse_time = time.time()
        self.last_data_time = None
        self.sim_f = None
        # для дросселя CRC‑варнингов
        self.last_crc_warning = 0.0
        self.crc_cooldown    = 1.0   # не более 1 варнинга в секунду
        self.port_name = port_name
        self.baud = baud
        self._running = True
        self._paused = False
        # UDP по умолчанию
        self.udp_enabled = False
        self.udp_host = "127.0.0.1"
        self.udp_port = 5005
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Для режима имитации
        self.sim_enabled   = False
        self.sim_file_path = ""
        # Логи
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs("log", exist_ok=True)
        self.bin_path = f"log/grib_{now}.bin"
        self.csv_path = f"log/grib_{now}.csv"
        self.f_bin = open(self.bin_path, "ab")
        self.f_csv = open(self.csv_path, "w", encoding="utf-8")
        headers = [f"field_{i}" for i in range(len(struct.unpack(STRUCT_FMT, b'\x00'*60)))]
        self.f_csv.write(";".join(headers) + "\n")

        #from functools import reduce
        #import operator
        #def xor_block(self, data: bytes) -> int:
            #return reduce(operator.xor, data, 0)
    def xor_block(self, data: bytes) -> int:
            res = 0
            for b in data:
                res ^= b
            return res

    @Slot(bool, str)
    def update_simulation(self, enabled, file_path):
        """Настройки режима имитации из файла."""
        # Закрываем старый дескриптор, если открыт
        if hasattr(self, 'sim_f') and self.sim_f:
            try:
                self.sim_f.close()
            except:
                pass
            self.sim_f = None

            """Переключить файл симуляции без гонок и I/O-блокировок."""
            # остановить прежнюю симуляцию и закрыть файл, если открыт
            print(f"[SIM] TelemetryWorker.update_simulation(enabled={enabled}, path={file_path})")
            self.sim_enabled = False
            if hasattr(self, 'sim_f') and self.sim_f:
                try: self.sim_f.close()
                except: pass
                self.sim_f = None

            # установить новый файл и включить симуляцию
            self.sim_file_path = file_path
            try:
                self.sim_file_size = os.path.getsize(file_path)
            except:
                self.sim_file_size = None
            self.sim_enabled   = enabled
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log_ready.emit(f"[{ts}] Simulation set to {file_path}, enabled={enabled}")

    @Slot(bool, str, int)
    def update_udp(self, enabled, host, port):
        """Обновляем настройки UDP."""
        self.udp_enabled = enabled
        self.udp_host = host
        self.udp_port = port
        ts = datetime.datetime.now()

        # Закрываем старый и создаём новый сокет
        try:
            self.udp_socket.close()
        except Exception:
            pass
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.udp_socket.sendto(b"status", (self.udp_host, self.udp_port))

        self.log_ready.emit(f"[{ts}] UDP settings updated: enabled={enabled}, host={host}, port={port}")
        if enabled:
            try:
                self.udp_socket.bind(('', self.udp_port))
            except Exception as e:
                self.log_ready.emit(f"[ERROR] UDP bind failed: {e}")
                return
            self.udp_socket.sendto(b"status", (self.udp_host, self.udp_port))
            self.log_ready.emit(f"[{datetime.datetime.now()}] UDP bound to port {self.udp_port} and 'status' sent")
        else:
            self.log_ready.emit(f"[{datetime.datetime.now()}] UDP disabled; socket closed")

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def is_paused(self):
        return self._paused

    def stop(self):
        self._running = False
        # сразу закроем файлы, чтобы не блокировать FS
        try:
            if hasattr(self, 'f_bin') and not self.f_bin.closed: self.f_bin.close()
        except: pass
        try:
            if hasattr(self, 'f_csv') and not self.f_csv.closed: self.f_csv.close()
        except: pass

    def run(self):
        print("[SIM] Simulation thread started")
        print(f"[SIM] run() started: initial sim_enabled={self.sim_enabled}, udp_enabled={self.udp_enabled}")
        buf = b""
        self.log_ready.emit(f"Telemetry thread started. Version {APP_VERSION}")
        self.log_ready.emit(f"Надёжная версия: {STABLE_VERSION}")

        while self._running:
            try:
                sim, udp = self.sim_enabled, self.udp_enabled
                if sim and not udp:
                    # Режим симуляции
                    if not hasattr(self, 'sim_f') or self.sim_f is None:
                        self.sim_f = open(self.sim_file_path, 'rb')
                    rcv = self.sim_f.read(60)
                    # Эмитим прогресс (текущая позиция и размер)
                    pos = self.sim_f.tell()
                    if hasattr(self, "sim_file_size") and self.sim_file_size:
                        self.simulation_progress.emit(pos, self.sim_file_size)
                    if not rcv:
                        self.log_ready.emit("[SIM] End of file reached")
                        self.sim_ended.emit()
                        # отключаем симуляцию, закрываем файл и возвращаемся к началу цикла
                        self.sim_enabled = False
                        try: self.sim_f.close()
                        except: pass
                        self.sim_f = None
                        continue
                    # вместо time.sleep(1):
                    self.msleep(1000)
                else:
                    # Режим UDP
                    try:
                        rcv = self.udp_socket.recv(60*100)
                    except Exception as e:
                        continue
            except Exception as e:
                continue

            self.log_ready.emit(f"[DATA] Got {len(rcv)} bytes")
            buf += rcv

            if self._paused:
                continue

            while len(buf) >= 60:
                if buf[:2] == b"\xAA\xAA":
                    chunk = buf[:60]
                    try:
                        pkt = struct.unpack(self.packet_format, chunk)
                    except struct.error:
                        buf = buf[1:]
                        continue
                    if self.xor_block(chunk[:-1]) == pkt[-1]:
                        try:
                            # Динамическое формирование данных на основе конфигурации
                            data = {}
                            for field in self.fields:
                                if field["type"] == "vector3":
                                    indices = field["indices"]
                                    scale = field.get("scale", 1.0)
                                    data[field["name"]] = [pkt[i]*scale for i in indices]
                                elif field["type"] == "float":
                                    index = field["index"]
                                    scale = field.get("scale", 1.0)
                                    data[field["name"]] = pkt[index]*scale
                                elif field["type"] == "int" and "mask" in field:
                                    index = field["index"]
                                    mask = field["mask"]
                                    data[field["name"]] = pkt[index] & mask
                                elif field["type"] == "int":
                                    index = field["index"]
                                    data[field["name"]] = pkt[index]
                                # ... другие типы ...
                        
                            # ... остальной код обработки ...
                            self.data_ready.emit(data)
                            self.last_data_time = time.time()
                            if self.f_csv and not self.f_csv.closed:
                                self.f_csv.write(";".join(str(x) for x in pkt) + "\n")
                            self.f_bin.write(chunk)
                            buf = buf[60:]
                        except Exception as e:
                            self.log_ready.emit(f"[ERROR] Ошибка парсинга пакета: {e}")
                            buf = buf[60:]
                            continue
                    else:
                        self.error_crc.emit()
                        mw = QApplication.activeWindow()
                        if hasattr(mw, "notify"):
                            mw.notify("CRC mismatch", "warning")
                        buf = buf[1:]
                else:
                    buf = buf[1:]

                    # по выходу из цикла точно закроем
        if getattr(self, 'sim_f', None):
            try: self.sim_f.close()
            except: pass
        for fh in (getattr(self, 'f_bin', None), getattr(self, 'f_csv', None)):
            try:
                if fh and not fh.closed: fh.close()
            except: pass
            self.log_ready.emit(f"[{datetime.datetime.now()}] TelemetryWorker stopped")

    sim_ended = Signal()  # <-- новый сигнал

# === ТЁМНАЯ ТЕМА ===
def apply_dark_theme(app: QApplication):
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(COLORS["bg_main"]))
    pal.setColor(QPalette.WindowText, QColor(COLORS["text_primary"]))
    pal.setColor(QPalette.Base, QColor(COLORS["bg_panel"]))
    pal.setColor(QPalette.AlternateBase, QColor("#353535"))
    pal.setColor(QPalette.Text, QColor(COLORS["text_primary"]))
    pal.setColor(QPalette.Button, QColor(COLORS["btn_normal"]))
    pal.setColor(QPalette.ButtonText, QColor(COLORS["text_primary"]))
    pal.setColor(QPalette.Highlight, QColor(COLORS["accent"]))
    pal.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(pal)
    app.setStyle("Fusion")

    app.setStyleSheet(f"""
        /* Карточки со светящимся бэкграундом и тенью */
        QFrame#card {{
            border-radius: 12px;
            background-color: {COLORS['bg_dark']};
            border: 1px solid {COLORS['chart_grid']};
            padding: 16px;
        }}
        QFrame#card QCheckBox {{
            spacing: 8px;
            font-size: 10pt;
            color: {COLORS['text_primary']};
        }}
        QFrame#card QSpinBox {{
            min-width: 50px;
            font-size: 10pt;
            color: {COLORS['text_primary']};
            background: {COLORS['bg_panel']};
            border: 1px solid {COLORS['chart_grid']};
            border-radius: 4px;
            padding: 2px 4px;
        }}
        QPushButton#resetLayoutBtn {{
            background-color: {COLORS['btn_normal']};
            color: {COLORS['text_primary']};
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 10pt;
        }}
        QPushButton#resetLayoutBtn:hover {{
            background-color: {COLORS['accent_darker']};
        }}
        QPushButton#resetLayoutBtn:pressed {{
            background-color: {COLORS['accent']};
        }}
        QChartView {{
            border-radius: 12px;
            background-color: transparent;
        }}
        QScrollArea {{
            border-radius: 10px;
        }}
        QPushButton {{
            border: none;
            border-radius: 8px;
            padding: 8px 14px;
            background-color: {COLORS['btn_normal']};
            color: {COLORS['text_primary']};
        }}
        QPushButton:hover {{
            background-color: {COLORS['btn_hover']};
        }}
        QToolTip {{
            background-color: #202020;
            color: #ffffff;
            border: 1px solid #81c784;
            border-radius: 4px;
            padding: 4px;
            font-size: 10pt;
        }}
        QPushButton:pressed {{
            background-color: {COLORS['btn_active']};
        }}
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {COLORS['bg_panel']};
            border: 1px solid {COLORS['chart_grid']};
            border-radius: 6px;
            padding: 6px;
            color: {COLORS['text_primary']};
        }}
        QLabel {{
            font-size: 10.5pt;
        }}
    """)

# === СТРАНИЦА ТЕЛЕМЕТРИИ + ГРАФИКИ ===
class TelemetryPage(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self._last_values = {}
        
        layout = QGridLayout(self)
        layout.setSpacing(12)
        
        # --- кнопка Пауза/Возобновить ---
        self.pause_btn = QPushButton("⏸ Пауза")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.toggle_pause)
        layout.addWidget(self.pause_btn, 0, 0, 1, 2)
        
        # --- динамические поля из config["telemetry_view"] ---
        self._label_widgets = {}
        row = 1
        col = 0
        
        for f in config.get("telemetry_view", {}).get("fields", []):
            card = QFrame()
            card.setObjectName("card")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 8, 10, 8)
            
            title = QLabel(f.get("label", ""), objectName="title")
            value = QLabel("–", objectName="value")
            
            value.setAlignment(Qt.AlignCenter)
            value.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            card_layout.addWidget(title)
            card_layout.addWidget(value)
            
            layout.addWidget(card, row, col)
            self._label_widgets[f["source"]] = (value, f)
            
            # Move to next column or row
            col = (col + 1) % 2
            if col == 0:
                row += 1

    @Slot(dict)
    def update_values(self, data):
        self._last_values = data.copy() if data else {}

        if not self.pause_btn.isEnabled():
            self.pause_btn.setEnabled(True)

        for src, (label, field) in self._label_widgets.items():
            val = data.get(src)
            # Get the format string from the field config, default to '{}'
            fmt = field.get("format", "{}")
            text_to_set = "–" # Default text if value is None

            if val is not None:
                try:
                    if isinstance(val, (list, tuple)):
                        # Attempt to format the list/tuple using the provided format string
                        # This assumes the format string is compatible (e.g., "[{:.2f}, {:.2f}, {:.2f}]")
                        # A more robust solution might involve parsing the format string.
                        # For now, try direct formatting, fallback to simple join.
                        try:
                            # Special case for list/tuple: unpack elements if format allows
                            text_to_set = fmt.format(*val)
                        except (TypeError, IndexError):
                            # Fallback if format string expects a single value or wrong number of args
                            text_to_set = ", ".join(str(x) for x in val) # Original simple join
                    elif isinstance(val, (int, float)):
                        # Format single number
                        text_to_set = fmt.format(val)
                    else:
                        # Fallback for other types (string, bool, etc.)
                        text_to_set = fmt.format(val) # Try formatting anyway
                except Exception as e:
                    # Catch potential formatting errors (e.g., trying to format a non-number with {:.2f})
                    print(f"[TelemetryPage] Error formatting value for {src} (value: {val}, format: {fmt}): {e}")
                    text_to_set = f"Err: {val}" # Show error indicator instead of crashing

            # Update the label text
            label.setText(text_to_set)

    @Slot()
    def toggle_pause(self):
        if hasattr(self, 'worker'):
            if self.worker.is_paused():
                self.worker.resume()
                self.pause_btn.setText("⏸ Пауза")
            else:
                self.worker.pause()
                self.pause_btn.setText("▶ Продолжить")

    def set_worker(self, worker):
        self.worker = worker

class DraggableCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def mousePressEvent(self, ev: QMouseEvent):
        mime = QMimeData()
        # передаём адрес объекта
        mime.setData("application/x-card", QByteArray(str(id(self)).encode()))
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.MoveAction)

    def dragEnterEvent(self, ev: QDragEnterEvent):
        if ev.mimeData().hasFormat("application/x-card"):
            ev.acceptProposedAction()

    def dragMoveEvent(self, ev: QDragMoveEvent):
        if ev.mimeData().hasFormat("application/x-card"):
            ev.acceptProposedAction()

    def dropEvent(self, ev: QDropEvent):
        source = ev.source()
        target = self
        if isinstance(source, DraggableCard) and source is not target:
            layout = target.parent().layout()  # это QGridLayout

            # найдём позицию source и target
            idx_src = layout.indexOf(source)
            idx_tgt = layout.indexOf(target)
            r_src, c_src, _, _ = layout.getItemPosition(idx_src)
            r_tgt, c_tgt, _, _ = layout.getItemPosition(idx_tgt)

            # убираем виджеты из layout
            layout.removeWidget(source)
            layout.removeWidget(target)

            # ставим обратно на swapped позиции
            layout.addWidget(source, r_tgt, c_tgt)
            layout.addWidget(target, r_src, c_src)

        ev.acceptProposedAction()

class GraphsPage(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self._orig_pos = {}
        # Map series names to QLineSeries for updates
        self.series = {}
        layout = QGridLayout(self)
        self._detached_windows = {}
        # === System Monitor ===
        import psutil
        from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout
        self.sys_frame = QFrame()
        self.sys_frame.setObjectName("card")
        h = QHBoxLayout(self.sys_frame)
        self.cpu_label = QLabel("CPU: – %")
        self.ram_label = QLabel("RAM: – %")
        self.lat_label = QLabel("UDP Latency: – s")
        for lbl in (self.cpu_label, self.ram_label, self.lat_label):
            lbl.setStyleSheet("font-size:10pt; font-weight:bold;")
            h.addWidget(lbl)
        layout.addWidget(self.sys_frame, 0, 0, 1, 2)

        # таймер обновления
        from PySide6.QtCore import QTimer
        self.sys_timer = QTimer(self)
        self.sys_timer.timeout.connect(lambda: self._update_system_monitor(psutil))
        self.sys_timer.start(1000)
        # Оборачиваем сетку в прокручиваемую область
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True) # Revert to standard behavior
        content = QWidget()
        layout = QGridLayout(content)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll)
        scroll.setWidget(content)
        layout.setSpacing(12)
        self._grid_layout = self.findChild(QScrollArea).widget().layout()

        # Make the first two columns stretch equally
        self._grid_layout.setColumnStretch(0, 1)
        self._grid_layout.setColumnStretch(1, 1)
        # Explicitly prevent stretching of subsequent columns
        self._grid_layout.setColumnStretch(2, 0)

        # ежеминутный сброс, чтобы QLineSeries/ QSplineSeries не росли в C++
        self._cleanup_timer = QTimer(self)
        self._cleanup_timer.timeout.connect(self.reset_charts)
        self._cleanup_timer.start(60000)

        # Dictionary to store all chart views and series
        self.charts = {}
        self.indexes = {}
        self.data_points = {}  # Store maximum points to display
        self.data_history     = {}      # Имя -> список значений
        self.default_y_ranges = {}      # Имя -> исходный диапазон по Y
        self.last_extreme     = {}      # Имя -> время последнего выхода за пределы
        self.extreme_decay    = 5.0     # секунд до сброса к дефолтному диапазону

        # --- Load Saved Layout ---
        self._loaded_layout = {}
        try:
            cfg_parser = configparser.ConfigParser()
            # Read config.ini, ensuring the file exists
            if os.path.exists("config.ini"):
                cfg_parser.read("config.ini")
                if cfg_parser.has_section("Layout") and cfg_parser.has_option("Layout", "chart_positions"):
                    pos_str = cfg_parser.get("Layout", "chart_positions")
                    # Parse "name1:row1:col1,name2:row2:col2,..."
                    for item in pos_str.split(','):
                        parts = item.split(':')
                        if len(parts) == 3:
                            name, r_str, c_str = parts
                            try:
                                self._loaded_layout[name] = (int(r_str), int(c_str))
                            except ValueError:
                                print(f"[GraphsPage] Warning: Invalid position '{r_str}:{c_str}' for chart '{name}' in config.ini")
                    print(f"[GraphsPage] Loaded layout: {self._loaded_layout}") # Debug print
                else:
                    print("[GraphsPage] No saved layout found in config.ini.")
            else:
                print("[GraphsPage] config.ini not found, using default layout.")
        except configparser.Error as e:
            print(f"[GraphsPage] Error reading config.ini for layout: {e}")
        except Exception as e:
            print(f"[GraphsPage] Unexpected error loading layout: {e}")

        # Создаём графики по секции "graphs" из конфигурации (tw_config.py)
        for cfg in self.config.get("graphs", []):
            wrapper = self.create_chart(cfg)
            size = cfg.get("size", [1, 1])
            # Use loaded position if available, otherwise default from config
            chart_name = cfg.get("name")
            if chart_name in self._loaded_layout:
                pos = self._loaded_layout[chart_name]
                print(f"[GraphsPage] Using saved position {pos} for '{chart_name}'") # Debug print
            else:
                pos = cfg.get("position", [0, 0]) # Default position from config
                print(f"[GraphsPage] Using default position {pos} for '{chart_name}'") # Debug print
            self._grid_layout.addWidget(wrapper, pos[0], pos[1], size[0], size[1])

    def reset_charts(self):
            """Полностью очистить графики и вернуть их в дефолт."""
            # 1) Очистить все серии
            for cfg in self.charts.values():
                if cfg["multi_axis"]:
                    for s in cfg["series"]:
                        s.clear()
                else:
                    cfg["series"].clear()
            # 2) Сбросить индексы X
            for k in self.indexes:
                self.indexes[k] = 0
            # 3) Очистить историю авто-скейлинга
            self.data_history.clear()
            # 4) Вернуть оси в дефолтные диапазоны и перерисовать
            for name, cfg in self.charts.items():
                x_axis = cfg["x_axis"]
                y_axis = cfg["y_axis"]
                dmin, dmax = self.default_y_ranges.get(name, (0,1))
                y_axis.setRange(dmin, dmax)
                x_axis.setRange(0, 5)
                cfg["view"].update()

    def _update_system_monitor(self, psutil):
            # CPU и RAM
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            # пытаемся получить MainWindow через self.window()
            mw = self.window()
            lat_text = "UDP Latency: N/A"
            if mw and hasattr(mw, "worker"):
                last = getattr(mw.worker, "last_data_time", None)
                if last:
                    lat = time.time() - last
                    lat_text = f"UDP Latency: {lat:.2f}s"

            # обновляем метки
            self.cpu_label.setText(f"CPU: {cpu:.0f}%")
            self.ram_label.setText(f"RAM: {ram:.0f}%")
            self.lat_label.setText(lat_text)

    def create_chart(self, config):
        # Получаем заголовок из конфигурации, с поддержкой и старого, и нового формата
        title = config.get("title", config.get("name", "График"))
        
        # Диапазон Y - поддерживаем как старый формат (y_range), так и новый (y_min/y_max)
        if "y_range" in config:
            y_range = config["y_range"]
        else:
            # Используем y_min/y_max если они есть, иначе дефолтные значения
            y_min = config.get("y_min", 0)
            y_max = config.get("y_max", 100)
            y_range = (y_min, y_max)
        
        # Цвет графика
        color = config.get("color", "#4fc3f7")  # Дефолтный цвет
        
        # Тип графика
        chart_type = config.get("type", "line")  # Дефолтный тип - линейный
        
        name = config["name"]
        multi_axis = config.get("multi_axis", False)
        axis_names = config.get("axis_names", ["X", "Y", "Z"])

        # Initialize index and series
        self.indexes[name] = 0

        # Create chart and setup
        chart = QChart()
        chart.setTitle(title)
        # - Удаляем анимацию для устранения подергиваний
        # chart.setAnimationOptions(QChart.SeriesAnimations)

        # Styling
        chart.setBackgroundVisible(False)
        chart.setBackgroundVisible(True)
        chart.setBackgroundBrush(Qt.transparent)
        chart.setTitleFont(QFont("Segoe UI", 12, QFont.Bold))
        chart.legend().setVisible(multi_axis)  # Show legend only for multi-axis charts
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.legend().setFont(QFont("Segoe UI", 9))
        chart.legend().setLabelColor(QColor(COLORS["text_primary"]))

        # Axes
        ax_x = QValueAxis()
        ax_x.setLabelsVisible(True)
        ax_x.setTickCount(5)           # ➕ 5 делений по X
        ax_x.setTitleText("")              # без заголовка, но подписи видны
        ax_x.setGridLineVisible(True)
        ax_x.setMinorGridLineVisible(True)

        ax_y = QValueAxis()
        ax_y.setLabelsVisible(True)
        ax_y.setTickCount(5)           # ➕ 5 делений по Y
        ax_y.setTitleText("")              # без заголовка, но подписи видны
        ax_y.setGridLineVisible(True)
        ax_y.setMinorGridLineVisible(True)

        # Styling axes
        for axis in [ax_x, ax_y]:
            axis.setLabelsColor(QColor(COLORS["text_secondary"]))
            axis.setTitleBrush(QColor(COLORS["text_secondary"]))
            ax_x.setGridLineColor(QColor(COLORS["chart_grid"]))
            ax_x.setMinorGridLineColor(QColor(COLORS["chart_grid"]))
            ax_y.setGridLineColor(QColor(COLORS["chart_grid"]))
            ax_y.setMinorGridLineColor(QColor(COLORS["chart_grid"]))
            axis.setMinorGridLineColor(QColor("#2a2a2a"))
            axis.setTitleFont(QFont("Segoe UI", 9))
            axis.setLabelsFont(QFont("Segoe UI", 8))

        # Create series
        if multi_axis:
            # For multi-axis data (like accelerometer with x,y,z)
            colors = ["#4fc3f7", "#ff9e80", "#aed581"]  # Blue, Orange, Green for X, Y, Z
            series_list = []

            for i in range(3):
                series = QLineSeries()
                # animate line drawing
                series.setName(axis_names[i])
                pen = QPen()
                pen.setColor(QColor(colors[i]))
                pen.setWidthF(2.0)
                series.setPen(pen)
                if config.get("use_opengl", False):
                    series.setUseOpenGL(True)
                chart.addSeries(series)

                # We must create separate Y axis for each series to avoid scaling issues
                if i == 0:
                    # Use the main Y axis for the first series
                    chart.addAxis(ax_y, Qt.AlignLeft)
                    series.attachAxis(ax_y)
                else:
                    # Create additional Y axes that will share the same scale
                    extra_y = QValueAxis()
                    extra_y.setRange(y_range[0], y_range[1])
                    extra_y.setVisible(False)  # Hide additional Y axes, only use for scaling
                    chart.addAxis(extra_y, Qt.AlignLeft)
                    series.attachAxis(extra_y)

                # All series share the X axis
                if i == 0:
                    chart.addAxis(ax_x, Qt.AlignBottom)
                series.attachAxis(ax_x)

                series_list.append(series)

            # Register in charts and series dicts
            self.charts[name] = {
                "view": None,
                "chart": chart,
                "series": series_list,
                "x_axis": ax_x,
                "y_axis": ax_y,
                "multi_axis": True,
                "y_range": y_range
            }
            # Populate series mapping for updates
            for i, s in enumerate(series_list):
                key = f"{name}_{i}"
                self.series[key] = s
                self.indexes[key] = 0
        else:
            # For single value data
            series = QLineSeries()
            pen = QPen()
            pen.setColor(QColor(color))
            pen.setWidthF(2.5)
            series.setPen(pen)

            chart.addSeries(series)
            chart.addAxis(ax_x, Qt.AlignBottom)
            chart.addAxis(ax_y, Qt.AlignLeft)
            series.attachAxis(ax_x)
            series.attachAxis(ax_y)

            # Register in charts and series dicts
            self.charts[name] = {
                "view": None,
                "chart": chart,
                "series": series,
                "x_axis": ax_x,
                "y_axis": ax_y,
                "multi_axis": False,
                "y_range": y_range
            }
            # Populate series mapping for updates
            self.series[name] = series
            self.indexes[name] = 0

        # Create chart view with enhanced rendering
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        # ➕ Включаем «резиновую рамку» для зума и пан
        #chart_view.setRubberBand(QChartView.RectangleRubberBand)
        chart_view.setRenderHint(QPainter.TextAntialiasing)
        chart_view.setRenderHint(QPainter.SmoothPixmapTransform)
        chart_view.setBackgroundBrush(Qt.transparent)
        # Set a reasonable minimum size for charts
        chart_view.setMinimumSize(300, 250) 

        # wrap into card for rounded background
        wrapper = DraggableCard()
        wrapper.setObjectName("card")
        wrapper.setProperty("chart_name", name)
        wrapper.setProperty("detached", False)
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0,0,0,0)
        wrapper_layout.addWidget(chart_view)
        # + кнопка Detach (открыть новый Window-клон)
        btn_detach = QPushButton("⇱")
        btn_detach.setFixedSize(24,24)
        btn_detach.setToolTip("Open chart in separate window")
        # передаём name, чтобы найти chart_data
        btn_detach.clicked.connect(lambda _, n=config["name"]: self._open_detach(n))
        wrapper_layout.addWidget(btn_detach, alignment=Qt.AlignLeft)

        # +++ кнопка Save PNG +++
        btn = QPushButton("💾 Save PNG")
        btn.setFixedHeight(30)
        btn.setCursor(Qt.PointingHandCursor)
        wrapper_layout.addWidget(btn, alignment=Qt.AlignRight)
        btn.clicked.connect(lambda _, w=chart_view, n=name: self._save_chart_png(w, n))

        # Store the view reference
        self.charts[name]["view"]    = chart_view
        self.charts[name]["wrapper"] = wrapper

        # ➕ Запомним исходный диапазон Y сразу при создании
        self.default_y_ranges[name] = tuple(y_range)
        return wrapper

    def auto_scale_y_axis(self, name, data_values):
        """Automatically scale the Y axis based on current data values with improved logic"""
        chart_data = self.charts.get(name)
        if not chart_data:
            return

        y_axis = chart_data["y_axis"]
        # + Получаем историю значений
        history = self.data_history.setdefault(name, [])

        # + Если новых значений нет или они пустые - не меняем масштаб
        if not data_values:
            return

        # + Работаем с историей + текущими значениями для стабильного масштабирования
        all_values = history + data_values

        # + Если данных все еще мало - используем исходный диапазон
        # Всегда вычисляем мин/макс из всех собранных значений
        valid_values = []
        for v in all_values:
            if v is not None and not math.isnan(v):
                valid_values.append(v)
        if not valid_values:
            return
        current_min = min(valid_values)
        current_max = max(valid_values)

        # вычисляем середину и размах
        v_min = min(valid_values)
        v_max = max(valid_values)
        mid  = (v_min + v_max) / 2.0
        # добавляем 20% запаса, и не даём span упасть ниже 0.1
        span = max((v_max - v_min) * 1.2, 0.1)

        # + Не допускаем, чтобы мин и макс были слишком близко друг к другу
        if abs(current_max - current_min) < 0.1:
            current_min -= 0.5
            current_max += 0.5

        # + Добавляем отступ для лучшей визуализации (20%)
        padding = (current_max - current_min) * 0.2
        new_min = current_min - padding
        new_max = current_max + padding
        new_min = mid - span/2
        new_max = mid + span/2

        current_axis_min = y_axis.min()
        current_axis_max = y_axis.max()
        now = time.time()
        if new_min < current_axis_min or new_max > current_axis_max:
            # ➕ сразу расширяем до экстремума и запоминаем момент
            self.last_extreme[name] = now
            y_axis.setRange(new_min, new_max)
            if chart_data.get("multi_axis"):
                for series in chart_data["series"][1:]:
                    for axis in chart_data["chart"].axes(Qt.Vertical, series):
                        axis.setRange(new_min, new_max)
            return

        # ➕ плавное сжатие диапазона
        # + Плавное изменение масштаба вместо резкого
        current_axis_min = y_axis.min()
        current_axis_max = y_axis.max()

        smooth_factor = 0.2  # Коэффициент сглаживания…
        final_min = current_axis_min + (new_min - current_axis_min) * smooth_factor
        final_max = current_axis_max + (new_max - current_axis_max) * smooth_factor
        # + Меняем масштаб только если разница существенная
        threshold = (current_axis_max - current_axis_min) * 0.1  # 10% порог изменения
        if (abs(final_min - current_axis_min) > threshold or
            abs(final_max - current_axis_max) > threshold):
            y_axis.setRange(final_min, final_max)

            # + Также обновляем дополнительные оси в мульти-графиках
            if chart_data.get("multi_axis"):
                chart = chart_data["chart"]
                for i, series in enumerate(chart_data["series"]):
                    if i > 0:  # Пропускаем первую серию, т.к. она использует основную ось
                        axes = chart.axes(Qt.Vertical, series)
                        if axes:
                            for axis in axes:
                                axis.setRange(final_min, final_max)

    def _toggle_detach(self, wrapper):
        """Toggle detach/attach of chart-card, hide/show the original Detach button,
        and ensure cross-close also re-attaches."""
        grid    = self._grid_layout
        content = grid.parentWidget() if grid else None

        # ATTACH back if already detached
        if wrapper in self._detached_windows:
            win = self._detached_windows.pop(wrapper)
            # close the detached window
            win.close()
            # return card to saved grid position
            r, c = self._orig_pos.pop(wrapper)
            wrapper.setParent(content)
            grid.addWidget(wrapper, r, c)
            # reset flags
            wrapper.setProperty("detached", False)
            wrapper.setProperty("detached_win", None)
            # show the original Detach ("⇱") button
            for btn in wrapper.findChildren(QPushButton):
                if btn.toolTip() == "Open chart in separate window":
                    btn.show()
            return

        # DETACH: remove from grid and open in its own window
        idx = grid.indexOf(wrapper)
        if idx < 0:
            print("[GraphsPage] detach: wrapper not in grid")
            return
        r, c, rs, cs = grid.getItemPosition(idx)
        self._orig_pos[wrapper] = (r, c)
        grid.removeWidget(wrapper)

        # create the new window
        win = QMainWindow()
        win.setWindowTitle(f"Chart: {wrapper.property('chart_name')}")
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0,0,0,0)

        # move the wrapper into the window
        wrapper.setParent(container)
        lay.addWidget(wrapper)

        # add a reattach button inside the window
        btn_reattach = QPushButton("−")
        btn_reattach.setFixedSize(24,24)
        btn_reattach.setToolTip("Reattach chart")
        btn_reattach.clicked.connect(lambda _, w=wrapper: self._toggle_detach(w))
        lay.addWidget(btn_reattach, alignment=Qt.AlignLeft)

        win.setCentralWidget(container)

        # override closeEvent so cross-click also reattaches
        def close_and_reattach(event):
            # call toggle to reattach
            self._toggle_detach(wrapper)
            # accept the close
            event.accept()
        win.closeEvent = close_and_reattach

        win.show()

        # hide the original Detach button in the embedded wrapper
        for btn in wrapper.findChildren(QPushButton):
            if btn.toolTip() == "Open chart in separate window":
                btn.hide()

        # mark as detached
        wrapper.setProperty("detached", True)
        wrapper.setProperty("detached_win", win)
        self._detached_windows[wrapper] = win

    def _open_detach(self, name: str):
            """Найти wrapper по name и вызвать toggle."""
            # ищем wrapper во всех карточках
            for info in self.charts.values():
                # мы сохранили view, его parent() — wrapper
                wrapper = info["view"].parent()
                if wrapper.property("chart_name") == name:
                    # вызываем общий toggle
                    self._toggle_detach(wrapper)
                    return
            print(f"[GraphsPage] Warning: no chart wrapper found for '{name}'")

    @Slot(object, str)
    def _save_chart_png(self, chart_view, name: str):
        # parent для диалога — окно, в котором сейчас chart_view
        parent_win = chart_view.window() or self
        path, _ = QFileDialog.getSaveFileName(
            parent_win,
            f"Save chart «{name}» as PNG",
            f"{name}.png",
            "PNG Files (*.png)"
        )
        if not path:
            return
        # снимем «скрин» и сбросим события, чтобы UI не завис
        pix = chart_view.grab()
        QApplication.processEvents()
        if not pix.save(path, "PNG"):
            print(f"[GraphsPage] Failed to save PNG to {path}")

    def save_layout(self):
        """Save current grid positions into config.ini as name:row:col,..."""
        import configparser
        # получаем layout, в котором лежат карточки
        layout = self._grid_layout

        pairs = []
        # для каждого элемента layout
        for idx in range(layout.count()):
            item = layout.itemAt(idx)
            w = item.widget()
            if not w: continue
            name = w.property("chart_name")
            # узнаём где он
            r, c, rs, cs = layout.getItemPosition(idx)
            pairs.append(f"{name}:{r}:{c}")

        cfg = configparser.ConfigParser()
        cfg.read("config.ini")
        if "Layout" not in cfg:
            cfg["Layout"] = {}
        cfg["Layout"]["chart_positions"] = ",".join(pairs)
        with open("config.ini", "w") as f:
            cfg.write(f)

    @Slot(dict)
    def update_charts(self, data):

        # Update each configured chart
        for graph_config in self.config.get("graphs", []):
            name = graph_config.get("name")
            chart_data = self.charts.get(name)
            if not chart_data:
                continue

            chart_view = chart_data["view"]
            # Disable updates temporarily to prevent flicker
            try:
                chart_view.setUpdatesEnabled(False)
            except RuntimeError:
                pass # View might be closed

            max_points = self.data_points.get(name, 200)
            x_axis = chart_data["x_axis"]
            current_count = 0

            # --- Multi-axis charts (use 'sources' key) --- 
            if chart_data.get("multi_axis", False) and "sources" in graph_config:
                values = []
                # Extract each value from the sources list
                for raw_src in graph_config["sources"]:
                    val = None
                    if '[' in raw_src and ']' in raw_src:
                        base, idx_str = raw_src.split('[')
                        idx = int(idx_str.rstrip(']'))
                        arr = data.get(base)
                        if isinstance(arr, (list, tuple)) and len(arr) > idx:
                            val = arr[idx]
                    else:
                        val = data.get(raw_src)
                    values.append(val if val is not None else 0)
                
                # Update series and enforce window
                if len(values) == len(chart_data["series"]):
                    for i, series in enumerate(chart_data["series"]):
                        if series.count() >= max_points:
                            remove_cnt = series.count() - max_points + 1
                            series.removePoints(0, remove_cnt)
                        series.append(series.count(), values[i])
                    current_count = chart_data["series"][0].count()
                
                    # Update history and autoscale
                    hist = self.data_history.setdefault(name, [])
                    hist.extend(values)
                    max_hist = max_points * 3 * len(values)
                    if len(hist) > max_hist:
                        hist[:] = hist[-max_hist:]
                    # Autoscale based on the new values added
                    self.auto_scale_y_axis(name, values)
            
            # --- Single-value charts (use 'source' key) ---
            elif "source" in graph_config:
                val = None
                raw_src = graph_config["source"]
                # Handle indexed sources like accel[0]
                if '[' in raw_src and ']' in raw_src:
                    try: # Add try-except for safety during debug
                        base, idx_str = raw_src.split('[')
                        idx = int(idx_str.rstrip(']'))
                        arr = data.get(base)
                        if isinstance(arr, (list, tuple)) and len(arr) > idx:
                            val = arr[idx]
                        else:
                            pass # Ignore parsing errors silently for now
                    except Exception as e:
                        pass # Ignore parsing errors silently for now
                # Handle direct sources like temp_bmp
                else:
                    val = data.get(raw_src)
                
                # Append value if found
                if val is not None:
                    series = chart_data["series"]
                    if series.count() >= max_points:
                        remove_cnt = series.count() - max_points + 1
                        series.removePoints(0, remove_cnt)
                    series.append(series.count(), val)
                    current_count = series.count()

                    # Update history and autoscale
                    hist = self.data_history.setdefault(name, [])
                    hist.append(val)
                    max_hist = max_points * 3
                    if len(hist) > max_hist:
                        hist[:] = hist[-max_hist:]
                    self.auto_scale_y_axis(name, [val]) # Autoscale based on the single new value
            
            # --- Update X-axis and repaint (common for both types if data was added) ---
            if current_count > 0: # Only update axis if points were added
                x_axis.setRange(max(0, current_count - max_points), current_count + 5) # Use current_count
                # Advance index counter (useful for debugging or future features)
                self.indexes[name] = self.indexes.get(name, 0) + 1
            
            # Re-enable updates and repaint the view
            try:
                chart_view.setUpdatesEnabled(True)
            except RuntimeError:
                pass # View might be closed
            chart_view.update()

    def showEvent(self, event):
        super().showEvent(event)
        # Refresh all chart views when the page is shown
        # Use QTimer.singleShot to ensure updates happen after the event loop is processed
        def refresh_charts():
            for info in self.charts.values():
                try:
                    if info.get("view"): info["view"].update()
                except Exception as e:
                    print(f"[GraphsPage] Error refreshing chart in showEvent: {e}")
        QTimer.singleShot(0, refresh_charts)

import numpy as np
def load_mesh_obj(filename: str, max_faces: int = 1000) -> MeshData:
    """
    Загружает Wavefront OBJ файл и возвращает MeshData.
    Делает триангуляцию и динамическое упрощение до max_faces треугольников.
    """
    verts = []
    faces = []

    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('v '):
                parts = line.strip().split()[1:]
                verts.append(tuple(map(float, parts)))
            elif line.startswith('f '):
                parts = line.strip().split()[1:]
                idx = [int(p.split('/')[0]) - 1 for p in parts]
                # Триангуляция (fan)
                if len(idx) == 3:
                    faces.append(idx)
                else:
                    for i in range(1, len(idx) - 1):
                        faces.append([idx[0], idx[i], idx[i + 1]])

    # Конвертация в numpy
    vert_array = np.array(verts, dtype=np.float32)
    face_array = np.array(faces, dtype=np.int32)

    # --- Оптимизация: если граней слишком много, уменьшаем до max_faces ---
    total = face_array.shape[0]
    if total > max_faces:
        step = math.ceil(total / max_faces)
        face_array = face_array[::step]

    return MeshData(vertexes=vert_array, faces=face_array)

# === СТРАНИЦА ЛОГОВ + ЭКСПОРТ В ZIP ===
class LogPage(QWidget):
    def __init__(self):
        super().__init__()
        self.error_list: list[str] = []
        layout = QVBoxLayout(self); layout.setContentsMargins(15,15,15,15)
        self.log_entries: list[tuple[str,str]] = []  # хранить пары (raw, html)
        # --- Search filter ---
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search logs...")
        self.search_edit.textChanged.connect(self.filter_logs)
        layout.addWidget(self.search_edit)
        header = QLabel("Системный журнал")
        header.setStyleSheet(f"""
            font-size: 16pt; font-weight: bold; color: {COLORS['text_primary']}; margin-bottom:10px
        """)
        self.log_text = QTextEdit();
        self.log_text.setReadOnly(True)
        # включить контекстное меню с Copy
        self.log_text.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        self.log_text.setFont(QFont("Consolas",10))
        self.log_text.setStyleSheet(f"""
            QTextEdit {{ background: {COLORS['bg_dark']}; color: {COLORS['text_primary']};
            border-radius:6px; padding:10px; border:none }}
        """)
        buttons_layout = QHBoxLayout()
        self.clear_btn = QPushButton("Очистить лог")
        self.save_btn = QPushButton("Сохранить лог")
        self.export_btn = QPushButton("Экспорт ZIP")
        for btn in (self.clear_btn, self.save_btn, self.export_btn):
            btn.setFixedHeight(40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['bg_panel']};
                    color: {COLORS['text_primary']};
                    border-radius:8px; font-size:11pt; padding:0 20px;
                }}
                QPushButton:hover {{ background-color: {COLORS['accent_darker']}; }}
                QPushButton:pressed {{ background-color: {COLORS['accent']}; }}
            """)
        self.clear_btn.clicked.connect(self.clear_log)
        self.save_btn.clicked.connect(self.save_log)
        self.export_btn.clicked.connect(self.export_logs)
        # авто-сохранение
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self._on_auto_save)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.export_btn)
        # +++ Кнопка «Экспорт отчёта» +++
        self.report_btn = QPushButton("Экспорт отчёта")
        self.report_btn.setFixedHeight(40)
        self.report_btn.setStyleSheet(self.export_btn.styleSheet())
        self.report_btn.clicked.connect(self.export_report)
        buttons_layout.addWidget(self.report_btn)
        buttons_layout.addStretch()
        layout.addWidget(header); layout.addWidget(self.log_text); layout.addLayout(buttons_layout)
        # таймер-дебаунсер для автоскейла

    @Slot(str)
    def configure_auto_save(self, enabled: bool, interval_min: int):
        if self.auto_save_timer.isActive():
            self.auto_save_timer.stop()
        if enabled:
            self.auto_save_timer.start(interval_min * 60 * 1000)

    @Slot()
    def _on_auto_save(self):
        # пометим, что это автосохранение
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.add_log_message(f"[AUTO] Автосохранение логов: {ts}")
        self.save_log()

    @Slot(str)
    def add_log_message(self, message):
    # Определяем цвет по уровню
        level = "info"
        if message.startswith("[ERROR]"):
            level = "danger"
        elif message.startswith("[WARNING]"):
            level = "warning"
        color = {
            "info":    COLORS["text_secondary"],
            "warning": COLORS["warning"],
            "danger":  COLORS["danger"],
        }[level]
        # Формируем сырое и HTML-представление
        raw  = f"{datetime.datetime.now().strftime('%H:%M:%S')} {message}"
        html = f'<span style="color:{color};">{raw}</span>'
        # Сохраняем пару и добавляем в QTextEdit
        self.log_entries.append((raw, html))
        self.log_text.append(html)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def clear_log(self):
        self.log_text.clear()
        self.log_entries.clear()
        from PySide6.QtWidgets import QApplication
        mw = QApplication.activeWindow()
        if hasattr(mw, "notify"):
            mw.notify("Logs cleared", "info")

    def filter_logs(self, text):
        """Фильтрация по сырым строкам, вывод с сохранением цвета."""
        self.log_text.clear()
        for raw, html in self.log_entries:
            if text.lower() in raw.lower():
                self.log_text.append(html)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def save_log(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = f"log/system_log_{now}.txt"
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log_text.toPlainText())
            self.add_log_message(f"[{datetime.datetime.now()}] Лог сохранен в {path}")
            msg = f"[{datetime.datetime.now()}] Лог сохранен в {path}"
            self.add_log_message(msg)
            from PySide6.QtWidgets import QApplication
            mw = QApplication.activeWindow()
            if hasattr(mw, "notify"):
                mw.notify("Log saved", "success")
        except Exception as e:
            self.add_log_message(f"[ERROR] Не удалось сохранить лог: {e}")

    @Slot()
    def export_logs(self):
            # Запускаем фоновый поток для архивации
            self.add_log_message(f"[{datetime.datetime.now()}] Запуск экспорта ZIP...")
            if not os.path.isdir("log"):
                return
            self._export_thread = ExportLogsThread(log_dir="log")
            self._export_thread.finished.connect(self._on_export_finished)
            self._export_thread.start()

    @Slot()
    def export_report(self):
        """Экспорт всей сессии в HTML или PDF."""
        from PySide6.QtWidgets import QFileDialog
        from PySide6.QtGui import QTextDocument
        from PySide6.QtCore import QBuffer
        from PySide6.QtPrintSupport import QPrinter

        path, fmt = QFileDialog.getSaveFileName(
            self, "Export report", "", "HTML Files (*.html);;PDF Files (*.pdf)"
        )
        if not path:
            return

        # Получаем главное окно
        mw = self.window()

        # Логи и ошибки
        logs = self.log_text.toPlainText()
        errors = "\n".join(self.error_list)

        # Картинки графиков
        imgs = {}
        if hasattr(mw, "graphs"):
            for name, chart_data in mw.graphs.charts.items():
                pix = chart_data["view"].grab()
                buf = QBuffer()
                buf.open(QBuffer.ReadWrite)
                pix.save(buf, "PNG")
                b64 = buf.data().toBase64().data().decode()
                imgs[name] = b64

        # HTML
        html = "<html><head><style>"
        html += "body{background:#1a1a1a;color:#ffffff;font-family:Segoe UI;}"
        html += ".card{background:#242424;padding:10px;margin:10px;border-radius:8px;}"
        html += "h1,h2{color:" + COLORS["accent"] + ";}</style></head><body>"
        html += "<h1>Telemetry Report</h1><h2>Logs</h2><pre>{}</pre>".format(logs)
        html += "<h2>Errors</h2><pre>{}</pre><h2>Charts</h2>".format(errors)
        for name, b64 in imgs.items():
            html += f"<div class='card'><h3>{name}</h3>"
            html += f"<img src='data:image/png;base64,{b64}'/></div>"
        html += "</body></html>"

        # Сохраняем HTML или PDF
        if path.lower().endswith(".html"):
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            msg = f"HTML report saved to {path}"
        else:
            doc = QTextDocument()
            doc.setHtml(html)
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(path)
            doc.print_(printer)
            msg = f"PDF report saved to {path}"

        # Лог и уведомление (один раз)
        self.add_log_message(f"[AUTO] {msg}")
        if hasattr(mw, "notify"):
            mw.notify("Report exported", "success")

    @Slot(str, bool, str)
    def _on_export_finished(self, archive: str, success: bool, error: str):
        if success:
            self.add_log_message(f"[{datetime.datetime.now()}] Логи экспортированы в {archive}")
            from PySide6.QtWidgets import QApplication
            mw = QApplication.activeWindow()
            if hasattr(mw, "notify"):
                mw.notify("Logs ZIP exported", "success")
        else:
            self.add_log_message(f"[ERROR] Экспорт ZIP не удался: {error}")

    def get_errors(self) -> list[str]:
        """Вернуть все WARN/ERROR сообщения."""
        return self.error_list

# === СТРАНИЦА НАСТРОЕК + .ini ===
class SettingsPage(QWidget):
    settings_changed      = Signal(bool, str, int)
    simulator_changed     = Signal(bool, str)

    def __init__(self):
        super().__init__()
        self.cfg = configparser.ConfigParser()
        # Гарантированно есть секция, даже если файл пуст
        self.cfg.read_dict({"UDP": {}, "Settings": {}, "SimulationHistory": {}, "Layout": {}})
        if os.path.isfile("config.ini"):
            self.cfg.read("config.ini")

        # --- Простая фильтрация ориентации ---
        self.roll   = 0.0
        self.pitch  = 0.0
        self.alpha  = 0.98   # вес гироскопа в комплементарном фильтре

        # --- Read saved settings ---
        udp_enabled  = self.cfg.get("UDP", "enabled", fallback="False") == "True"
        host         = self.cfg.get("UDP", "host",    fallback="127.0.0.1")
        try:
            port = int(self.cfg.get("UDP", "port", fallback="5005"))
        except ValueError:
            port = 5005
        sim_enabled  = self.cfg.get("Settings", "simulation",    fallback="False") == "True"
        auto_save    = self.cfg.getboolean("Settings", "auto_save",            fallback=False)
        auto_interval= self.cfg.getint    ("Settings", "auto_save_interval",  fallback=5)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("Настройки")
        header.setStyleSheet(f"""
            font-size:18pt; font-weight:bold; color:{COLORS['text_primary']};
            margin-bottom:20px
        """)
        layout.addWidget(header)

        # --- UDP settings ---
        udp_card = QFrame()
        udp_card.setObjectName("card")
        v = QVBoxLayout(udp_card)
        lab = QLabel("<b>UDP настройки</b>")
        lab.setStyleSheet("font-size:14pt;")
        self.udp_enable = QCheckBox("Включить UDP отправку")
        self.udp_enable.setChecked(udp_enabled)
        self.udp_ip     = QLineEdit(host)
        self.udp_ip.setPlaceholderText("IP адрес")
        self.udp_port   = QLineEdit(str(port))
        self.udp_port.setPlaceholderText("Порт")
        for w in (lab, self.udp_enable, self.udp_ip, self.udp_port):
            v.addWidget(w)
        layout.addWidget(udp_card)

        # --- Simulation from file ---
        sim_card = QFrame()
        sim_card.setObjectName("card")
        v2 = QVBoxLayout(sim_card)
        lab2 = QLabel("<b>Имитация из файла</b>")
        self.sim_enable    = QCheckBox("Включить имитацию")
        self.sim_enable.setChecked(sim_enabled)
        self.sim_file_path = QLineEdit()
        self.sim_file_path.setPlaceholderText("Путь к бинарному лог-файлу")
        self.sim_file_path.setReadOnly(True)
        btn_browse = QPushButton("Выбрать файл")
        btn_browse.clicked.connect(self.browse_sim_file)
        # История последних файлов
        self.history_combo = QComboBox()
        hist = self.cfg.get("SimulationHistory", "last_files", fallback="").split(",")
        hist = [p for p in hist if p]
        self.history_combo.addItems(hist)
        self.history_combo.setToolTip("Последние 5 файлов симуляции")
        self.history_combo.currentTextChanged.connect(
            lambda path: (self.sim_file_path.setText(path),
                          self.simulator_changed.emit(True, path))
        )
        # Вставляем в layout
        v2.addWidget(QLabel("История файлов"))
        v2.addWidget(self.history_combo)
        v2.addWidget(lab2)
        v2.addWidget(self.sim_enable)
        hl = QHBoxLayout()
        hl.addWidget(self.sim_file_path)
        hl.addWidget(btn_browse)
        v2.addLayout(hl)
        layout.addWidget(sim_card)
        # Эмитим только по нажатию Save
        # Disable simulation block when UDP is on
        # Когда включаем UDP — выключаем симуляцию, и наоборот
        self.udp_enable.stateChanged.connect(lambda state: (
            # если UDP включили — убираем галочку и блокируем симуляцию
            self.sim_enable.setChecked(False) if state else None,
            self.sim_enable.setEnabled(not state),
            self.sim_file_path.setEnabled(not state),
            btn_browse.setEnabled(not state)
        ))
        self.sim_enable.stateChanged.connect(lambda state: (
            # если симуляцию включили — убираем галочку и блокируем UDP
            self.udp_enable.setChecked(False) if state else None,
            self.udp_enable.setEnabled(not state),
            self.udp_ip.setEnabled(not state),
            self.udp_port.setEnabled(not state)
        ))
        # initial enable/disable
        self.sim_enable.setEnabled(not udp_enabled)
        self.sim_file_path.setEnabled(not udp_enabled)
        btn_browse.setEnabled(not udp_enabled)

        # --- Save button ---
        self.save_btn = QPushButton("Сохранить настройки")
        self.save_btn.setFixedHeight(40)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS["bg_panel"]};
                color:{COLORS['text_primary']};
                border-radius:6px; font-size:11pt;
                padding:0 20px
            }}
            QPushButton:hover {{ background: {COLORS["accent_darker"]}; }}
            QPushButton:pressed {{ background: {COLORS["accent"]}; }}
        """)
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)
        # --- Auto-save logs every N minutes ---
        # wrap into card
        auto_card = QFrame()
        auto_card.setObjectName("card")
        v_auto = QVBoxLayout(auto_card)
        self.auto_save_chk = QCheckBox("Автосохранение логов каждые N минут")
        self.auto_save_spin = QSpinBox()
        self.auto_save_spin.setRange(1, 60)
        self.auto_save_chk.setChecked(auto_save)
        self.auto_save_spin.setValue(auto_interval)
        h = QHBoxLayout()
        h.addWidget(self.auto_save_chk)
        h.addWidget(self.auto_save_spin)
        v_auto.addLayout(h)
        layout.addWidget(auto_card)
        # --- Reset graph layout ---
        self.reset_layout_btn = QPushButton("Сбросить расположение графиков")
        self.reset_layout_btn.setObjectName("resetLayoutBtn")
        self.reset_layout_btn.setFixedHeight(30)
        self.reset_layout_btn.clicked.connect(self._reset_graph_layout)
        # wrap reset button into its own card
        reset_card = QFrame()
        reset_card.setObjectName("card")
        v_reset = QVBoxLayout(reset_card)
        v_reset.addWidget(self.reset_layout_btn, alignment=Qt.AlignCenter)
        layout.addWidget(reset_card)
        layout.addStretch()
    def save_settings(self):
        # UDP section
        self.cfg["UDP"] = {
            "enabled": str(self.udp_enable.isChecked()),
            "host":    self.udp_ip.text(),
            "port":    self.udp_port.text()
        }
        # Settings section (simulation)
        if "Settings" not in self.cfg:
            self.cfg["Settings"] = {}
        self.cfg["Settings"]["simulation"]    = str(self.sim_enable.isChecked())

        # store auto-save into cfg
        self.cfg["Settings"]["auto_save"] = str(self.auto_save_chk.isChecked())
        self.cfg["Settings"]["auto_save_interval"] = str(self.auto_save_spin.value())
        # Write to file
        with open("config.ini", "w") as f:
            self.cfg.write(f)
        # store auto-save
        self.cfg["Settings"]["auto_save"] = str(self.auto_save_chk.isChecked())
        self.cfg["Settings"]["auto_save_interval"] = str(self.auto_save_spin.value())

        # Emit signals
        self.settings_changed.emit(
            self.udp_enable.isChecked(),
            self.udp_ip.text(),
            int(self.udp_port.text() or 0)
        )
        self.simulator_changed.emit(
            self.sim_enable.isChecked(),
            self.sim_file_path.text()
        )
        # уведомляем
        from PySide6.QtWidgets import QApplication
        mw = QApplication.activeWindow()
        if hasattr(mw, "notify"):
            mw.notify("Settings saved", "success")

    from PySide6.QtWidgets import QFileDialog

    def browse_sim_file(self):
            """Открыть немодальный Qt-диалог выбора бинарного файла без сетевого зависания."""
            dlg = QFileDialog(self.window(), "Выбрать бинарный файл",
                             self.sim_file_path.text() or os.getcwd())
            dlg.setFileMode(QFileDialog.ExistingFile)
            dlg.setNameFilter("Binary files (*.bin);;All files (*)")
            dlg.setOption(QFileDialog.DontUseNativeDialog, True)  # использовать Qt-диалог
            dlg.fileSelected.connect(self._on_sim_file_chosen)
            dlg.open()

    def _on_sim_file_chosen(self, path: str):
            """Слот при выборе файла: обновляем поле, историю и запускаем симуляцию."""
            self.sim_file_path.setText(path)
            # Обновляем историю
            hist = self.cfg.get("SimulationHistory", "last_files", fallback="").split(",")
            hist = [p for p in hist if p and p != path]
            hist.insert(0, path)
            hist = hist[:5]
            self.cfg["SimulationHistory"] = {"last_files": ",".join(hist)}
            with open("config.ini", "w") as f:
                self.cfg.write(f)
            self.history_combo.clear()
            self.history_combo.addItems(hist)
            # Эмитим сигнал
            self.simulator_changed.emit(True, path)

    def _reset_graph_layout(self):
        """Сбросить сохранённый порядок графиков."""
        import configparser
        from PySide6.QtWidgets import QMessageBox

        cfg = configparser.ConfigParser()
        cfg.read("config.ini")
        if cfg.has_section("Layout") and cfg.has_option("Layout", "graph_order"):
            cfg.remove_option("Layout", "graph_order")
            with open("config.ini", "w") as f:
                cfg.write(f)
        QMessageBox.information(self, "Сброс",
                                "Порядок графиков сброшен. Перезапустите приложение.")

class ConsolePage(QWidget):
    """Простейшая консоль для команд TelemetryWorker."""
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        ConsoleHighlighter(self.output)
        self.input = QLineEdit()
        self.input.setPlaceholderText("Введите команду и Enter…")
        self.layout().addWidget(self.output)
        self.layout().addWidget(self.input)
        self.input.returnPressed.connect(self._on_enter)
        self.output.setStyleSheet("font-family: Consolas, monospace;")
        # + автодополнение команд — сначала определяем список команд
        from PySide6.QtWidgets import QCompleter
        self.cmds = [
            "pause","resume","help","version","errors","exit","quit","ping","fps","events",
            "clear logs","clear errors","export report","export logs","export zip",
            "load bin","udp enable","udp disable","sensor info","log","simulate error"
        ]
        # + затем создаём QCompleter на основе self.cmds
        self.completer = QCompleter(self.cmds, self.input)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.input.setCompleter(self.completer)
        # история команд
        import json, os
        hist_file = "console_history.json"
        if os.path.exists(hist_file):
            try:
                with open(hist_file, "r") as f:
                    self._history = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._history = []
        else:
            self._history = []
        self._hist_idx = -1
        # перехват стрелок
        self.input.installEventFilter(self)

    def eventFilter(self, obj, ev):
        from PySide6.QtCore import QEvent, Qt
        if obj is self.input and ev.type() == QEvent.KeyPress:
            key = ev.key()
            if key in (Qt.Key_Up, Qt.Key_Down):
                if not self._history:
                    return False
                # перемещаем индекс
                if key == Qt.Key_Up:
                    self._hist_idx = max(0, self._hist_idx - 1)
                else:
                    self._hist_idx = min(len(self._history)-1, self._hist_idx + 1)
                # вставляем команду
                self.input.setText(self._history[self._hist_idx])
                return True
        return super().eventFilter(obj, ev)

    def _on_enter(self):
        cmd = self.input.text().strip()
        if not cmd:
            return
        # сохранить в историю
        self._history.append(cmd)
        self._hist_idx = len(self._history)
        # сбросить файл
        import json
        with open("console_history.json", "w") as f:
            json.dump(self._history, f)
        # отобразить в консоли
        self.output.appendPlainText(f"> {cmd}")
        # послать сигнал
        self.command_entered.emit(cmd)
        self.input.clear()

    # сигнал команд
    command_entered = Signal(str)

    def write_response(self, text: str):
        self.output.appendPlainText(text)

class ConsoleHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent.document())
        self.rules = []
        def make(fmt, pattern):
            self.rules.append((QRegularExpression(pattern), fmt))

        # формат для команд
        fmt_cmd = QTextCharFormat()
        fmt_cmd.setForeground(QColor(COLORS["accent"]))
        fmt_cmd.setFontWeight(QFont.Bold)

        # все одиночные команды
        single = [
            "pause","resume","help","version","errors",
            "exit","quit","ping","fps","events"
        ]
        # команды из двух слов
        multi = [
            "clear logs","clear errors",
            "export report","export logs","export zip",
            "load bin","udp enable","udp disable",
            "sensor info","log","simulate error"
        ]
        # добавляем правило для каждого
        for kw in single:
            make(fmt_cmd, rf"\b{kw}\b")
        for cmd in multi:
            pat = r"\b" + cmd.replace(" ", r"\s+") + r"\b"
            make(fmt_cmd, pat)

        # формат для ошибок и WARN
        fmt_err = QTextCharFormat()
        fmt_err.setForeground(QColor(COLORS["danger"]))
        fmt_err.setFontWeight(QFont.Bold)
        make(fmt_err, r"\bERROR\b.*")

        fmt_warn = QTextCharFormat()
        fmt_warn.setForeground(QColor(COLORS["warning"]))
        make(fmt_warn, r"\bWARNING\b.*")

    def highlightBlock(self, text):
        for expr, fmt in self.rules:
            it = expr.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)


class Notification(QWidget):
    """Всплывающее уведомление (toast)."""
    def __init__(self, message, level="info", duration=3000, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # фон по уровню
        bg = {
            "info":    COLORS["info"],
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "danger":  COLORS["danger"]
        }.get(level, COLORS["info"])
        # фон + тень
        self.setStyleSheet(f"background-color:{bg}; border-radius:8px;")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0,4)
        shadow.setColor(QColor(0,0,0,160))
        self.setGraphicsEffect(shadow)
        lbl = QLabel(message, self)
        lbl.setStyleSheet(f"color:{COLORS['text_primary']}; padding:8px;")
        lay = QHBoxLayout(self)
        lay.addWidget(lbl)
        self.adjustSize()
        # fade in
        self.setWindowOpacity(0.0)
        anim_in = QPropertyAnimation(self, b"windowOpacity", self)
        anim_in.setDuration(300)
        anim_in.setStartValue(0.0)
        anim_in.setEndValue(1.0)
        anim_in.start()
        # fade out по таймеру, сохраняем анимацию в поле
        def start_fade_out():
            self._fade_out_anim = QPropertyAnimation(self, b"windowOpacity", self)
            self._fade_out_anim.setDuration(500)
            self._fade_out_anim.setStartValue(1.0)
            self._fade_out_anim.setEndValue(0.0)
            self._fade_out_anim.finished.connect(self.close)
            self._fade_out_anim.start()
        QTimer.singleShot(duration, start_fade_out)

class MapPage(QWidget):
    """Отдельная вкладка с картой и возможностью пан/зум."""
    def __init__(self):
        super().__init__()
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10,10,10,10)
        # QML-карта
        self.map_widget = QQuickWidget()
        self.map_widget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        qml_path = os.path.join(os.getcwd(), "MapView.qml")
        self.map_widget.setSource(QUrl.fromLocalFile(qml_path))
        # Растяжение и минимум по высоте
        self.map_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.map_widget.setMinimumHeight(400)
        layout.addWidget(self.map_widget)
        # Root-объект QML для управления из Python
        self.map_root = self.map_widget.rootObject()

    def set_worker(self, worker):
        """Подписываем GPS-данные на обновление карты."""
        self.worker = worker
        worker.data_ready.connect(self.on_map_data)

    @Slot(dict)
    def on_map_data(self, data):
        """Обновляем центр карты при приходе новых координат."""
        print(f"[DBG MapPage] on_map_data received: {data}") # DEBUG 1
        lat, lon, _ = data.get("gps", (0,0,0))
        gps_fix = data.get("gps_fix", 0)
        print(f"[DBG MapPage] Extracted lat={lat}, lon={lon}, fix={gps_fix}") # DEBUG 2
        # Check if fix is valid (>0) and coordinates are non-zero (or at least one is non-zero)
        # if data.get("gps_fix", 0) > 0 and (lat or lon): # Old line
        if gps_fix > 0 and (lat != 0.0 or lon != 0.0): # More explicit check for non-zero coords
            print(f"[DBG MapPage] Condition met (fix > 0 and lat/lon != 0). Setting properties...") # DEBUG 3
            # Здесь предполагается, что в QML у Map есть свойства 'latitude'/'longitude'
            try:
                # Check return value of setProperty
                ret_lat = self.map_root.setProperty("latitude", lat)
                ret_lon = self.map_root.setProperty("longitude", lon)
                print(f"[DBG MapPage] setProperty results: lat_ok={ret_lat}, lon_ok={ret_lon}") # DEBUG 4
                if not ret_lat or not ret_lon:
                     print("[DBG MapPage] WARNING: setProperty failed! Check QML component properties.")
            except Exception as e:
                print(f"[DBG MapPage] Error calling setProperty: {e}") # DEBUG 5
        else:
             print(f"[DBG MapPage] Condition NOT met (fix={gps_fix}, lat={lat}, lon={lon})") # DEBUG 6

# === ГЛАВНОЕ ОКНО ===
class MainWindow(QMainWindow):
    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        
        # Буфер пакетов
        self.buffered_packets = []
        self.last_data = None
        
        self.setWindowTitle("Telemetry Dashboard")
        
        # ➕ Статус-бар и прогресс-бар симуляции
        self.setStatusBar(QStatusBar(self))
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False) # Hide percentage text
        self.progress_bar.setFixedHeight(8) # Make it slim
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['bg_panel']};
                border-radius: 4px;
                border: 1px solid {COLORS['chart_grid']};
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['accent']};
                border-radius: 3px;
            }}
        """)
        self.progress_bar.hide() # Initially hidden
        
        # Optionally remove status bar if nothing else uses it
        # self.setStatusBar(None) 
        
        self.resize(1200, 800)
        # self.showMaximized() # Alternative: start maximized
        self.setWindowTitle("Главное окно")
        # Remove placeholder label if it exists from previous versions
        # label = QLabel("Главное окно приложения", self)
        # label.setAlignment(Qt.AlignCenter)
        # self.setCentralWidget(label)
        label = QLabel("Главное окно приложения", self)
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)
        apply_dark_theme(QApplication.instance())

        # Pages
        self.tel     = TelemetryPage(self.config)
        self.graphs   = GraphsPage(self.config)  # Передаем конфигурацию в GraphsPage
        self.log_page = LogPage()
        self.settings = SettingsPage()
        self.console  = ConsolePage()
        self.map_page = MapPage()

        # Layout: sidebar + content
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(f"background-color: {COLORS['bg_main']};")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 30, 15, 20)
        sidebar_layout.setSpacing(10)

        menu_items = [
            {"name": "Telemetry", "icon": "📊", "index": 0},
            {"name": "Graphs",    "icon": "📈", "index": 1},
            {"name": "Logs",      "icon": "📝", "index": 2},
            {"name": "Settings",  "icon": "⚙️", "index": 3},
            {"name": "Console",   "icon": "💻", "index": 4},
            {"name": "Map",       "icon": "🗺️", "index": 5}
        ]
        self.nav_buttons = []
        for item in menu_items:
            btn = QPushButton(f" {item['icon']} {item['name']}")
            btn.setProperty("index", item["index"])
            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 12px 15px;
                    border-radius: 8px;
                    color: {COLORS['text_primary']};
                    background: transparent;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background: {COLORS['accent_darker']};
                    color: {COLORS['text_primary']};
                }}
                QPushButton:checked {{
                    background: {COLORS['accent']};
                    color: white;
                    font-weight: bold;
                }}
            """)
            btn.clicked.connect(lambda _, idx=item["index"], b=btn: self.on_nav_click(idx, b))
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch(1) # Add stretch before version/progress
        # ➕ версия приложения внизу боковой панели
        ver_lbl = QLabel(f"Version {APP_VERSION} Beta")
        ver_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 8pt;")
        ver_lbl.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(ver_lbl)
        # Add progress bar below version
        sidebar_layout.addWidget(self.progress_bar)

        self.nav_buttons[0].setChecked(True) # Check first item after adding all widgets
        main_layout.addWidget(sidebar)

        # заставляем сначала занять весь доступный space, потом QStackedWidget
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")


        # Content: помещаем фон и стек в одну ячейку grid, чтобы наложить их друг на друга
        content_area = QWidget()
        grid = QGridLayout(content_area)
        grid.setContentsMargins(20, 20, 20, 20)
        grid.setSpacing(0)

        # 1) фон
        self.bg_anim = QQuickWidget(content_area)
        self.bg_anim.setClearColor(Qt.transparent)
        self.bg_anim.setAttribute(Qt.WA_TranslucentBackground)
        self.bg_anim.setStyleSheet("background: transparent;")
        self.bg_anim.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.bg_anim.setSource(QUrl.fromLocalFile(os.path.join(os.getcwd(), "gradient.qml")))
        grid.addWidget(self.bg_anim, 0, 0)

        # 2) основной стек страниц — поверх фона
        # делаем стек и страницы прозрачными, чтобы QQuickWidget-градиент был за ними
        self.stack = QStackedWidget(content_area)
        self.stack.setAttribute(Qt.WA_TranslucentBackground)
        for page in (self.tel, self.graphs, self.log_page, self.settings, self.console, self.map_page):
            page.setAttribute(Qt.WA_TranslucentBackground)
            self.stack.addWidget(page)
        grid.addWidget(self.stack, 0, 0)

        # растянуть оба на весь доступный space
        grid.setRowStretch(0, 1)
        grid.setColumnStretch(0, 1)
        main_layout.addWidget(content_area)

        self.setCentralWidget(main_widget)

        # Telemetry worker — передаём сначала config, потом порт и baudrate
        self.worker = TelemetryWorker(self.config, "COM3", 9600)

        # Буфер пакетов и таймер для отложенного UI-обновления
        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.flush_buffered_packets)
        self.ui_timer.start(50)  # обновлять UI не чаще чем раз в 50 ms

        # ➕ При окончании симуляции — чекаем графики и буфер
        self.worker.sim_ended.connect(self.graphs.reset_charts)
        self.worker.sim_ended.connect(lambda: (
            self.tel.pause_btn.setText("⏸ Пауза"),
            self.tel.pause_btn.setEnabled(False)
        ))
        self.worker.sim_ended.connect(lambda: self.buffered_packets.clear())
        self.worker.sim_ended.connect(self._on_simulation_ended) # Connect sim end to hide progress

        self.tel.set_worker(self.worker)
        self.worker.data_ready.connect(self._on_data_ready)  # Используем _on_data_ready вместо прямого append
        self.worker.log_ready.connect(self.log_page.add_log_message)
        self.map_page.set_worker(self.worker)
        self.worker.error_crc.connect(QApplication.beep)
        # Connect progress signal
        self.worker.simulation_progress.connect(self._on_simulation_progress)

        # Сначала сохраняем настройки, без подключённых слотов — чтобы не было всплывашек на старте
        self.settings.save_settings()
        # Теперь подключаем обработчики сигналов
        self.settings.settings_changed.connect(self.worker.update_udp)
        self.settings.settings_changed.connect(lambda *_: (
            self.tel.pause_btn.setText("⏸ Пауза"),
            self.tel.pause_btn.setEnabled(False)
        ))
        self.settings.simulator_changed.connect(self.on_simulator_changed)
        # автосохранение логов
        self.settings.save_settings()  # чтобы cfg обновился
        self.log_page.configure_auto_save(
            self.settings.auto_save_chk.isChecked(),
            self.settings.auto_save_spin.value()
        )
        self.settings.auto_save_chk.stateChanged.connect(
            lambda s: self.log_page.configure_auto_save(
                bool(s), self.settings.auto_save_spin.value()
            )
        )
        self.settings.auto_save_spin.valueChanged.connect(
            lambda v: self.log_page.configure_auto_save(
                self.settings.auto_save_chk.isChecked(), v
            )
        )

        # Start
        print("[UI] MainWindow: about to start TelemetryWorker")
        self.worker.start()
        print("[UI] MainWindow: TelemetryWorker.start() called")
        # Подписываемся на прогресс симуляции
        self.worker.simulation_progress.connect(self._on_simulation_progress)
        self.worker.sim_ended.connect(lambda: self.progress_bar.reset())
        # Сразу скрываем прогресс-бар (будет виден только на вкладке Телеметрия)
        self.progress_bar.setVisible(self.stack.currentIndex() == 0)

        # — Горячие клавиши —
        # Ctrl+P — пауза/возобновление
        sc_pause = QShortcut(QKeySequence("Ctrl+P"), self)
        sc_pause.activated.connect(lambda: self.tel.pause_btn.click())
        # Ctrl+S — экспорт логов
        sc_export = QShortcut(QKeySequence("Ctrl+S"), self)
        sc_export.activated.connect(self.log_page.export_logs)
        # Ctrl+R — сброс расположения графиков (reset layout)
        sc_reset = QShortcut(QKeySequence("Ctrl+R"), self)
        sc_reset.activated.connect(self.settings._reset_graph_layout)
        # Чтобы на старте и при сохранении настроек не вылезали уведомления:
        self.settings.save_settings()
        self.console.command_entered.connect(self._handle_console_command)
        sc_profile = QShortcut(QKeySequence("Ctrl+I"), self)
        sc_profile.activated.connect(self.print_profile)

        # теперь действительно обновляем маленькие графики в TelemetryPage
        self.worker.data_ready.connect(self.tel.update_values)

    def print_profile(self):
        import tracemalloc
        tracemalloc.start()
        # flush once
        self.flush_buffered_packets()
        print(tracemalloc.get_traced_memory())
        tracemalloc.stop()

    def show(self):
        super().show()
        self.center()
    def center(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        geom   = self.frameGeometry()
        geom.moveCenter(screen.center())
        self.move(geom.topLeft())

    def notify(self, message: str, level: str="info"):
        n = Notification(message, level, parent=self)
        # позиция: правый нижний угол с отступом
        x = self.geometry().right() - n.width() - 20
        y = self.geometry().bottom() - n.height() - 20
        n.move(x, y)
        n.show()

    def on_nav_click(self, idx, btn):
        for b in self.nav_buttons:
            b.setChecked(False)
        btn.setChecked(True)
        self.stack.setCurrentIndex(idx)
        # Show progress bar only when Telemetry tab (index 0) is active
        is_telemetry_tab = (idx == 0)
        is_sim_running = self.worker.sim_enabled and self.progress_bar.value() < self.progress_bar.maximum()
        self.progress_bar.setVisible(is_telemetry_tab and is_sim_running)

        # все тяжёлые вещи — через QTimer.singleShot(0,…)
        QTimer.singleShot(0, self._start_simulation)

    def _start_simulation(self):
        # 1) снимем паузу
        self.worker.resume()
        # 2) сбросим UI-буфер
        self.buffered_packets.clear()
        # 3) очистим графики
        #self.graphs.reset_charts()
        # 4) деактивируем кнопку Pause до начала прихода данных
        self.tel.pause_btn.setEnabled(False)
        # Reset progress bar, but don't show it yet.
        # It will become visible in _on_simulation_progress when data arrives.
        if self.worker.sim_enabled: # Reset only if sim mode is on
            self.progress_bar.reset() # Reset progress on start

    def closeEvent(self, event):
        # save graph layout
        try:
            self.graphs.save_layout()
        except Exception:
            pass
        self.worker.stop()
        self.worker.wait(1000)
        super().closeEvent(event)

    def flush_buffered_packets(self):
        # Создадим локальную копию буфера и очистим оригинал,
        # чтобы избежать повторной обработки одних и тех же данных
        packets = list(self.buffered_packets)
        self.buffered_packets.clear()
        
        # Если страница графиков активна - обновим графики
        if hasattr(self, 'graphs') and self.graphs is not None:
            for p in packets:
                try:
                    self.graphs.update_charts(p)
                except Exception as e:
                    print(f"[UI] flush_buffered_packets error: {e}")
        
        # Если страница телеметрии активна - обновим её ТОЛЬКО последним пакетом
        if packets and hasattr(self, 'tel') and self.tel is not None:
            try:
                self.tel.update_values(packets[-1]) # Use only the last packet
            except Exception as e:
                print(f"[UI] flush_buffered_packets error (telemetry): {e}")
        
        # Также обновляем последние данные
        if packets:
            self.last_data = packets[-1]

    @Slot(bool, str)
    def on_simulator_changed(self, enabled: bool, filepath: str):
        """Обработка смены файла симуляции."""
        print(f"[UI] MainWindow.on_simulator_changed(enabled={enabled}, path={filepath})")
        # 1) Передаём новые параметры воркеру
        self.worker.update_simulation(enabled, filepath)
        # 🔧 DEBUG: подтверждение вызова слота MainWindow.on_simulator_changed
        print(f"[UI] on_simulator_changed(enabled={enabled}, path='{filepath}')")
        # 1) Передаём новые параметры воркеру через прямое присваивание и слот
        self.worker.sim_enabled = enabled
        self.worker.sim_file_path = filepath
        # также вызываем слот для логирования
        self.worker.update_simulation(enabled, filepath)
        if not enabled:
            return
        # 3) Подготавливаем UI и запускаем симуляцию
        QTimer.singleShot(0, self._start_simulation)
        # Visibility is now handled by on_nav_click and _on_simulation_progress
        # Hide immediately if simulation is turned OFF
        if not enabled:
            self.progress_bar.hide()
            self.progress_bar.reset()

    @Slot(int, int)
    def _on_simulation_progress(self, pos: int, total: int):
        """Обновляем прогресс-бар в процентах."""
        pct = int(pos * 100 / total) if total else 0
        self.progress_bar.setValue(pct)
        # Show the progress bar ONLY if the telemetry tab is active
        if self.stack.currentIndex() == 0:
            self.progress_bar.show()

    # Add a new slot to handle simulation end signal
    @Slot()
    def _on_simulation_ended(self):
        """Слот, вызываемый при завершении имитации."""
        print("[UI] Simulation ended signal received.")
        self.progress_bar.hide()
        self.progress_bar.reset()
        # Optionally notify user
        # self.notify("Имитация завершена", "info")

    @Slot()
    def toggle_pause_shortcut(self):
        # переключаем паузу так же, как кнопка
        if self.worker.is_paused():
            self.worker.resume()
            self.log_page.add_log_message("[INFO] Resumed via Ctrl+P")
        else:
            self.worker.pause()
            self.log_page.add_log_message("[INFO] Paused via Ctrl+P")
    @Slot(str)
    def _handle_console_command(self, cmd: str):
        cmd = cmd.lower()
        # help
        if cmd in ("help", "?"):
            cmds = {
                "pause":          "приостановить прием данных",
                "resume":         "продолжить прием",
                "version":        "версия программы",
                "errors":         "показать WARN/ERROR",
                "help":           "список команд",
                "clear logs":     "очистить лог",
                "clear errors":   "очистить список ошибок",
                "exit / quit":    "выйти из приложения",
                "export report":  "экспорт отчёта HTML/PDF",
                "export logs":    "сохранить лог в файл",
                "export zip":     "экспорт логов в ZIP",
                "load bin <файл>":"загрузить бинарник для симуляции",
                "udp enable":     "включить UDP режим",
                "udp disable":    "выключить UDP режим",
                "ping":           "показать задержку UDP",
                "sensor info":    "показать последние значения всех датчиков",
                "log <текст>":    "добавить в лог сообщение",
                "simulate error": "сгенерировать CRC-ошибку",
                "fps":            "показать текущий FPS",
                "events":         "вывести список событий миссии",
            }
            hotkeys = {
                "Ctrl+P": "Pause/Resume",
                "Ctrl+S": "Export logs ZIP",
                "Ctrl+R": "Reset graph layout"
            }
            self.console.write_response("Commands:")
            for k,v in cmds.items():
                self.console.write_response(f"  {k:<7} — {v}")
            self.console.write_response("Hotkeys:")
            for k,v in hotkeys.items():
                self.console.write_response(f"  {k:<7} — {v}")
            return

        # ---------------- new commands ----------------
        if cmd == "clear logs":
            self.log_page.clear_log()
            self.console.write_response("Logs cleared")
            return
        if cmd == "clear errors":
            self.log_page.error_list.clear()
            self.console.write_response("Errors cleared")
            return
        if cmd in ("exit", "quit"):
            self.console.write_response("Exiting…")
            QTimer.singleShot(100, QApplication.instance().quit)
            return
        if cmd == "export report":
            self.log_page.export_report()
            self.console.write_response("Report export triggered")
            return
        if cmd == "export logs":
            self.log_page.save_log()
            self.console.write_response("Logs save triggered")
            return
        if cmd == "export zip":
            self.log_page.export_logs()
            self.console.write_response("ZIP export triggered")
            return
        if cmd.startswith("load bin "):
            path = cmd[len("load bin "):].strip()
            self.on_simulator_changed(True, path)
            self.console.write_response(f"Simulation file set to {path}")
            return
        if cmd == "udp enable":
            self.settings.udp_enable.setChecked(True)
            # Отключаем симуляцию
            self.worker.update_simulation(False, self.worker.sim_file_path)
            self.console.write_response("UDP enabled, simulation disabled")
            return
            return
        if cmd == "udp disable":
            self.settings.udp_enable.setChecked(False)
            self.console.write_response("UDP disabled")
            return
        if cmd == "ping":
            # Выводим время последних полученных данных если доступно
            if hasattr(self, 'worker') and hasattr(self.worker, 'last_data_time'):
                last = self.worker.last_data_time
                if last:
                    lat = time.time() - last
                    self.console.write_response(f"UDP Latency: {lat:.2f}s")
                else:
                    self.console.write_response("UDP Latency: N/A")
            else:
                self.console.write_response("UDP Latency: N/A")
            return
        if cmd == "sensor info":
            if self.last_data:
                for k,v in self.last_data.items():
                    self.console.write_response(f"{k}: {v}")
            else:
                self.console.write_response("No sensor data yet")
            return
        if cmd.startswith("log "):
            text = cmd[len("log "):]
            self.log_page.add_log_message(f"[USER] {text}")
            self.console.write_response("Logged message")
            return
        if cmd == "simulate error":
            self.worker.error_crc.emit()
            self.console.write_response("Simulated CRC error")
            return
        if cmd == "events":
            notes = getattr(self.log_page, "mission_notes", [])
            if notes:
                for n in notes:
                    self.console.write_response(n)
            else:
                self.console.write_response("No mission events")
            return

        # version
        if cmd == "version":
            self.console.write_response(f"Grib Telemetry Dashboard v{APP_VERSION} — program 'Norfa'")
            return
        # pause/resume without data-check
        if cmd in ("pause", "resume"):
            if cmd == "pause":
                self.tel.pause_btn.click()
                self.log_page.add_log_message("[INFO] Telemetry paused via console")
                self.console.write_response("OK: paused (button clicked)")
            else:
                self.tel.pause_btn.click()
                self.console.write_response("OK: resumed (button clicked)")
            return

        # show errors/warnings from log
        if cmd in ("errors", "show errors", "warnings"):
            errs = self.log_page.get_errors()
            if not errs:
                self.console.write_response("No warnings or errors.")
            for e in errs:
                self.console.write_response(e)
            return

        self.console.write_response(f"Unknown command: {cmd}")

    def _on_data_ready(self, data):
        """Обработка получения данных из TelemetryWorker."""
        # Добавляем в буфер
        self.buffered_packets.append(data)
        
        # Активируем кнопку паузы в телеметрии, если она есть и не активна
        if hasattr(self, 'tel') and hasattr(self.tel, 'pause_btn') and not self.tel.pause_btn.isEnabled():
            self.tel.pause_btn.setEnabled(True)

if __name__ == "__main__":
    # Force software OpenGL to avoid GPU "device removed" errors
    QGuiApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)
    
    # Загрузка конфигурации
    try:
        from tw_config import load_config
        config = load_config()
    except Exception as e:
        print(f"Ошибка загрузки конфигурации: {e}")
        config = {}  # Пустой конфиг на случай ошибки
    
    app = QApplication(sys.argv)
    splash = SplashScreen(config)
    splash.show()
    sys.exit(app.exec())
