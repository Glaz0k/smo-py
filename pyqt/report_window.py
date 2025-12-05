from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from my_simulator import MySimulator

class ReportWindow(QWidget):
    def __init__(self, simulator: MySimulator):
        super().__init__()
        self.initUI()
        self.form_report(simulator)
        
    def initUI(self):
        self.setWindowTitle('Отчёт симуляции')
        self.resize(1000, 800)
        
        main_layout = QVBoxLayout()
        
        # Таблица "Отчёт"
        report_group = QGroupBox('Отчёт')
        report_layout = QVBoxLayout()
        self.report_table = QTableWidget()
        self.report_table.setRowCount(1)
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels([
            'Общее время симуляции', 
            'Запросов получено', 
            'Запросов обработано', 
            'Запросов отклонено', 
            'Вероятность отказа'
        ])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.report_table.verticalHeader().setVisible(False)
        report_layout.addWidget(self.report_table)
        report_group.setLayout(report_layout)
        
        # Таблица "Источники"
        sources_group = QGroupBox('Источники')
        sources_layout = QVBoxLayout()
        self.sources_report_table = QTableWidget()
        self.sources_report_table.setColumnCount(8)
        self.sources_report_table.setHorizontalHeaderLabels([
            'i', 'Кол-во\n запросов', 'Вероятность\n отказа', 'Полное\n время',
            'Время\n буффера', 'Время\n обработки', 'Дисперсия\n буффера', 'Дисперсия\n обработки'
        ])
        self.sources_report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sources_report_table.verticalHeader().setVisible(False)
        sources_layout.addWidget(self.sources_report_table)
        sources_group.setLayout(sources_layout)
        
        # Таблица "Приборы"
        devices_group = QGroupBox('Приборы')
        devices_layout = QVBoxLayout()
        self.devices_report_table = QTableWidget()
        self.devices_report_table.setColumnCount(2)
        self.devices_report_table.setHorizontalHeaderLabels(['i', 'Коэффициент использования'])
        self.devices_report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.devices_report_table.verticalHeader().setVisible(False)
        devices_layout.addWidget(self.devices_report_table)
        devices_group.setLayout(devices_layout)
        
        # Собираем все вместе
        main_layout.addWidget(report_group)
        main_layout.addWidget(sources_group)
        main_layout.addWidget(devices_group)
        
        self.setLayout(main_layout)
    
    def form_report(self, sim: MySimulator):
        # Заполняем таблицу "Отчёт"
        for j, value in enumerate(form_report_data(sim)):
            item = QTableWidgetItem(value)
            item.setTextAlignment(Qt.AlignCenter)
            self.report_table.setItem(0, j, item)
        
        # Заполняем таблицу "Источники"
        source_data = form_source_data(sim)
        self.sources_report_table.setRowCount(len(source_data))
        for i, row in enumerate(source_data):
            for j, value in enumerate(row):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.sources_report_table.setItem(i, j, item)
        # Заполняем таблицу "Приборы"
        device_data = form_device_data(sim)
        self.devices_report_table.setRowCount(len(device_data))
        for i, row in enumerate(device_data):
            for j, value in enumerate(row):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.devices_report_table.setItem(i, j, item)

TABLE_ROUNDING = 3

def form_report_data(sim: MySimulator) -> list[str]:
    recieved = sim.current_amount_of_requests
    rejected = sim.rejected_amount
    report_data = [
        sim.current_simulation_time, 
        recieved, 
        recieved - rejected, 
        rejected, 
        round(rejected / recieved, TABLE_ROUNDING)
    ]
    return list(map(str, report_data))

def form_source_data(sim: MySimulator) -> list[list[str]]:
    source_data = []
    for i, source_stat in enumerate(sim.source_statistics):
        buffer_time = source_stat.avg_buffer_time()
        device_time = source_stat.avg_device_time()
        source_data.append(list(map(str, [
            i, 
            source_stat.generated, 
            round(source_stat.rejected / source_stat.generated, TABLE_ROUNDING),
            round(buffer_time + device_time, TABLE_ROUNDING),
            round(buffer_time, TABLE_ROUNDING),
            round(device_time, TABLE_ROUNDING),
            round(source_stat.variance_buffer_time(), TABLE_ROUNDING),
            round(source_stat.variance_device_time(), TABLE_ROUNDING)
        ])))
    return source_data
    
def form_device_data(sim: MySimulator) -> list[list[str]]:
    device_data = []
    for i, device_stat in enumerate(sim.device_statistics):
        device_data.append(list(map(str, [
            i, 
            round(device_stat.time_in_usage / sim.current_simulation_time, TABLE_ROUNDING)
        ])))
    return device_data