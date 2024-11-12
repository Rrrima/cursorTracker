from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QLineEdit
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont
import os
import subprocess

class CursorInfoWidget(QWidget):
    def __init__(self,tracker_callback=None, screenshots_path=None, note_callback=None):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | 
                          Qt.WindowType.FramelessWindowHint |
                          Qt.WindowType.Tool)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow)  # Specific for macOS
        
        # self.setFixedHeight(170)  # Adjust this value as needed

        self.tracking_enabled = True  # Track state
        self.tracker_callback = tracker_callback
        self.is_collapsed = False
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)  # Reduce space between labels

        # Create top bar with minimize button
        top_bar = QHBoxLayout()
        top_bar.addStretch()  # This pushes the minimize button to the right

        # Create minimize button
        self.minimize_button = QPushButton("_")
        self.minimize_button.setFont(QFont("Menlo", 9))
        self.minimize_button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: rgba(0, 0, 0, 180);
                padding: 3px;
                border-radius: 5px;
                width: 10px;
                height: 10px;
            }
            QPushButton:hover {
                background-color: rgba(40, 40, 40, 180);
            }
        """)
        self.minimize_button.clicked.connect(self.showMinimized)    


         # Create collapse button
        self.collapse_button = QPushButton("▼")  # ▼ for expanded, ▶ for collapsed
        self.collapse_button.setFont(QFont("Menlo", 9))
        self.collapse_button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: rgba(0, 0, 0, 180);
                padding: 3px;
                border-radius: 5px;
                width: 10px;
                height: 10px;
            }
            QPushButton:hover {
                background-color: rgba(40, 40, 40, 180);
            }
        """)
        self.collapse_button.clicked.connect(self.toggle_collapse)


        top_bar.addWidget(self.collapse_button)
        top_bar.addWidget(self.minimize_button)
        
        # Add top bar to main layout
        layout.addLayout(top_bar)
        
        # Create labels
        self.pos_label = QLabel("Position")
        self.type_label = QLabel("Cursor Type")
        self.action_label = QLabel("Action")
        self.app_label = QLabel("Active App")
        self.element_label = QLabel("Element Info")
        self.selected_text_label = QLabel("Selected Text")

        # Create container widget for collapsible content
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(2)

        # Move labels into content layout
        self.labels = [
            self.pos_label,
            self.type_label,
            self.action_label,
            self.app_label,
            self.element_label,
            self.selected_text_label
        ]
        
        # Style labels
        font = QFont("Menlo", 11)
        for label in self.labels:
            label.setFont(font)
            label.setStyleSheet("color: black; background-color: rgba(0, 0, 0, 20); padding: 5px; border-radius: 5px; max-width: 200px; height: 30px;")
            label.setFixedHeight(30)  # Force fixed height
            self.content_layout.addWidget(label)

        layout.addWidget(self.content_widget)

         # Add button container
        button_layout = QHBoxLayout()
        
        # Create control button
        self.control_button = QPushButton("Stop Tracking")
        self.control_button.setFont(QFont("Menlo", 11))
        self.control_button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: rgba(0, 0, 0, 180);
                padding: 5px;
                border-radius: 5px;
                min-width: 100px;
                height: 15px;
            }
            QPushButton:hover {
                background-color: rgba(40, 40, 40, 180);
            }
        """)
        self.control_button.clicked.connect(self.toggle_tracking)

        # create folder button
        self.folder_button = QPushButton("Screenshots")
        self.folder_button.setFont(QFont("Menlo", 11))
        self.folder_button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: rgba(0, 0, 0, 180);
                padding: 5px;
                border-radius: 5px;
                width: 30px;
                height: 15px;
            }
            QPushButton:hover {
                background-color: rgba(40, 40, 40, 180);
            }
        """)
        self.screenshots_path = screenshots_path
        self.folder_button.clicked.connect(self.open_folder)

        
        button_layout.addWidget(self.control_button)
        button_layout.addWidget(self.folder_button)
        layout.addLayout(button_layout)


        # Create note input section
        note_layout = QHBoxLayout()
        
        # Create note input box
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("Add a note...")
        self.note_input.setFont(QFont("Menlo", 11))
        self.note_input.setStyleSheet("""
            QLineEdit {
                color: black;
                background-color: rgba(255, 255, 255, 180);
                padding: 5px;
                border-radius: 5px;
                border: 1px solid rgba(0, 0, 0, 100);
                height: 20px;
            }
        """)
        self.note_input.returnPressed.connect(self.submit_note)

        # Create add note button
        self.add_note_button = QPushButton("+")
        self.add_note_button.setFont(QFont("Menlo", 11))
        self.add_note_button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: rgba(0, 0, 0, 180);
                padding: 5px;
                border-radius: 5px;
                width: 20px;
                height: 20px;
            }
            QPushButton:hover {
                background-color: rgba(40, 40, 40, 180);
            }
        """)
        self.add_note_button.clicked.connect(self.submit_note)
        
        note_layout.addWidget(self.note_input)
        note_layout.addWidget(self.add_note_button)
        layout.addLayout(note_layout)

        
        self.setLayout(layout)
        
        # Set initial position
        self.move(100, 100)

        print("CursorInfoWidget initialized")
        
        # For dragging window
        self.dragging = False
        self.offset = QPoint()
        self.note_callback = note_callback
    
    def submit_note(self):
        note_text = self.note_input.text().strip()
        if note_text and self.note_callback:
            self.note_callback(note_text)
            self.note_input.clear()
    
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
        
        event_type = cursor_info.get('event_type', '')
        if event_type == 'click':
            button = cursor_info.get('button', '')
            action = 'pressed' if cursor_info.get('pressed') else 'released'
            self.action_label.setText(f"Action: {button} click {action}")
        elif event_type == 'keyboard':
            action = cursor_info.get('action', '')
            self.action_label.setText(f"Action: {action}")
        elif event_type == 'move':
            self.action_label.setText("Action: move")
        elif event_type == 'scroll':
            self.action_label.setText("Action: scroll")

    def open_folder(self):
        if self.screenshots_path and os.path.exists(self.screenshots_path):
            if os.sys.platform == 'darwin':  # macOS
                subprocess.run(['open', self.screenshots_path])
            elif os.sys.platform == 'win32':  # Windows
                subprocess.run(['explorer', self.screenshots_path])
            else:  # Linux
                subprocess.run(['xdg-open', self.screenshots_path])
        
    def toggle_tracking(self):
        self.tracking_enabled = not self.tracking_enabled
        if self.tracking_enabled:
            self.control_button.setText("Stop Tracking")
            if self.tracker_callback:
                self.tracker_callback(True)
        else:
            self.control_button.setText("Resume Tracking")
            if self.tracker_callback:
                self.tracker_callback(False)
    
    def toggle_collapse(self):
        self.is_collapsed = not self.is_collapsed
        
        # Update button text
        self.collapse_button.setText("▶" if self.is_collapsed else "▼")
        
        # Toggle visibility of content
        self.content_widget.setVisible(not self.is_collapsed)
        
        # Adjust window size
        if self.is_collapsed:
            self.setFixedHeight(80)  # Height for just top bar, note input, and buttons
        else:
            self.setFixedHeight(270)  # Full height with all labels
    
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