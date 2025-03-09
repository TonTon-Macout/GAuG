VERSION = 0.1
import sys
import zlib
import struct
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QTextEdit, QPushButton, QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt

# Функция для создания GZIP-данных
def compress_to_gzip(data):
    compressor = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)
    compressed_data = compressor.compress(data) + compressor.flush()
    gzip_header = bytearray([0x1f, 0x8b, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0a])
    crc = zlib.crc32(data) & 0xffffffff
    size = len(data) & 0xffffffff
    gzip_footer = struct.pack("<LL", crc, size)
    return gzip_header + compressed_data + gzip_footer

# Функция для преобразования байтов в массив C-стиля
def bytes_to_c_array(data, add_progmem=False):
    result = "{\n    "
    for i, byte in enumerate(data):
        if i % 16 == 0 and i != 0:
            result += "\n    "
        result += f"0x{byte:02x}"
        if i < len(data) - 1:
            result += ", "
    result += "\n};"
    if add_progmem:
        result = "const uint8_t data[] PROGMEM = " + result
    return result

# Функция для преобразования массива C-стиля в байты
def c_array_to_bytes(c_array):
    print("Начало преобразования массива в байты...")
    c_array = re.sub(r'^.*?(?=\{)', '', c_array)
    c_array = re.sub(r'\}.*?$', '}', c_array)
    byte_values = re.findall(r'0x[0-9a-fA-F]{2}', c_array)
    if not byte_values:
        raise ValueError("Не удалось извлечь байты из массива")
    print(f"Извлечено {len(byte_values)} байтов: {byte_values[:10]}...")
    return bytes(int(x, 16) for x in byte_values)

# Проверка, является ли текст массивом C-стиля
def is_c_array(text):
    return bool(re.search(r'{\s*(0x[0-9a-fA-F]{2}(,\s*0x[0-9a-fA-F]{2})*\s*)*}', text))

# Главное окно приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GZip-Array-UnGZip")
        self.setGeometry(100, 100, 600, 500)

        # Основной виджет и layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)




        # Чекбоксы в одной строке
        checkbox_layout = QHBoxLayout()

        self.on_top_checkbox = QCheckBox("Поверх всех окон")
        self.on_top_checkbox.setChecked(False)
        self.on_top_checkbox.stateChanged.connect(self.toggle_on_top)
        checkbox_layout.addWidget(self.on_top_checkbox)
        layout.addLayout(checkbox_layout)

        self.progmem_checkbox = QCheckBox("Добавить (const uint8_t data[] PROGMEM =)")
        self.progmem_checkbox.setChecked(False)
        checkbox_layout.addWidget(self.progmem_checkbox)



        # Поле ввода
        input_label = QLabel("Введите текст или массив байтов:")
        layout.addWidget(input_label)
        self.input_text = QTextEdit()
        self.input_text.textChanged.connect(self.update_buttons)
        layout.addWidget(self.input_text)

        # Кнопки "Запаковать" и "Распаковать"
        button_layout = QHBoxLayout()
        self.pack_button = QPushButton("Запаковать")
        self.pack_button.clicked.connect(self.pack_data)
        self.pack_button.setEnabled(True)
        button_layout.addWidget(self.pack_button)

        self.unpack_button = QPushButton("Распаковать")
        self.unpack_button.clicked.connect(self.unpack_data)
        self.unpack_button.setEnabled(False)
        button_layout.addWidget(self.unpack_button)
        layout.addLayout(button_layout)

        # Поле вывода
        output_label = QLabel("Результат:")
        layout.addWidget(output_label)
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(False)
        layout.addWidget(self.output_text)

        # Кнопки "Копировать" и "Очистить"
        bottom_button_layout = QHBoxLayout()
        self.copy_button = QPushButton("Копировать")
        self.copy_button.clicked.connect(self.copy_result)
        bottom_button_layout.addWidget(self.copy_button)

        self.clear_button = QPushButton("Очистить")
        self.clear_button.clicked.connect(self.clear_fields)
        bottom_button_layout.addWidget(self.clear_button)
        layout.addLayout(bottom_button_layout)

    # Функция для запаковки
    def pack_data(self):
        input_text = self.input_text.toPlainText().strip()
        if not input_text:
            self.show_error("Введите данные для сжатия!")
            return
        
        try:
            data = input_text.encode('utf-8')
            gzip_data = compress_to_gzip(data)
            add_progmem = self.progmem_checkbox.isChecked()
            result = bytes_to_c_array(gzip_data, add_progmem)
            self.output_text.clear()
            self.output_text.setPlainText(result)
            QApplication.processEvents()
            self.output_text.repaint()
        except Exception as e:
            self.show_error(f"Не удалось запаковать данные: {str(e)}")

    # Функция для распаковки
    def unpack_data(self):
        input_text = self.input_text.toPlainText().strip()
        if not input_text:
            self.show_error("Введите массив для распаковки!")
            return
        
        try:
            print("Запуск распаковки...")
            gzip_data = c_array_to_bytes(input_text)
            print(f"Получено {len(gzip_data)} байтов GZIP-данных")
            decompressed_data = zlib.decompress(gzip_data, 16 + zlib.MAX_WBITS)
            print("Декомпрессия успешна!")
            result = decompressed_data.decode('utf-8')
            print(f"Распакованный текст: {result[:50]}...")
            self.output_text.clear()
            self.output_text.setPlainText(result)
            QApplication.processEvents()
            self.output_text.repaint()
        except Exception as e:
            self.show_error(f"Не удалось распаковать данные: {str(e)}")
            print(f"Ошибка при распаковке: {str(e)}")

    # Функция для копирования результата в буфер обмена
    def copy_result(self):
        result_text = self.output_text.toPlainText().strip()
        if result_text:
            clipboard = QApplication.clipboard()
            clipboard.setText(result_text)
            print("Результат скопирован в буфер обмена")
            QMessageBox.information(window, "Info", "Результат скопирован в буфер обмена!")
        else:
            
            self.show_error("Нечего копировать!")

    # Функция для очистки полей
    def clear_fields(self):
        self.input_text.clear()
        self.output_text.clear()
        print("Поля очищены")
        QApplication.processEvents()

    # Обновление состояния кнопок
    def update_buttons(self):
        input_text = self.input_text.toPlainText().strip()
        if is_c_array(input_text):
            self.pack_button.setEnabled(False)
            self.unpack_button.setEnabled(True)
           
        else:
            self.pack_button.setEnabled(True)
            self.unpack_button.setEnabled(False)
            

    # Функция для переключения "Поверх всех окон"
    def toggle_on_top(self, state):
        if state == Qt.CheckState.Checked.value:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()

    # Показать сообщение об ошибке
    def show_error(self, message):
        self.output_text.clear()
        self.output_text.setPlainText(f"Ошибка: {message}")
        QApplication.processEvents()
        self.output_text.repaint()

# Запуск приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())