from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QFileDialog, QListWidgetItem
from PySide6.QtGui import QPixmap, QIcon
from PIL import Image
import sys
import os

class ImagesToPDF(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image To PDF")
        self.setGeometry(100, 100, 400, 500)
        
        self.layout = QVBoxLayout()
        
        # زر اختيار الصور
        self.button = QPushButton("اختر الصور")
        self.button.clicked.connect(self.load_images)
        self.layout.addWidget(self.button)
        
        # قائمة الصور
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QPixmap(100, 100).size())
        self.list_widget.setDragDropMode(QListWidget.InternalMove)  # تمكين السحب والإفلات
        self.layout.addWidget(self.list_widget)
        
        # زر تحويل الصور إلى PDF
        self.pdf_button = QPushButton("تحويل إلى PDF")
        self.pdf_button.setEnabled(False)  # يبدأ غير مفعل
        self.pdf_button.clicked.connect(self.convert_to_pdf)
        self.layout.addWidget(self.pdf_button)
        
        self.setLayout(self.layout)
    
    def load_images(self):
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(self, "اختر الصور", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        
        if file_paths:
            self.list_widget.clear()
            sorted_files = sorted(file_paths, key=lambda x: os.path.basename(x).lower())  # ترتيب بالاسم
            
            for file_path in sorted_files:
                item = QListWidgetItem(os.path.basename(file_path))
                item.setIcon(QIcon(QPixmap(file_path).scaled(100, 100)))  # عرض الصورة كأيقونة
                item.setData(256, file_path)  # تخزين المسار الكامل
                self.list_widget.addItem(item)
            
            self.pdf_button.setEnabled(True)  # تفعيل زر PDF عند إضافة صور
        else:
            self.pdf_button.setEnabled(False)  # تعطيل زر PDF إذا لم يتم اختيار صور
    
    def convert_to_pdf(self):
        if self.list_widget.count() == 0:
            return
        
        file_dialog = QFileDialog()
        pdf_path, _ = file_dialog.getSaveFileName(self, "حفظ PDF", "", "PDF Files (*.pdf)")
        
        if pdf_path:
            images = []
            for index in range(self.list_widget.count()):
                file_path = self.list_widget.item(index).data(256)
                img = Image.open(file_path).convert("RGB")
                images.append(img)
            
            if images:
                images[0].save(pdf_path, save_all=True, append_images=images[1:])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImagesToPDF()
    window.show()
    sys.exit(app.exec())
