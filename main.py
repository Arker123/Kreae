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
    QSlider,
    QComboBox,
    QToolButton,
)
from PyQt5.QtCore import Qt




import os
from llmware.library import Library
from llmware.retrieval import Query
from llmware.status import Status
from llmware.prompts import Prompt
from llmware.configs import LLMWareConfig, MilvusConfig
from importlib import util

if not util.find_spec("torch") or not util.find_spec("transformers"):
    print("\nto run this code, with the selected embedding model, please install transformers and torch, e.g., "
          "\n`pip install torch`"
          "\n`pip install transformers`")

if not (util.find_spec("chromadb") or util.find_spec("pymilvus") or util.find_spec("lancedb") or util.find_spec("faiss")):
    print("\nto run this code, you will need to pip install the vector db drivers. see comments above.")


class QuantumStrand(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.start_new_chat()
        
    def init_ui(self):

        self.setWindowTitle("<h1 style='font-size: 1pt;'><b><font style='font-family: Arial;'>QuantumStrand</font></b></h1>")
        
        self.setStyleSheet("background-color: white; color: black; font-family: Arial; font-size: 12pt; padding: 10px;")
        self.setGeometry(100, 100, 1000, 800)

        main_layout = QHBoxLayout(self)

        splitter_main = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter_main)

        self.chats_panel = QWidget()
        self.chats_panel_layout = QVBoxLayout()
        self.chats_panel.setLayout(self.chats_panel_layout)

        self.chats_list = QListWidget()
        self.new_chat_button = QPushButton("New Chat")
        self.new_chat_button.clicked.connect(self.start_new_chat)

        try:
            with open("saved_chats.json", "r") as f:
                for line in f:
                    chat = eval(line)
                    existing_chats = [self.chats_list.item(i).text() for i in range(self.chats_list.count())]
                    if chat["chat"] in existing_chats:
                        for i in range(self.chats_list.count()):
                            if self.chats_list.item(i).text() == chat["chat"]:
                                self.chats_list.item(i).setData(Qt.UserRole, chat)
                                break
                    else:
                        chat_item = QListWidgetItem(chat["chat"])
                        chat_item.setData(Qt.UserRole, chat)
                        self.chats_list.addItem(chat_item)
        except FileNotFoundError:
            open("saved_chats.json", "w").close()

        # when a chat is clicked, load the chat history
        self.chats_list.itemClicked.connect(self.load_chat)

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
        self.chat_input.returnPressed.connect(self.send_message)
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        self.chat_panel_layout.addWidget(self.chat_display)
        self.chat_panel_layout.addWidget(self.chat_input)
        self.chat_panel_layout.addWidget(self.send_button)

        # RAG parameters panel
        self.rag_panel = QWidget()
        self.rag_panel_layout = QVBoxLayout()
        self.rag_panel.setLayout(self.rag_panel_layout)
        
        
        self.model_select = QComboBox()
        self.model_select.addItem("RAG-bling-phi-3-gguf")
        self.model_select.currentIndexChanged.connect(self.model_changed)
        self.model_select.setEnabled(False)  # Disable user modification

        self.rag_panel_layout.addWidget(QLabel("Model Select"))
        self.rag_panel_layout.addWidget(self.model_select)
        
        self.temperature_slider = QSlider(Qt.Horizontal)
        self.temperature_slider.setMinimum(0)
        self.temperature_slider.setMaximum(100)
        self.temperature_slider.setValue(0)
        self.temperature_slider.setTickInterval(10)
        self.temperature_slider.setTickPosition(QSlider.TicksBelow)
        self.temperature_slider.valueChanged.connect(self.update_temperature_label)

        self.temperature_label = QLabel()
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.update_temperature_label()
        self.rag_panel_layout.addWidget(QLabel("Temperature"))
        self.rag_panel_layout.addWidget(self.temperature_label)

        self.rag_panel_layout.addWidget(self.temperature_slider)

        self.rag_label = QLabel("<font style='font-family: Arial;'>Instructions</font>")
        self.rag_text_edit = QTextEdit()
        self.rag_text_edit.setPlainText("You are a good assistant")

        

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_rag_text)

        self.rag_panel_layout.addWidget(self.rag_label)
        self.rag_panel_layout.addWidget(self.rag_text_edit)
        self.rag_panel_layout.addWidget(self.save_button)        

        self.gpu_button = QPushButton()
        self.gpu_button.setCheckable(True)
        self.gpu_button.setChecked(False)
        self.gpu_button.setStyleSheet("QPushButton {"
                           "border: none;"
                           "background-color: #ccc;"
                           "width: 50px;"
                           "height: 25px;"
                           "border-radius: 12px;"
                           "}"
                           "QPushButton:checked {"
                           "background-color: #5cb85c;"
                           "}")
        self.gpu_button.setText("GPU: Off")
        self.gpu_button.clicked.connect(self.toggle_gpu)

        self.rag_panel_layout.addWidget(self.gpu_button)

        
        
        self.file_path_label = QLabel("Select Data Folder:")
        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)
        self.file_path_button = QPushButton("Browse")
        self.file_path_button.clicked.connect(self.select_folder_path)

        self.rag_panel_layout.addWidget(self.file_path_label)
        self.rag_panel_layout.addWidget(self.file_path_input)
        self.rag_panel_layout.addWidget(self.file_path_button)

        

        # Add panels to splitters
        splitter_chat_rag.addWidget(self.chat_panel)
        splitter_chat_rag.addWidget(self.rag_panel)

        splitter_main.addWidget(self.chats_panel)
        splitter_main.addWidget(splitter_chat_rag)

        splitter_main.setSizes([200, 800]) 
        splitter_chat_rag.setSizes([500, 300])

    def model_changed(self):
        # To change the model
        pass

    def save_rag_text(self):
        with open("rag_text.txt", "w") as f:
            f.write(self.rag_text_edit.toPlainText())

    def update_temperature_label(self):
        self.temperature_label.setText(str(self.temperature_slider.value() / 100))
        
    def toggle_gpu(self):
        if self.gpu_button.isChecked():
            self.gpu_button.setText("GPU: On")
        else:
            self.gpu_button.setText("GPU: Off")

    def load_chat(self, chat_item):
        self.chat_display.clear()
        with open("saved_chats.json", "r") as f:
            for line in f:
                chat = eval(line)
                if chat["chat"] == chat_item.text():
                    self.chat_display.addItem(QListWidgetItem(chat["user"]))
                    self.chat_display.addItem(QListWidgetItem(chat["bot"]))

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
        response = self.semantic_rag(message)
        print(response)
        return response

    def start_new_chat(self):
        # Clear the chat display and start a new chat
        self.chat_display.clear()
        new_chat_item = QListWidgetItem("Chat " + str(self.chats_list.count() + 1))
        self.chats_list.addItem(new_chat_item)
        self.chats_list.setCurrentItem(new_chat_item)

    def save_chat(self, user_message, bot_response):
        # Save chat history (this function can be expanded to save to a database or file)
        current_chat = self.chats_list.currentItem().text()
        # save user message and bot response to a saved_chats.json file
        with open("saved_chats.json", "a") as f:
            f.write(f'{{"chat": "{current_chat}", "user": "{user_message}", "bot": "{bot_response}"}}\n')

    def select_folder_path(self):
        # Open a file dialog to select a folder
        folder_dialog = QFileDialog(self)
        folder_path = folder_dialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.file_path_input.setText(folder_path)



    def semantic_rag(self, query):

        sample_files_path = self.file_path_input.text()
        if not sample_files_path:
            print("Please select a folder path")
            return

        # Embedding model:- jinaai/jina-embeddings-v2-base-en
        embedding_model_name = "jina-small-en-v2"
        llm_model_name = "bling-phi-3-gguf"
        vector_db = "chromadb"

        lib_name = "sys_llm_win"
        library = Library().create_new_library(lib_name)
        library.add_files(input_folder_path=sample_files_path, chunk_size=400, max_chunk_size=800, smart_chunking=2)
        library.install_new_embedding(embedding_model_name=embedding_model_name, vector_db=vector_db, batch_size=200, use_gpu=False)


        # RAG start here ...
        prompter = Prompt().load_model(llm_model_name, temperature=self.temperature_slider.value() / 100, sample=False, use_gpu=False)
        results = Query(library).semantic_query(query, result_count=80, embedding_distance_threshold=1.0, use_gpu=False)

        for i, contract in enumerate(os.listdir(sample_files_path)):
            qr = []
            if contract != ".DS_Store": # For Mac users
                for j, entries in enumerate(results):
                    library_fn = entries["file_source"]
                    if os.sep in library_fn:
                        # handles difference in windows file formats vs. mac 
                        library_fn = library_fn.split(os.sep)[-1]

                    if library_fn == contract:
                        print("Top Retrieval: ", j, entries["distance"], entries["text"])
                        qr.append(entries)

                source = prompter.add_source_query_results(query_results=qr)

                response = prompter.prompt_with_source(query, prompt_name="default_with_context")

                for resp in response:
                    if "llm_response" in resp:
                        print("\nupdate: llm answer - ", resp["llm_response"])
                prompter.clear_source_materials()

        return response[0]["llm_response"]



def main():
    

    LLMWareConfig().set_active_db("sqlite")

    # select one of:  'milvus' | 'chromadb' | 'lancedb' | 'faiss'
    LLMWareConfig().set_vector_db("chromadb")
    

    app = QApplication(sys.argv)
    quantum_strand = QuantumStrand()
    quantum_strand.show()

    # semantic_rag(sample_files_path="sample_files")

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()