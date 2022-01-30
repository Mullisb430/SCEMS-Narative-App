import sys, json, os
from datetime import date
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox
from patientModel import PatientModel

# Main window with narative inside
from NarativeWindow import Ui_MainWindow

# Patient management window with tableView that contains all the patient's data
from PatientManagementScreen import Ui_MainWindow as PatientWindow

filename = 'ptdata.json' 
filename_2 = 'ptnaratives.json'
if '_MEIPASS2' in os.environ:
    filename = os.path.join(os.environ['_MEIPASS2'], filename)
    filename_2 = os.path.join(os.environ['_MEIPASS2'], filename_2)
fd = open(filename, 'rb')



#---- Patient Window with table view ------------------------------------------------------------------------#

class PatientWindow(QtWidgets.QMainWindow, PatientWindow):
    def __init__(self):
        super().__init__()
        self.home = None
        self.setupUi(self)
        self.setFixedSize(748, 599)
        self.model = PatientModel()
        self.load()
        self.patientView.setModel(self.model)
        self.patientView.resizeColumnsToContents() # <- Makes tableview columns resize to fit their contents
        self.patientIDBox.setFocus()

        
        

        # Throwing it back to the home screen
        self.backHomeButton.pressed.connect(self.backHome)

        # Adding a patient and their data to the data file
        self.AddButton.pressed.connect(self.add)

        # Deleting a patient and their data from the data file
        self.deleteSelectionButton.pressed.connect(self.delete)

        # Clearing all fields in the "Add Patient" form section
        self.clearFieldsButton.pressed.connect(self.clear)

        # Selecting a patient row to edit
        self.editSelectionButton.pressed.connect(self.editPatient)

    def backHome(self):
        if self.home is None:
            self.home = MainWindow()
            self.home.show()
            self.close()
    
    def add(self): # everythingIsEntered() checks that all fields in the "Add Patient" section are filled out
        if self.everythingIsEntered(): 
            ptAddress = self.patientAddressBox.text()
            ptID = self.patientIDBox.text()
            ptDialysisName = self.patientDialysisNameBox.text()
            ptDialysisAddress = self.patientDialysisAddressBox.text()
            ptGender = self.getGender()
            birthMonth = self.birthMonthBox.value()
            birthDay = self.birthDayBox.value()
            birthYear = self.birthYearBox.value()

            # Saves all the data for the added patient in a single list and appends it to the list that holds
            # all patients
            self.model.patients.append([ptID, ptAddress, ptDialysisName, ptDialysisAddress, ptGender, birthMonth, birthDay, birthYear])

            self.model.layoutChanged.emit()
            self.patientView.resizeColumnsToContents()
            self.clear()
            self.save()

    def clear(self):
        self.patientIDBox.setText("")
        self.patientAddressBox.setText("")
        self.patientDialysisAddressBox.setText("")
        self.patientDialysisNameBox.setText("")
        self.maleCheckBox.setChecked(False)
        self.femaleCheckBox.setChecked(False)
        self.birthDayBox.setValue(1)
        self.birthMonthBox.setValue(1)
        self.birthYearBox.setValue(1900)

    def delete(self):
        indexes = self.patientView.selectedIndexes()

        if indexes:
            index = indexes[0]

            del self.model.patients[index.row()]
            self.model.layoutChanged.emit()
            self.patientView.clearSelection()
            self.save()

    def editPatient(self):
        indexes = self.patientView.selectedIndexes()

        if indexes:
            index = indexes[0]

            # Throws the selected patient's info back into the "Add Patient" form
            # so that the user can edit the patient's data
            self.patientIDBox.setText(self.model.patients[index.row()][0])
            self.patientAddressBox.setText(self.model.patients[index.row()][1])
            self.patientDialysisAddressBox.setText(self.model.patients[index.row()][3])
            self.patientDialysisNameBox.setText(self.model.patients[index.row()][2])
            if (self.model.patients[index.row()][4] == "male"):
                self.maleCheckBox.setChecked(True)
            else:
                self.femaleCheckBox.setChecked(True)
            self.birthDayBox.setValue(int(self.model.patients[index.row()][5]))
            self.birthMonthBox.setValue(int(self.model.patients[index.row()][6]))
            self.birthYearBox.setValue(int(self.model.patients[index.row()][7]))

            # Deletes the patient from the view.
            del self.model.patients[index.row()]
            self.model.layoutChanged.emit()
            self.patientView.clearSelection()
            self.save()

    def getGender(self):
        if (self.femaleCheckBox.isChecked()):
            return "female"
        elif (self.maleCheckBox.isChecked()):
            return "male"

    def load(self):
        try:
            with open(filename, 'r') as f:
                self.model.patients = json.load(f)
        except Exception:
            pass

    def save(self):
        with open(filename, 'w') as f:
            patients = json.dump(self.model.patients, f)

    def everythingIsEntered(self):
        if ((self.patientIDBox.text() == "") or (self.patientAddressBox.text() == "") or (self.patientDialysisNameBox.text() == "") or (self.patientDialysisAddressBox.text() == "") or (not self.maleCheckBox.isChecked() and not self.femaleCheckBox.isChecked()) or (self.birthYearBox.value() == 1900)):

        # Creates an "Error" QMessageBox object that pops up on the user's screen when one of the 
        # fields inside the "Add Patient" section is not filled out
            msg = QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msg.setText("Entry Error")
            msg.setInformativeText("One or more of the fields in the \"Add Patient\" form is not filled out!")
            msg.setWindowTitle("Error")
            msg.exec()
            return False
        else:
            return True









#---- Main Window with narative box ------------------------------------------------------------------------#


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.ptWindow = None
        self.setupUi(self)
        self.setFixedSize(668, 715)

        # Grabs all patientID's saved in storage and adds them to both of the selection boxes
        # on the narative main screen so the user can select from them
        self.fillSelectionBoxes()

        self.model = PatientModel()
        self.load()
        self.patientSelectionBox.setFocus()

        # Throwing it to the patient management screen
        self.patientManageButton.pressed.connect(self.managePatientScreen)
        
        # Make sure that when one of the below check boxes is checked then the other one is unchecked
        self.checkBoxBTrip.toggled.connect(lambda checked: checked and self.checkBoxATrip.setChecked(False))
        self.checkBoxATrip.toggled.connect(lambda checked: checked and self.checkBoxBTrip.setChecked(False))

        # Generates a normal dialysis trip narative
        self.generateButton.pressed.connect(self.generateNarative)

        # Generates a doctor's trip narative
        self.generateButton_2.pressed.connect(self.generateNarative_2)

    def managePatientScreen(self):
        if self.ptWindow is None:
            self.ptWindow = PatientWindow()
            self.ptWindow.show()
            self.close()

    def load(self):
        try:
            with open(filename, 'r') as f:
                self.model.patients = json.load(f)
        except Exception:
            pass

    def fillSelectionBoxes(self):
        with open("ptdata.json", 'r') as f:
            patients = json.load(f)
            
            for patient in patients:
                self.patientSelectionBox.addItem(patient[0])
                self.patientSelectionBox_2.addItem(patient[0])
        
    # Narative generation for regular dialysis trips
    def generateNarative(self):
        if (self.checkBoxATrip.isChecked() or self.checkBoxBTrip.isChecked()):
            patient = self.patientSelectionBox.currentText()
            patient_info = []

            if len(self.model.patients) > 0:

                # This if block executes when there is at least one patient saved
                for pt in self.model.patients:
                    if pt[0] == patient:
                        patient_info = pt
                        break

                with open(filename_2, 'r') as f:
                    narative = json.load(f)
                    if self.checkBoxATrip.isChecked():
                        workingNarative = narative[0]
                    elif self.checkBoxBTrip.isChecked():
                        workingNarative = narative[1]
                    else:
                        workingNarative = narative[0]

                workingNarative = workingNarative.replace('##', patient_info[1]).replace("%%", patient_info[2]).replace("&&", patient_info[3]).replace('$$', patient_info[4]).replace("@@", self.getAge(patient_info[5], patient_info[6], patient_info[7]))
            else:

                # This else block will only execute when there is no patient data stored
                workingNarative = "No patient info present!"

            self.narativeLabel.setText(workingNarative)
        else:
            msg = QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msg.setText("Entry Error")
            msg.setInformativeText("Please select either \"A Trip\" or \"B Trip\"")
            msg.setWindowTitle("Error")
            msg.exec()
            
        
    # Narative generation for doctor trips
    def generateNarative_2(self):
        patient = self.patientSelectionBox.currentText()
        patient_info = []
        tripType = self.doctorTripBox.currentText()

        if len(self.model.patients) > 0:

            # This if block executes when there is at least one patient saved
            for pt in self.model.patients:
                if pt[0] == patient:
                    patient_info = pt
                    break
            

            with open(filename_2, 'r') as f:
                narative = json.load(f)
                if tripType == "A trip from home to doctor":
                    workingNarative = narative[2]
                elif tripType == "A trip from dialysis to doctor":
                    workingNarative = narative[4]
                elif tripType == "B trip from doctor to home":
                    workingNarative = narative[3]
                elif tripType == "B trip from doctor to dialysis":
                    workingNarative = narative[5]

            workingNarative = workingNarative.replace('##', patient_info[1]).replace("%%", patient_info[2]).replace("&&", patient_info[3]).replace('$$', patient_info[4]).replace("@@", self.getAge(patient_info[5], patient_info[6], patient_info[7])).replace("**", self.doctorOfficeName.text()).replace("^^", self.doctorOfficeAddress.text())
        else:

            # This else block will only execute when there is no patient data stored
            workingNarative = "No Patient info present!"

        self.narativeLabel.setText(workingNarative)

    def getAge(self, month, day, year):
        today = date.today()
        return str(today.year - year - ((today.month, today.day) < (month, day)))



    
        

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()