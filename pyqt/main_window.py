import json
from typing import Optional
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from my_simulator import MySimulator, SimulatorConfig, SimulatorLaw
from pyqt.auto_dialog import AutoDialog
from pyqt.step_window import StepWindow

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.simulator_config: Optional[SimulatorConfig] = None
        
    def initUI(self):
        self.setWindowTitle('Симулятор СМО')
        self.setFixedSize(400, 250)
        
        # Заголовок
        title = QLabel('Симуляция СМО')
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        
        # Выбор файла конфигурации
        self.file_label = QLabel('Файл не выбран')
        self.file_label.setStyleSheet('border: 1px solid gray; padding: 5px;')
        select_btn = QPushButton('Выбрать файл (.json)')
        select_btn.clicked.connect(self.select_config_file)
        
        config_layout = QHBoxLayout()
        config_layout.addWidget(self.file_label, 1)
        config_layout.addWidget(select_btn)

        config_group = QGroupBox('Выбор конфигурации')
        config_group.setLayout(config_layout)
        
        # Кнопки режимов
        step_btn = QPushButton('Пошаговый режим')
        step_btn.setFixedHeight(40)
        step_btn.clicked.connect(self.open_step_mode)
        
        auto_btn = QPushButton('Автоматический режим')
        auto_btn.setFixedHeight(40)
        auto_btn.clicked.connect(self.open_auto_mode)
        
        # Добавление элементов в основной layout
        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(config_group)
        layout.addSpacing(20)
        layout.addWidget(step_btn)
        layout.addWidget(auto_btn)
        layout.addStretch()
        self.setLayout(layout)
        
    def select_config_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Выберите файл конфигурации', '', 'JSON files (*.json)')
        if file_name:
            self.file_label.setText(file_name)
            try:
                with open(file_name, 'r') as f:
                    config_dict = json.load(f)
                    self.simulator_config = SimulatorConfig(
                        target_amount_of_requests = config_dict['requests'],
                        buffer_capacity = config_dict['buffer'],
                        source_periods = config_dict['sources'],
                        device_coefficients = config_dict['devices']
                    )
            except KeyError as e:
                QMessageBox.critical(self, 'Ошибка', 'Неверная конфигурация')
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить файл: {str(e)}')
    
    def open_step_mode(self):
        if not self.simulator_config:
            QMessageBox.warning(self, 'Внимание', 'Сначала выберите файл конфигурации!')
            return
        
        sim = MySimulator(self.simulator_config, SimulatorLaw.STOCHASTIC)
        self.step_window = StepWindow(sim)
        self.step_window.show()
        self.close()
    
    def open_auto_mode(self):
        if not self.simulator_config:
            QMessageBox.warning(self, 'Внимание', 'Сначала выберите файл конфигурации!')
            return
        
        sim = MySimulator(self.simulator_config, SimulatorLaw.STOCHASTIC)
        self.auto_dialog = AutoDialog(sim, self)
        self.auto_dialog.exec()