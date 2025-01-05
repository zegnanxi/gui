from PySide6.QtCore import QThread, Signal
import time

class OperationWorker(QThread):
    finished = Signal()  # 操作完成信号
    log_message = Signal(str)  # 添加日志信号
    
    def __init__(self, operation_type, **kwargs):
        super().__init__()
        self.operation_type = operation_type
        self.kwargs = kwargs

    def run(self):
        if self.operation_type == "power_reset":
            self.log_message.emit("Executing power reset...")
            Operation.power_reset()
            self.log_message.emit("Power reset completed\n")
        elif self.operation_type == "chip_reset":
            self.log_message.emit("Executing chip reset...")
            Operation.chip_reset()
            self.log_message.emit("Chip reset completed\n")
        elif self.operation_type == "upgrade":
            file_path = self.kwargs.get("file_path")
            self.log_message.emit(f"Upgrading firmware with file {file_path}...")
            Operation.upgrade(file_path)
            self.log_message.emit("Upgrade firmware completed\n")
        elif self.operation_type == "dump_log":
            self.log_message.emit("Exporting logs...")
            Operation.dump_log()
            self.log_message.emit("Log export completed\n")
        elif self.operation_type == "work_mode":
            mode_label = self.kwargs.get("mode_label")
            mode_value = self.kwargs.get("mode_value")
            self.log_message.emit(f"Switching to {mode_label}({mode_value})...")
            Operation.set_work_mode(mode_label, mode_value)
            self.log_message.emit(f"Work mode switched to: {mode_label}({mode_value})\n")
        self.finished.emit()

class Operation:
    @staticmethod
    def power_reset():
        """Execute power reset operation"""
        print("Executing power reset...")
        time.sleep(5)  # Simulate 5 second delay
        print("Power reset completed")

    @staticmethod
    def chip_reset():
        """Execute chip reset operation"""
        print("Executing chip reset...")
        time.sleep(5)  # Simulate 5 second delay
        print("Chip reset completed")

    @staticmethod
    def upgrade(file_path):
        """Execute upgrade operation"""
        print(f"Upgrading with file {file_path}...")
        time.sleep(5)  # Simulate 5 second delay
        print("Upgrade completed")

    @staticmethod
    def dump_log():
        """Execute log export operation"""
        print("Exporting logs...")
        time.sleep(5)  # Simulate 5 second delay
        print("Log export completed")

    @staticmethod
    def set_work_mode(mode_label, mode_value):
        """Set work mode"""
        print(f"Switching to {mode_label} (Mode value: {mode_value})...")
        time.sleep(5)  # Simulate 5 second delay
        print(f"Work mode switched to: {mode_label}")
