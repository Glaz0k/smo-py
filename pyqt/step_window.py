from typing import Optional
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from my_simulator import MySimulator
from pyqt.report_window import ReportWindow
from simulator.components import Request, SpecialEvent, SpecialEventType
from simulator.statistics import MAX_TIME


class StepWindow(QWidget):
    def __init__(self, simulator: MySimulator):
        super().__init__()
        self.simulator = simulator
        self.init_UI()
        self.update_values()
        
    def init_UI(self):
        self.setWindowTitle('Пошаговый режим симуляции')
        self.resize(900, 700)
        
        # Время
        time_group = QGroupBox('Время')
        time_layout = QVBoxLayout()
        self.time_label = QLabel(str(self.simulator.current_simulation_time))
        self.time_label.setAlignment(Qt.AlignCenter)
        time_font = QFont()
        time_font.setPointSize(14)
        self.time_label.setFont(time_font)
        time_layout.addWidget(self.time_label)
        time_group.setLayout(time_layout)
        
        # Событие
        event_group = QGroupBox('Событие')
        event_layout = QVBoxLayout()
        self.event_label = QLabel('')
        self.event_label.setAlignment(Qt.AlignCenter)
        self.event_label.setFont(time_font)
        event_layout.addWidget(self.event_label)
        event_group.setLayout(event_layout)
        
        # Верхняя панель
        top_panel = QHBoxLayout()
        top_panel.addWidget(time_group, 1)
        top_panel.addWidget(event_group, 1)
        
        # Таблица "Календарь источников"
        sources_group = QGroupBox('Календарь источников')
        sources_layout = QVBoxLayout()
        self.sources_table = QTableWidget()
        self.sources_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.sources_table.setColumnCount(3)
        self.sources_table.setRowCount(len(self.simulator.source_statistics))
        self.sources_table.setHorizontalHeaderLabels(['i', 'След. событие', 'Знак'])
        self.sources_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sources_table.verticalHeader().setVisible(False)
        sources_layout.addWidget(self.sources_table)
        sources_group.setLayout(sources_layout)
        
        # Таблица "Календарь приборов"
        devices_group = QGroupBox('Календарь приборов')
        devices_layout = QVBoxLayout()
        self.devices_table = QTableWidget()
        self.devices_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.devices_table.setColumnCount(4)
        self.devices_table.setRowCount(len(self.simulator.device_statistics))
        self.devices_table.setHorizontalHeaderLabels(['i', 'След. событие', 'Знак', 'Запрос'])
        self.devices_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.devices_table.verticalHeader().setVisible(False)
        devices_layout.addWidget(self.devices_table)
        devices_group.setLayout(devices_layout)
        
        # Панель устройств
        mid_panel = QHBoxLayout()
        mid_panel.addWidget(sources_group, 1)
        mid_panel.addWidget(devices_group, 1)

        # Таблица "Буфер"
        buffer_group = QGroupBox('Буфер')
        buffer_layout = QVBoxLayout()
        self.buffer_table = QTableWidget()
        self.buffer_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.buffer_table.setColumnCount(self.simulator.buffer_capacity)
        self.buffer_table.setHorizontalHeaderLabels([str(i) for i in range(self.simulator.buffer_capacity)])
        self.buffer_table.setRowCount(1)
        self.buffer_table.setVerticalHeaderLabels(['Значения:'])
        self.buffer_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        buffer_layout.addWidget(self.buffer_table)
        buffer_group.setLayout(buffer_layout)
        buffer_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        
        # Панель кнопок
        button_layout = QHBoxLayout()
        
        self.step_btn = QPushButton('Шаг')
        self.step_btn.setFixedSize(100, 40)
        self.step_btn.clicked.connect(self.step_simulation)
        
        self.end_btn = QPushButton('Конец симуляции')
        self.end_btn.setFixedSize(150, 40)
        self.end_btn.clicked.connect(self.end_simulation)
        
        self.report_btn = QPushButton('Отчёт')
        self.report_btn.setFixedSize(100, 40)
        self.report_btn.clicked.connect(self.show_report)
        self.report_btn.setEnabled(False)
        
        button_layout.addWidget(self.step_btn)
        button_layout.addWidget(self.end_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.report_btn)
        
        # Основной Layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_panel)
        main_layout.addLayout(mid_panel)
        main_layout.addWidget(buffer_group)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def update_values(self):
        for i, source_stat in enumerate(self.simulator.source_statistics):
            time, sign = get_time_and_sign(source_stat.next_request_time)
            row = [str(i), str(time) if time else '', str(sign)]
            for j, value in enumerate(row):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.sources_table.setItem(i, j, item)
        
        for i, device_stat in enumerate(self.simulator.device_statistics):
            time, sign = get_time_and_sign(device_stat.next_request_time)
            row = [str(i), str(time) if time else '', str(sign), format_request(device_stat.current_request)]
            for j, value in enumerate(row):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.devices_table.setItem(i, j, item)

        for i, request in enumerate(self.simulator.fake_buffer):
            value = format_request(request)
            item = QTableWidgetItem(value)
            item.setTextAlignment(Qt.AlignCenter)
            self.buffer_table.setItem(0, i, item)
        for i in range(len(self.simulator.fake_buffer), self.simulator.buffer_capacity):
            value = format_request(None)
            item = QTableWidgetItem(value)
            item.setTextAlignment(Qt.AlignCenter)
            self.buffer_table.setItem(0, i, item)
    
    def step_simulation(self):
        event = self.simulator.step()
        self.time_label.setText(str(event.planned_time))
        self.event_label.setText(format_event(event))
        self.update_values()
        if (event.event_type == SpecialEventType.END_OF_SIMULATION):
            self.handle_end()
    
    def end_simulation(self):
        self.simulator.run_to_completion()
        self.time_label.setText(str(self.simulator.current_simulation_time))
        self.event_label.setText("Симуляция окончена")
        self.update_values()
        self.handle_end()
    
    def show_report(self):
        self.report_window = ReportWindow(self.simulator)
        self.report_window.show()
        self.close()

    def handle_end(self):
        self.step_btn.setEnabled(False)
        self.end_btn.setEnabled(False)
        self.report_btn.setEnabled(True)

def get_time_and_sign(request_time: int) -> tuple[Optional[int], int]:
    if (request_time == MAX_TIME):
        return (None, 1)
    else:
        return (request_time, 0)
    
def format_request(request: Optional[Request]) -> str:
    if (request is None):
        return ""
    return f"{request.source_id}-{request.number}"

def format_event(event: SpecialEvent) -> str:
    match (event.event_type):
        case SpecialEventType.GENERATE_NEW_REQUEST:
            return f"Источник {event.event_id} создал новый запрос"
        case SpecialEventType.DEVICE_RELEASE:
            return f"Прибор {event.event_id} освободился"
        case SpecialEventType.END_OF_SIMULATION:
            return "Симуляция окончена"