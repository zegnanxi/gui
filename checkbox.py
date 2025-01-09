from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QCheckBox

app = QApplication([])
widget = QWidget()
layout = QVBoxLayout(widget)

check_box = QCheckBox('Check me', widget)
layout.addWidget(check_box)

check_box.stateChanged.connect(lambda state: print(f'Checked: {check_box.isChecked()}'))

widget.setWindowTitle('QCheckBox Example')
widget.resize(300, 200)
widget.show()
app.exec()
