from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QFileDialog, 
    QListWidgetItem, QLabel, QMessageBox
)
from PySide6.QtGui import QPixmap, QIcon, QColor, QFont, QPainter, QPen, QBrush
from PySide6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve
from PIL import Image
import sys
import os
import json

SAVE_FILE = "selected_images.json"

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Arial", 12))
        self.setStyleSheet("""
            QPushButton {
                background-color:rgb(234, 94, 0);
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
                border: none;
            }
            QPushButton:hover {
                background-color:rgb(216, 174, 59);
            }
            QPushButton:pressed {
                background-color: #03dac6;
            }
        """)

class ImagesToPDF(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image To PDF")
        self.setGeometry(100, 100, 1200, 720)
        self.setStyleSheet("background-color: #121212; color: white; font-size: 14px;")

        # ** التخطيط العام أفقي **
        self.main_layout = QHBoxLayout()

        # ** القائمة الجانبية (اليمين) **
        self.right_panel = QVBoxLayout()
        self.right_panel.setSpacing(10)
        self.right_panel.setContentsMargins(10, 10, 10, 10)

        # أزرار التحكم
        self.buttons_layout = QHBoxLayout()
        
        self.button_add = ModernButton("📷 إضافة صور")
        self.button_add.clicked.connect(self.load_images)
        self.buttons_layout.addWidget(self.button_add)

        self.button_remove = ModernButton("❌ إزالة المحددة")
        self.button_remove.clicked.connect(self.remove_selected_image)
        self.buttons_layout.addWidget(self.button_remove)

        self.button_clear_all = ModernButton("🗑️ مسح الكل")
        self.button_clear_all.clicked.connect(self.clear_all_images)
        self.buttons_layout.addWidget(self.button_clear_all)
        
        self.right_panel.addLayout(self.buttons_layout)

        # قائمة الصور
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border-radius: 10px;
                padding: 10px;
                border: 1px solid #333;
            }
            QListWidget::item {
                color: white;
                padding: 10px;
                border-bottom: 1px solid #333;
            }
            QListWidget::item:hover {
                background-color: #333;
            }
            QListWidget::item:selected {
                background-color: #6200ea;
            }
        """)
        self.list_widget.setIconSize(QPixmap(80, 80).size())
        self.list_widget.setDragDropMode(QListWidget.InternalMove)  # تمكين السحب والإفلات
        self.list_widget.itemClicked.connect(self.show_preview)
        self.right_panel.addWidget(self.list_widget)

        # زر تحويل الصور إلى PDF
        self.pdf_button = ModernButton("📄 تحويل إلى PDF")
        self.pdf_button.setEnabled(False)
        self.pdf_button.clicked.connect(self.convert_to_pdf)
        self.right_panel.addWidget(self.pdf_button)

        self.main_layout.addLayout(self.right_panel, 3)  # القائمة تأخذ 30% من المساحة

        # ** جزء المعاينة (اليسار) **
        self.preview_label = QLabel("📌 اضغط على صورة لمعاينتها هنا")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px solid #333;
                border-radius: 10px;
                padding: 10px;
                background-color: #1e1e1e;
                font-size: 16px;
                color: white;
            }
        """)
        self.main_layout.addWidget(self.preview_label, 7)  # المعاينة تأخذ 70% من المساحة

        self.setLayout(self.main_layout)
        self.load_saved_images()

    def load_images(self):
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(
            self, "اختر الصور", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp)"
        )

        if file_paths:
            sorted_files = sorted(file_paths, key=lambda x: os.path.basename(x).lower())
            for file_path in sorted_files:
                if not self.is_image_already_added(file_path):
                    item = QListWidgetItem(os.path.basename(file_path))
                    item.setIcon(QIcon(QPixmap(file_path).scaled(80, 80)))
                    item.setData(Qt.UserRole, file_path)  # تخزين المسار الكامل
                    self.list_widget.addItem(item)
            
            self.pdf_button.setEnabled(True)
            self.save_images()

    def is_image_already_added(self, file_path):
        """تجنب تكرار نفس الصورة أكثر من مرة"""
        for index in range(self.list_widget.count()):
            if self.list_widget.item(index).data(Qt.UserRole) == file_path:
                return True
        return False

    def remove_selected_image(self):
        """إزالة الصورة المحددة من القائمة وإخفاء المعاينة"""
        selected_item = self.list_widget.currentItem()
        if selected_item:
            row = self.list_widget.row(selected_item)
            self.list_widget.takeItem(row)
            self.preview_label.setText("📌 اضغط على صورة لمعاينتها هنا")  # إعادة النص الافتراضي للمعاينة
            self.preview_label.setPixmap(QPixmap())  # إزالة أي صورة معاينة
            
            self.save_images()
            if self.list_widget.count() == 0:
                self.pdf_button.setEnabled(False)

    def clear_all_images(self):
        """حذف جميع الصور وإعادة ضبط الواجهة"""
        self.list_widget.clear()
        self.preview_label.setText("📌 اضغط على صورة لمعاينتها هنا")  # إعادة النص الافتراضي
        self.preview_label.setPixmap(QPixmap())  # إزالة أي صورة معاينة
        self.pdf_button.setEnabled(False)
        
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)  # حذف ملف الحفظ

    def show_preview(self, item):
        """عرض الصورة في قسم المعاينة عند الضغط عليها"""
        file_path = item.data(Qt.UserRole)
        pixmap = QPixmap(file_path).scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_label.setPixmap(pixmap)

    def convert_to_pdf(self):
        """تحويل الصور إلى PDF"""
        if self.list_widget.count() == 0:
            return

        options = QFileDialog.Options()
        pdf_path, _ = QFileDialog.getSaveFileName(self, "حفظ PDF", "", "PDF Files (*.pdf)", options=options)
        
        if pdf_path:
            images = []
            for index in range(self.list_widget.count()):
                file_path = self.list_widget.item(index).data(Qt.UserRole)
                img = Image.open(file_path).convert("RGB")
                images.append(img)
            
            if images:
                images[0].save(pdf_path, save_all=True, append_images=images[1:])
                QMessageBox.information(self, "تم الحفظ", f"تم حفظ PDF بنجاح في:\n{pdf_path}")

    def save_images(self):
        """حفظ قائمة الصور عند إغلاق التطبيق"""
        image_paths = [self.list_widget.item(i).data(Qt.UserRole) for i in range(self.list_widget.count())]
        with open(SAVE_FILE, "w") as f:
            json.dump(image_paths, f)

    def load_saved_images(self):
        """تحميل الصور المحفوظة عند فتح التطبيق"""
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r") as f:
                image_paths = json.load(f)

            for file_path in image_paths:
                if os.path.exists(file_path):
                    item = QListWidgetItem(os.path.basename(file_path))
                    item.setIcon(QIcon(QPixmap(file_path).scaled(80, 80)))
                    item.setData(Qt.UserRole, file_path)
                    self.list_widget.addItem(item)
            
            if self.list_widget.count() > 0:
                self.pdf_button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImagesToPDF()
    window.show()
    sys.exit(app.exec())