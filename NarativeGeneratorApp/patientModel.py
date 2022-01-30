from PyQt6 import QtCore
from PyQt6.QtCore import Qt

class PatientModel(QtCore.QAbstractTableModel):
    def __init__(self, patients=[["", "", "", "", "", "", "", ""]]):
        super().__init__()
        self.patients = patients or [["", "", "", "", "", "", "", ""]]

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.patients[index.row()][index.column()]

    def rowCount(self, index):
        return len(self.patients)

    def columnCount(self, index):
        try:
            return len(self.patients[0])
        except:
            return 8

