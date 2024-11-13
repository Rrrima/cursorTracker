from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit
from PyQt6.QtGui import QFont

class NoteViewer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Notes you took")
        self.setMinimumSize(300, 100)

        # Create layout
        layout = QVBoxLayout()

        # Create scrollable text area
        self.notes_area = QTextEdit()
        self.notes_area.setReadOnly(True)
        self.notes_area.setFont(QFont("Menlo", 11))
        self.notes_area.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 180);
                border-radius: 5px;
                border: 1px solid rgba(0, 0, 0, 100);
                padding: 5px;
            }
        """)
        
        layout.addWidget(self.notes_area)
        self.setLayout(layout)

    def set_notes(self, notes_data):
        formatted_notes = []
        for note in notes_data:
            # timestamp = note.get('timestamp', 'Unknown')
            try:
                from datetime import datetime
                timestamp = datetime.strptime(note.get('timestamp', ''), '%m%d_%H%M%S').strftime('%H:%M')
            except:
                timestamp = 'Unknown'
            note_text = note.get('note', '')
            formatted_notes.append(f"[{timestamp}]\n {note_text}\n")
        
        self.notes_area.setText('\n'.join(formatted_notes))