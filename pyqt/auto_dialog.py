from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from my_simulator import MySimulator
from pyqt.report_window import ReportWindow

class AutoDialog(QDialog):
    def __init__(self, simulator: MySimulator, parent: QWidget | None = None):
        super().__init__(parent)
        self.simulator = simulator
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Параметры автоматического режима')
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Поле для целевой вероятности отказа
        prob_group = QGroupBox('Целевая вероятность отказа')
        prob_layout = QHBoxLayout()
        self.prob_input = QDoubleSpinBox()
        self.prob_input.setRange(0.0, 1.0)
        self.prob_input.setSingleStep(0.001)
        self.prob_input.setDecimals(6)
        self.prob_input.setValue(0.05)
        prob_layout.addWidget(self.prob_input)
        prob_group.setLayout(prob_layout)
        
        # Поле для среднего времени обслуживания
        time_group = QGroupBox('Среднее время обслуживания новых приборов')
        time_layout = QHBoxLayout()
        self.time_input = QSpinBox()
        self.time_input.setRange(1, 1000)
        self.time_input.setValue(100)
        time_layout.addWidget(self.time_input)
        time_group.setLayout(time_layout)
        
        # Поле для предела количества заявок
        limit_group = QGroupBox('Предел количества заявок')
        limit_layout = QHBoxLayout()
        self.limit_input = QSpinBox()
        self.limit_input.setRange(100, 1000000)
        self.limit_input.setValue(1000)
        limit_layout.addWidget(self.limit_input)
        limit_group.setLayout(limit_layout)
        
        # Кнопки
        button_layout = QHBoxLayout()
        calc_btn = QPushButton('Расчёт')
        calc_btn.setFixedHeight(40)
        calc_btn.clicked.connect(self.calculate)
        
        cancel_btn = QPushButton('Отмена')
        cancel_btn.setFixedHeight(40)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(calc_btn)
        
        # Собираем все вместе
        layout.addWidget(prob_group)
        layout.addWidget(time_group)
        layout.addWidget(limit_group)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def calculate(self):
        # Здесь должна быть логика расчёта
        target_rejection_probability = self.prob_input.value()
        max_requests = self.limit_input.value()
        average_new_device_processing_time = self.time_input.value()
        while (target_rejection_probability < calculate_trustworthy_probability(self.simulator, max_requests)):
            self.simulator.reset()
            self.simulator.add_new_device(average_new_device_processing_time)
        
        self.report_window = ReportWindow(self.simulator)
        self.report_window.show()
        self.accept()
        self.parent.close()

def calculate_trustworthy_probability(sim: MySimulator, max_requests: int) -> float:
    next_requests = 0
    prev_rejection = 0.0
    current_rejection = -1.0
    while (True):
        prev_rejection = current_rejection
        sim.run_to_completion()
        current_requests = sim.target_amount_of_requests
        current_rejection = sim.rejected_amount / current_requests
        if (abs((current_rejection - prev_rejection) / prev_rejection) < 0.1 or current_requests == max_requests):
            return current_rejection
        
        next_requests = int(calculate_next_target_amount_of_requests(current_rejection))
        if (next_requests >= max_requests):
            next_requests = max_requests

        sim.reset(next_requests)

def calculate_next_target_amount_of_requests(rejection_probability: float) -> float:
    t_a = 1.643
    delta = 0.1
    p = rejection_probability
    return (t_a * t_a * (1 - p)) / (p * delta * delta)