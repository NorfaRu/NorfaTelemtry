# 📦 Стандартные библиотеки Python
import os
import sys
import math
import time
import socket
import struct
import zipfile
import datetime
import configparser
import tempfile
import subprocess
from subprocess import CREATE_NEW_CONSOLE
import requests

# 🌐 Настройка Qt API
os.environ['QT_API'] = 'pyside6'

APP_VERSION = "2.2.0"
GITHUB_REPO   = "NorfaRu/NorfaTelemtry"

from PySide6.QtCharts import QSplineSeries

from collections import deque

from PySide6.QtCore import QEvent, QPropertyAnimation, QObject, QMetaObject
from PySide6.QtGui  import QCursor, QGuiApplication
from PySide6.QtWidgets import QToolTip, QMessageBox
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
    Qt, QThread, Signal, Slot, QPointF, QTimer, QRect
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
        r = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest", timeout=3)
        r.raise_for_status()
        data = r.json()
        latest = data.get("tag_name", "")
        if latest and version_tuple(latest) > version_tuple(APP_VERSION):
            for asset in data.get("assets", []):
                if asset.get("name", "").lower().endswith(".exe"):
                    return True, asset["browser_download_url"], latest
    except Exception:
        pass
    return False, "", ""

class UpdateThread(QThread):
    # Добавляем сигнал для промежуточных шагов
    # Сигнал для текстовых шагов
    step     = Signal(str)
    # Сигнал для прогресса: (загружено байт, всего байт)
    progress = Signal(int, int)
    finished = Signal(bool, str)  # (success, msg)

    def __init__(self, download_url, parent=None):
        super().__init__(parent)
        self.download_url = download_url

    def run(self):
        try:
            # 1) Запрашиваем файл
            print("[Updater] Запуск загрузки…")
            self.step.emit("Начинаем загрузку обновления…")
            r = requests.get(self.download_url, stream=True, timeout=15)
            r.raise_for_status()

            # 2) Записываем с отчётом по чанкам
            temp_dir = tempfile.gettempdir()
            exe_path = os.path.join(temp_dir, "update.exe")
            tmp_exe = open(exe_path, "wb")
            print(f"[Updater] Сохраняю в {tmp_exe.name}")
            # Скачиваем и сразу пишем в update.exe
            for chunk in r.iter_content(8192):
                if not chunk:
                    continue
                tmp_exe.write(chunk)
            tmp_exe.close()
            self.step.emit("Загрузка завершена")
            print(f"[Updater] Итоговый размер: {os.path.getsize(exe_path)} байт")

            # 3) Готовим батник для безопасной замены
            self.step.emit("Подготавливаем установщик…")
            current = sys.executable
            # Тот же трюк для батника — читаем путь
            bat_path = os.path.join(temp_dir, "update.bat")
            bat = open(bat_path, "w", encoding="utf-8")
            print(f"[Updater] Создаю батник {bat_path}")
            bat_path = bat.name
            print(f"[Updater] Создаю батник {bat_path}")
            bat.write(f"""@echo off
            :wait
            tasklist /FI "IMAGENAME eq {os.path.basename(current)}" | findstr /I "{os.path.basename(current)}" >nul
            if %ERRORLEVEL%==0 (
                timeout /t 1 /nobreak >nul
                goto wait
            )
            move /Y "{tmp_exe.name}" "{current}" >nul 2>&1
            if exist "{current}" (
                start "" "{current}"
            ) else (
                echo ERROR replacing file > "%~dp0update_error.log"
            )
            pause
            exit
            """)
            bat.close()
            print(f"[Updater] Батник записан. Содержимое:\n{open(bat_path, 'r', encoding='utf-8').read()}")

            self.step.emit("Запускаем установщик…")
            # 3) Запускаем батник в новом консольном окне
            print(f"[Updater] Запускаю батник {bat_path}")
            # запускаем .bat с правами администратора
            import ctypes
            # ShellExecuteW возвращает >32 при успешном запуске
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",                # verb: run as administrator
                "cmd.exe",              # executable
                f'/k "{bat_path}"',     # аргументы (/k — оставить окно)
                None,
                1                       # SW_SHOWNORMAL
            )
            self.step.emit("Установщик запущен")
            self.finished.emit(True, "")
            # всё успешно — приложение закроется и .bat подменит exe
            self.step.emit("Обновление запущено, приложение перезапустится")
            self.finished.emit(True, "")
        except Exception as e:
            print(f"[Updater] Ошибка: {e}")
            self.step.emit(f"Ошибка при обновлении: {e}")
            self.finished.emit(False, str(e))

    @Slot(str, str)
    def _prompt_update(self, latest, url):
        print(f"[Splash] Запрашиваем у пользователя обновиться до {latest}…")

        mb = QMessageBox(self)
        mb.setWindowTitle("Доступно обновление")
        mb.setText(f"Найдена версия {latest} (у вас {APP_VERSION}). Обновиться?")
        mb.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        reply = mb.exec()

        if reply == QMessageBox.Yes:
            print("[Splash] Пользователь согласился.")
            self.update_pb.setValue(0)
            self.update_pb.show()

            self.upd_thread = UpdateThread(url)
            self.upd_thread.step.connect(lambda txt: print(f"[Updater] {txt}") or self.loading_step.emit(txt))
            self.upd_thread.progress.connect(
                lambda d, t: ( print(f"[Updater] Прогресс {d}/{t}"),
                              self.update_pb.setValue(int(d*100/t) if t else 0) )[1]
            )
            self.upd_thread.finished.connect(lambda *_: self.update_pb.hide())
            self.upd_thread.finished.connect(self._on_update_finished)
            print("[Splash] Запускаем UpdateThread…")
            self.upd_thread.start()
        else:
            print("[Splash] Пользователь отказался.")
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

    def __init__(self):
        super().__init__()
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
        self.main = MainWindow()
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
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtGui     import QDesktopServices
        from PySide6.QtCore    import QUrl
        mb = QMessageBox(self)
        mb.setWindowTitle("Доступно обновление")
        mb.setText(f"Найдена версия {latest} (у вас {APP_VERSION}). Обновиться?")
        mb.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        reply = mb.exec()
        if reply == QMessageBox.Yes:
            # Сбросить прогресс и показать бар
            self.update_pb.setValue(0)
            self.update_pb.show()

            self.upd_thread = UpdateThread(url)
            # текстовые шаги на статус-лейбл
            self.upd_thread.step.connect(self.loading_step)
            # обновление прогресса
            self.upd_thread.progress.connect(
                lambda done, total: self.update_pb.setValue(int(done * 100 / total) if total else 0)
            )
            # по завершении — скрыть прогресс-бар
            self.upd_thread.finished.connect(lambda *_: self.update_pb.hide())
            self.upd_thread.finished.connect(self._on_update_finished)
            self.upd_thread.start()
            return
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
        print(f"[Splash] UpdateThread завершился: success={success}, msg={msg}")
        if not success:
            QMessageBox.critical(self, "Ошибка обновления", msg)
        QApplication.quit()

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
    def __init__(self, port_name="COM3", baud=9600, parent=None):
        super().__init__(parent)
        import math, time
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
        self.log_ready.emit("Telemetry thread started. Version 2.1 (Fix Update)")
        self.log_ready.emit("Надёжная версия: 1.9")

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
                        pkt = struct.unpack(STRUCT_FMT, chunk)
                    except struct.error:
                        buf = buf[1:]
                        continue
                    if self.xor_block(chunk[:-1]) == pkt[-1]:
                        try:
                            data = {
                                "packet_num": pkt[12],
                                "timestamp": pkt[2],
                                "temp_bmp": pkt[3]/100,
                                "press_bmp": pkt[4],
                                "accel": [v*488/1000/1000 for v in pkt[5:8]],
                                "gyro": [v*70/1000 for v in pkt[8:11]],
                                "state": pkt[13] & 0x07,
                                "photo": pkt[14]/1000,
                                "mag": [v/1711 for v in pkt[15:18]],
                                "temp_ds": pkt[18]/16,
                                "gps": tuple(pkt[19:22]),
                                "gps_fix": pkt[22],
                                "scd41": pkt[23],
                                "mq4": pkt[24],
                                "me2o2": pkt[25],
                                "crc": pkt[-1]
                            }
                        except Exception as e:
                            self.log_ready.emit(f"[ERROR] Ошибка парсинга пакета: {e}")
                            buf = buf[60:]
                            continue
                        self.data_ready.emit(data)
                        self.last_data_time = time.time()
                        if self.f_csv and not self.f_csv.closed:
                            self.f_csv.write(";".join(str(x) for x in pkt) + "\n")
                        self.f_bin.write(chunk)
                        buf = buf[60:]
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
    def __init__(self):
        super().__init__()
        self._last_tooltip = 0.0
        layout = QGridLayout(self)
        layout.setSpacing(12)
        # ... (весь код карточек без изменений) ...
        self.pause_btn = QPushButton("⏸ Пауза")
        self.pause_btn.setFixedHeight(40)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS["btn_normal"]};
                color: {COLORS["text_primary"]};
                border-radius: 6px;
                font-size: 11pt;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: {COLORS["btn_hover"]}; }}
            QPushButton:pressed {{ background: {COLORS["btn_active"]}; }}
        """)
        self.pause_btn.clicked.connect(self.toggle_pause)
        layout.addWidget(self.pause_btn, 0, 0, 1, 2)

        self.cards = {}
        self._last_values = {}
        labels = [
            ("Номер пакета",    "packet_num"),
            ("Время, мс",       "timestamp"),
            ("Темп BMP, °C",    "temp_bmp"),
            ("Давл BMP, Па",    "press_bmp"),
            ("Ускор (X Y Z)",   "accel"),
            ("Угл.скор (X Y Z)","gyro"),
            ("Сост.аппарата",   "state"),
            ("Фото.рез, В",     "photo"),
            ("Магн.поле (X Y Z)","mag"),
            ("Темп DS18, °C",   "temp_ds"),
            ("GPS (lat lon h)", "gps"),
            ("GPS fix",         "gps_fix"),
            ("SCD41",           "scd41"),
            ("MQ-4, ppm",       "mq4"),
            ("ME2-O2, ppm",     "me2o2"),
            ("Контр.сумма",     "crc")
        ]
        for i, (title, key) in enumerate(labels):
            card = QFrame()
            card.setObjectName("card")
            # включаем hover-события и фильтр
            card.setAttribute(Qt.WA_Hover, True)
            card.installEventFilter(self)
            shadow = QGraphicsDropShadowEffect(card)
            shadow.setBlurRadius(12)
            shadow.setOffset(0, 4)
            shadow.setColor(QColor(0, 0, 0, 80))
            card.setGraphicsEffect(shadow)

            v = QVBoxLayout(card)
            v.setContentsMargins(10, 8, 10, 8)
            t = QLabel(title, objectName="title")
            val = QLabel("-", objectName="value")
            card.setToolTipDuration(1000)
            card.setToolTip(f"{title}: -")
            val.setContextMenuPolicy(Qt.CustomContextMenu)
            val.customContextMenuRequested.connect(
                lambda pos, w=val: w.copy() if hasattr(w, 'copy') else QApplication.clipboard().setText(w.text())
            )
            val.setAlignment(Qt.AlignCenter)
            val.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            v.addWidget(t); v.addWidget(val)
            layout.addWidget(card, i//2 + 1, i%2)
            self.cards[key] = val

    @Slot(dict)
    def update_values(self, data):
        self._last_values = data.copy()
        if not self.pause_btn.isEnabled():
            self.pause_btn.setEnabled(True)
        for k, w in self.cards.items():
            if k in data:
                v = data[k]
                self._last_values[k] = data[k]
                w.setText(
                    ", ".join(f"{x:.2f}" for x in v)
                    if isinstance(v, (list, tuple))
                    else (f"{v:.2f}" if isinstance(v, float) else str(v))
                )

    @Slot(dict)
    def update_chart(self, data):
        # Температура
        t = data.get("temp_bmp", 0.0)
        self.series_temp.append(self.temp_index, t)
        self.temp_index += 1
        if self.series_temp.count() > 100:
            self.series_temp.remove(0)
        # Ускорение
        a = data.get("accel", [0,0,0])
        mag = math.sqrt(a[0]**2 + a[1]**2 + a[2]**2)
        self.series_acc.append(self.acc_index, mag)
        self.acc_index += 1
        if self.series_acc.count() > 100:
            self.series_acc.remove(0)

    @Slot()
    def toggle_pause(self):
        if hasattr(self, 'worker'):
            if self.worker.is_paused():
                self.worker.resume();    self.pause_btn.setText("⏸ Пауза")
            else:
                self.worker.pause();     self.pause_btn.setText("▶ Продолжить")

    def set_worker(self, worker):
        self.worker = worker

        # + Replace the GraphsPage class with this enhanced version

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
    def __init__(self):
        super().__init__()
        self._orig_pos = {}
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
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QGridLayout(content)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll)
        scroll.setWidget(content)
        layout.setSpacing(12)
        self._grid_layout = self.findChild(QScrollArea).widget().layout()

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

        # Define all the charts we want to display
        chart_configs = [
            {"name": "temp_bmp", "title": "Температура BMP, °C", "color": "#5cceee", "y_range": [0, 40]},
            {"name": "press_bmp", "title": "Давление, Па", "color": "#ff9e80", "y_range": [80000, 110000]},
            {"name": "accel", "title": "Ускорение, g", "color": "#7bed9f", "y_range": [0, 3], "multi_axis": True,
             "axis_names": ["X", "Y", "Z"]},
            {"name": "gyro", "title": "Угловая скорость, °/с", "color": "#ffeb3b", "y_range": [-180, 180], "multi_axis": True,
             "axis_names": ["X", "Y", "Z"]},
            {"name": "mag", "title": "Магнитное поле", "color": "#ba68c8", "y_range": [-1, 1], "multi_axis": True,
             "axis_names": ["X", "Y", "Z"]},
            {"name": "temp_ds", "title": "Температура DS18B20, °C", "color": "#4db6ac", "y_range": [0, 40]},
            {"name": "photo", "title": "Фоторезистор, В", "color": "#fff176", "y_range": [0, 5]},
            {"name": "scd41", "title": "SCD41 (CO₂), ppm", "color": "#aed581", "y_range": [0, 2000]},
            {"name": "mq4", "title": "MQ-4 (CH₄), ppm", "color": "#f48fb1", "y_range": [0, 1000]},
            {"name": "me2o2", "title": "ME2-O2, ppm", "color": "#90caf9", "y_range": [0, 25]}
        ]

        # — load saved order —
        import configparser
        cfg = configparser.ConfigParser()
        cfg.read("config.ini")
        pos_map = {}
        if cfg.has_option("Layout", "chart_positions"):
            for token in cfg.get("Layout", "chart_positions").split(","):
                token = token.strip()
                # пропускаем пустые или некорректные записи
                if not token or token.count(":") != 2:
                    continue
                name, rs, cs = token.split(":")
                try:
                    pos_map[name] = (int(rs), int(cs))
                except ValueError:
                    # если не числа — пропустить
                    continue

        # Добавляем виджеты по сохранённым позициям, а незаписанные — в конец
        used = set()
        for config in chart_configs:
            name = config["name"]
            if name in pos_map:
                r, c = pos_map[name]
                w = self.create_chart(config)
                layout.addWidget(w, r, c)
                used.add(name)

        # Create charts
        row, col = 0, 0
        columns = 2  # Теперь две колонки вместо трех
        for config in chart_configs:
            name = config["name"]
            if name in used:
                continue
            w = self.create_chart(config)

            while layout.itemAtPosition(row, col) is not None:
                    col += 1
                    if col >= columns:
                        col = 0
                        row += 1
            layout.addWidget(w, row, col)

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
        """Create a chart based on configuration"""
        name = config["name"]
        title = config["title"]
        color = config["color"]
        y_range = config["y_range"]
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

            self.charts[name] = {
                "view": None,  # Will be set below
                "chart": chart,
                "series": series_list,
                "x_axis": ax_x,
                "y_axis": ax_y,
                "multi_axis": True,
                "y_range": y_range  # + Сохраняем исходный диапазон
            }
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

            self.charts[name] = {
                "view": None,  # Will be set below
                "chart": chart,
                "series": series,
                "x_axis": ax_x,
                "y_axis": ax_y,
                "multi_axis": False,
                "y_range": y_range  # + Сохраняем исходный диапазон
            }

        # Create chart view with enhanced rendering
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        # ➕ Включаем «резиновую рамку» для зума и пан
        #chart_view.setRubberBand(QChartView.RectangleRubberBand)
        chart_view.setRenderHint(QPainter.TextAntialiasing)
        chart_view.setRenderHint(QPainter.SmoothPixmapTransform)
        chart_view.setBackgroundBrush(Qt.transparent)
        chart_view.setMinimumHeight(250)

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
            # show the original Detach (“⇱”) button
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
        import time
        now = time.time()
        if not hasattr(self, '_last_chart_update'):
            self._last_chart_update = 0
        # не чаще 20 FPS
        if now - self._last_chart_update < 0.05:
            return
        self._last_chart_update = now
        """Update all charts with new data"""
        for name, chart_data in self.charts.items():
            if name not in data:
                continue
            # если вдруг нет default range — установить
            if name not in self.default_y_ranges:
                self.default_y_ranges[name] = tuple(chart_data["y_range"])

            chart_view = chart_data["view"]
            # блокируем перерисовку на время всех изменений
            chart_view.setUpdatesEnabled(False)

            chart_view = chart_data["view"]

            # + Блокируем обновления для предотвращения мерцания (без падений)
            try:
                chart_view.setUpdatesEnabled(False)
            except RuntimeError:
                # объект уже удалён на C++ стороне
                continue

            # ← вернуть определение переменных для обновления
            value      = data.get(name)
            index      = self.indexes.get(name, 0)
            x_axis     = chart_data["x_axis"]
            max_points = self.data_points.get(name, 200)
            # Check if this is a multi-axis chart
            if chart_data.get("multi_axis", False):
                # Multi-axis data (accel, gyro, mag)
                series_list = chart_data["series"]

                if isinstance(value, list) and len(value) >= 3:
                    data_values = []

                    for i in range(3):
                        series = series_list[i]
                        if series.count() >= max_points:
                            # быстро удаляем первые лишние точки
                            remove_cnt = series.count() - max_points + 1
                            series.removePoints(0, remove_cnt)

                        # Add new point
                        series.append(series.count(), value[i])
                        data_values.append(value[i])

                    # + Обновляем историю данных для автомасштабирования
                    history = self.data_history.get(name, [])
                    history.extend(data_values)
                    # Ограничиваем количество сохраненных точек
                    max_history = max_points * 3  # Храним максимум в 3 раза больше точек чем отображаем
                    if len(history) > max_history:
                        del history[:-max_history]
                    self.data_history[name] = history

                    # Auto-scale Y axis based on all three values
                    self.auto_scale_y_axis(name, data_values)

            else:
                # Single-value data
                series = chart_data["series"]

                if isinstance(value, (int, float)):
                    if series.count() >= max_points:
                        # быстро удаляем первые лишние точки
                        remove_cnt = series.count() - max_points + 1
                        series.removePoints(0, remove_cnt)

                    # Add new point
                    series.append(series.count(), value)

                    # + Обновляем историю данных
                    history = self.data_history.get(name, [])
                    history.append(value)
                    # Ограничиваем количество сохраненных точек
                    if len(history) > max_points * 3:
                        history = history[-max_points*3:]
                    self.data_history[name] = history

                    # Auto-scale Y axis based on current value
                    self.auto_scale_y_axis(name, [value])

            # Update index
            self.indexes[name] = index + 1

            # ➕ Скользящее окно: показываем только последние max_points точек
            if chart_data.get("multi_axis", False):
                cnt = chart_data["series"][0].count()
            else:
                cnt = chart_data["series"].count()
            start = max(0, cnt - max_points)
            end   = cnt + 5
            x_axis.setRange(start, end)

            # после всех series операций — разблокировать
            chart_view.setUpdatesEnabled(True)
            chart_view.update()
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
                self.add_log_message(f"[ERROR] Log directory missing: log")
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

# === ГЛАВНОЕ ОКНО ===
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Telemetry Dashboard")
        # ➕ Статус-бар и прогресс-бар симуляции
        self.setStatusBar(QStatusBar(self))
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.statusBar().addPermanentWidget(self.progress_bar)
        self.resize(600,400)
        self.setWindowTitle("Главное окно")
        self.setGeometry(100, 100, 600, 400)
        label = QLabel("Главное окно приложения", self)
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)
        apply_dark_theme(QApplication.instance())

        # Pages
        self.tel      = TelemetryPage()
        self.graphs   = GraphsPage()
        self.log_page = LogPage()
        self.settings = SettingsPage()
        self.console  = ConsolePage()

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
            {"name": "Console",   "icon": "💻", "index": 4}
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

        # ➕ версия приложения внизу боковой панели
        ver_lbl = QLabel(f"Version {APP_VERSION}")
        ver_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 8pt;")
        ver_lbl.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(ver_lbl)

        self.nav_buttons[0].setChecked(True)
        sidebar_layout.addStretch()
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
        for page in (self.tel, self.graphs, self.log_page, self.settings, self.console):
            page.setAttribute(Qt.WA_TranslucentBackground)
            self.stack.addWidget(page)
        grid.addWidget(self.stack, 0, 0)

        # растянуть оба на весь доступный space
        grid.setRowStretch(0, 1)
        grid.setColumnStretch(0, 1)
        main_layout.addWidget(content_area)

        self.setCentralWidget(main_widget)

        # Telemetry worker
        self.worker = TelemetryWorker("COM3", 9600)

        # Буфер пакетов и таймер для отложенного UI-обновления
        self.packet_buffer = deque(maxlen=100)  # хранить только 100 самых свежих пакетов
        self.last_data = None
        self.ui_timer      = QTimer(self)
        self.ui_timer.timeout.connect(self.flush_buffered_packets)
        self.ui_timer.start(50)  # обновлять UI не чаще чем раз в 50 ms

        # ➕ При окончании симуляции — чекаем графики и буфер
        self.worker.sim_ended.connect(self.graphs.reset_charts)
        self.worker.sim_ended.connect(lambda: (
            self.tel.pause_btn.setText("⏸ Пауза"),
            self.tel.pause_btn.setEnabled(False)
        ))
        self.worker.sim_ended.connect(lambda: self.packet_buffer.clear())

        self.tel.set_worker(self.worker)
        self.worker.data_ready.connect(self.packet_buffer.append)
        self.worker.log_ready.connect(self.log_page.add_log_message)
        self.worker.error_crc.connect(QApplication.beep)

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
        self.progress_bar.setVisible(idx == 0)

        # все тяжёлые вещи — через QTimer.singleShot(0,…)
        QTimer.singleShot(0, self._start_simulation)

    def _start_simulation(self):
        print("[UI] _start_simulation triggered")
        # 1) снимем паузу
        self.worker.resume()
        # 2) сбросим UI-буфер
        self.packet_buffer.clear()
        # 3) очистим графики
        #self.graphs.reset_charts()
        # 4) деактивируем кнопку Pause до начала прихода данных
        self.tel.pause_btn.setEnabled(False)

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
        if self.packet_buffer:
            try:
                data = self.packet_buffer.pop()
                print(f"[UI] Got telemetry: {data}")
                self.packet_buffer.clear()
                self.last_data = data
                self.tel.update_values(data)
                self.graphs.update_charts(data)
            except Exception as e:
                print(f"[UI] flush_buffered_packets error: {e}")

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

    @Slot(int, int)
    def _on_simulation_progress(self, pos: int, total: int):
        """Обновляем прогресс-бар в процентах."""
        pct = int(pos * 100 / total) if total else 0
        self.progress_bar.setValue(pct)

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
            # взять задержку из системного монитора
            self.console.write_response(self.graphs.lat_label.text())
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
            self.console.write_response("Grib Telemetry Dashboard v2.1 — program 'grib'")
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    sys.exit(app.exec())
