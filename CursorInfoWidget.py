from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont

class CursorInfoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | 
                          Qt.WindowType.FramelessWindowHint |
                          Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow)  # Specific for macOS
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create labels
        self.pos_label = QLabel("Position")
        self.type_label = QLabel("Cursor Type")
        self.app_label = QLabel("Active App")
        self.element_label = QLabel("Element Info")
        self.selected_text_label = QLabel("Selected Text")
        
        # Style labels
        font = QFont("Menlo", 11)
        for label in [self.pos_label, self.type_label, self.app_label, self.element_label, self.selected_text_label]:
            label.setFont(font)
            label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 180); padding: 5px; border-radius: 5px;")
            layout.addWidget(label)
        
        self.setLayout(layout)
        
        # Set initial position
        self.move(100, 100)

        print("CursorInfoWidget initialized")
        
        # For dragging window
        self.dragging = False
        self.offset = QPoint()
    
    def update_info(self, cursor_info):
        """Update the display with new cursor information"""
        self.pos_label.setText(f"Position: ({int(cursor_info['x'])}, {int(cursor_info['y'])})")
        self.type_label.setText(f"Cursor: {cursor_info['cursor_type']}")
        self.app_label.setText(f"App: {cursor_info['active_app'].get('app_name', 'Unknown')}")
        
        element = cursor_info['element_info']
        if element:
            role = element.get('AXRole', '')
            role_des = element.get('AXRoleDescription', '')
            title = element.get('AXRoleDescription', '')
            des = element.get('AXDescription','')
            self.element_label.setText(f"Element: {role}:{role_des} - {title}:{des}")
            if 'AXSelectedText' in element:
                self.selected_text_label.setText(f"Selected Text: {element['AXSelectedText']}")
            else:
                self.selected_text_label.setText("Selected Text: ")
        else:
            self.element_label.setText("Element: None")
        
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.mapToGlobal(event.pos() - self.offset))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False