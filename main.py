import sys
import threading
import time
import traceback

from PIL import ImageOps
from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog,QVBoxLayout,QLabel,QScrollArea,QWidget
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap , QImage
import pytesseract
import glob
from Processing import get_titile
from PyQt5.QtCore import QThread,pyqtSignal,pyqtSlot,Qt
import os


pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract"






class Main(QMainWindow):
    # updateUi_signal = pyqtSignal(QImage, str)
    def __init__(self):
        super(Main, self).__init__()
        loadUi(r"./gui/gui.ui", self)


        self.btn_select_file.clicked.connect(self.on_clicked_select_file)
        self.btn_select_folder.clicked.connect(self.on_clicked_select_folder)
        self.btn_save.clicked.connect(self.rename_files)
        self.scrollArea.setWidgetResizable(True)

        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.layout = QVBoxLayout(self.scrollAreaWidgetContents)
        # self.updateUi_signal.connect(self.updateUI)

        self.p = ProcessFolder()
        self.p.updateUi_signal.connect(self.updateUI)




    def on_clicked_select_folder(self):
        self.remove_all_ui()
        self.folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder')

        self.p.set_folder(self.folderpath)
        self.p.start()



    def on_clicked_select_file(self):
        self.remove_all_ui()
        path = QFileDialog.getOpenFileName(self, 'Open a file', '',
                                           'All Files (*.pdf)')

        self.folderpath = path[0]

        self.p.set_folder(self.folderpath)
        self.p.start()

    def rename_files(self):
        text = self.te_outpu.toPlainText()
        texts = text.split("\n")
        print(texts)

        if os.path.isfile(self.folderpath):
            os.rename(self.folderpath,f"{os.path.dirname(self.folderpath)}/{texts[0]}.pdf")
        elif os.path.isdir(self.folderpath):
            for i,file in enumerate(glob.glob(f"{self.folderpath}/*.pdf")):
                os.rename(file, f"{self.folderpath}/{texts[i]}.pdf")


    @pyqtSlot(QImage,str)
    def updateUI(self,img,title):
        try:
            # self.add_image(img)
            self.layout.setSpacing(2)
            label = QLabel("")
            label.setMinimumHeight(800)
            image = img.scaled(label.size(), Qt.KeepAspectRatio)
            pix = QPixmap(image)
            label.setPixmap(pix)
            self.layout.addWidget(label)

            self.te_outpu.appendPlainText(f"{title}")
            self.repaint()
        except :
            traceback.print_exc()


    def add_image(self,image):

        self.layout.setSpacing(2)
        label = QLabel("")
        label.setMinimumHeight(800)
        image = image.scaled(label.size(), Qt.KeepAspectRatio)
        pix = QPixmap(image)
        label.setPixmap(pix)
        self.layout.addWidget(label)

    def remove_all_ui(self):
        number_of_labels = self.layout.count()
        for i in range(number_of_labels - 1, -1, -1):
            l = self.layout.itemAt(i)
            l.widget().setParent(None)
        self.te_outpu.clear()

class ProcessFolder(QThread):
    updateUi_signal = pyqtSignal(QImage, str)
    def __init__(self):
        super(ProcessFolder,self).__init__()


    def set_folder(self,folderpath):
        self.folderpath = folderpath


    def run(self):
        if os.path.isfile(self.folderpath):
            self.get_titile(self.folderpath)
        elif os.path.isdir(self.folderpath):
            self.get_titiles()

    def get_titiles(self):
        folderpath = self.folderpath
        try:
            for file in glob.glob(f"{folderpath}/*.pdf"):
                title, img = get_titile(file)
                image = QImage(img, img.shape[1], img.shape[0], img.shape[1] * 3,
                               QImage.Format_RGB888)
                self.updateUi_signal.emit(image, title)
                time.sleep(0.1) # This delay is needed to make sure the UI is updted before the thread is terminated
        except:
            traceback.print_exc()

    def get_titile(self,file):
        title, img = get_titile(file)
        image = QImage(img, img.shape[1], img.shape[0], img.shape[1] * 3,
                       QImage.Format_RGB888)
        self.updateUi_signal.emit(image, title)
        time.sleep(0.1)  # This delay is needed to make sure the UI is updted before the thread is terminated


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    try:
        sys.exit(app.exec_())
    except Exception as exp:
        print(exp)
        print("Exiting")