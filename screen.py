import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
    QSplitter,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QFileDialog,
)
from PyQt5.QtCore import Qt

class QuantumStrand(QWidget):
    def __init__(self):
        super().__init__()
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("QuantumStrand")
        self.setGeometry(100, 100, 1000, 600)

        # Create the main layout
        main_layout = QHBoxLayout(self)

        # Splitter for resizing panels
        splitter_main = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter_main)

        # Previous chats panel
        self.chats_panel = QWidget()
        self.chats_panel_layout = QVBoxLayout()
        self.chats_panel.setLayout(self.chats_panel_layout)

        self.chats_list = QListWidget()
        self.new_chat_button = QPushButton("New Chat")
        self.new_chat_button.clicked.connect(self.start_new_chat)

        self.chats_panel_layout.addWidget(QLabel("Chats"))
        self.chats_panel_layout.addWidget(self.chats_list)
        self.chats_panel_layout.addWidget(self.new_chat_button)

        # Chat and RAG panels splitter
        splitter_chat_rag = QSplitter(Qt.Horizontal)

        # Chat panel
        self.chat_panel = QFrame()
        self.chat_panel_layout = QVBoxLayout()
        self.chat_panel.setLayout(self.chat_panel_layout)
        
        self.chat_display = QListWidget()
        self.chat_input = QLineEdit()
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        self.chat_panel_layout.addWidget(self.chat_display)
        self.chat_panel_layout.addWidget(self.chat_input)
        self.chat_panel_layout.addWidget(self.send_button)

        # RAG parameters panel
        self.rag_panel = QWidget()
        self.rag_panel_layout = QVBoxLayout()
        self.rag_panel.setLayout(self.rag_panel_layout)
        
        self.rag_label = QLabel("RAG Parameters")
        self.rag_text_edit = QTextEdit()
        
        self.file_path_label = QLabel("Select File:")
        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)
        self.file_path_button = QPushButton("Browse")
        self.file_path_button.clicked.connect(self.select_folder_path)

        self.rag_panel_layout.addWidget(self.rag_label)
        self.rag_panel_layout.addWidget(self.rag_text_edit)
        self.rag_panel_layout.addWidget(self.file_path_label)
        self.rag_panel_layout.addWidget(self.file_path_input)
        self.rag_panel_layout.addWidget(self.file_path_button)

        # Add panels to splitters
        splitter_chat_rag.addWidget(self.chat_panel)
        splitter_chat_rag.addWidget(self.rag_panel)

        splitter_main.addWidget(self.chats_panel)
        splitter_main.addWidget(splitter_chat_rag)

        splitter_main.setSizes([200, 800])  # Initial sizes for the main panels
        splitter_chat_rag.setSizes([500, 300])  # Initial sizes for chat and RAG panels

    def send_message(self):
        message = self.chat_input.text()
        if message:
            item = QListWidgetItem("User: " + message)
            self.chat_display.addItem(item)
            self.chat_input.clear()
            # Here you would typically call your model to generate a response
            response = self.generate_response(message)
            self.chat_display.addItem(QListWidgetItem("QuantumStrand: " + response))
            self.save_chat("User: " + message, "QuantumStrand: " + response)

    def generate_response(self, message):
        # Placeholder for model interaction
        return "This is a response to: " + message

    def start_new_chat(self):
        # Clear the chat display and start a new chat
        self.chat_display.clear()
        new_chat_item = QListWidgetItem("Chat " + str(self.chats_list.count() + 1))
        self.chats_list.addItem(new_chat_item)
        self.chats_list.setCurrentItem(new_chat_item)

    def save_chat(self, user_message, bot_response):
        # Save chat history (this function can be expanded to save to a database or file)
        current_chat = self.chats_list.currentItem()
        if current_chat:
            current_chat.setText(current_chat.text() + "\n" + user_message + "\n" + bot_response)

    def select_folder_path(self):
        # Open a file dialog to select a folder
        folder_dialog = QFileDialog(self)
        folder_path = folder_dialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.file_path_input.setText(folder_path)

def main():
    app = QApplication(sys.argv)
    quantum_strand = QuantumStrand()
    quantum_strand.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
