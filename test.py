import sys
from PySide6.QtWidgets import*

class IconLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setText('hello')


app = QApplication(sys.argv)
lab = IconLabel()
lab.show()
sys.exit(app.exec())