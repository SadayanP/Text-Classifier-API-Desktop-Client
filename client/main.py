import sys

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


BASE_URL = "http://127.0.0.1:8000"


APP_STYLE = """
QWidget {
    background-color: #f6f8fb;
    color: #1f2937;
    font-family: "Segoe UI";
    font-size: 14px;
}

QLabel#title {
    font-size: 28px;
    font-weight: 700;
    color: #111827;
}

QLabel#subtitle {
    color: #6b7280;
    font-size: 14px;
}

QLabel#section_title {
    font-size: 18px;
    font-weight: 600;
    color: #111827;
}

QLabel#error_label {
    color: #dc2626;
    font-size: 13px;
}

QLabel#result_label {
    font-size: 24px;
    font-weight: 700;
}

QLabel#confidence_label {
    color: #6b7280;
    font-size: 14px;
}

QFrame#card {
    background-color: white;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
}

QLineEdit,
QTextEdit {
    background-color: white;
    border: 1px solid #d1d5db;
    border-radius: 9px;
    padding: 10px 12px;
    color: #111827;
}

QLineEdit:focus,
QTextEdit:focus {
    border: 1px solid #4f46e5;
}

QTextEdit {
    padding: 12px;
}

QPushButton {
    background-color: #e5e7eb;
    border: none;
    border-radius: 9px;
    padding: 11px 18px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #d1d5db;
}

QPushButton:pressed {
    background-color: #cbd5e1;
}

QPushButton:disabled {
    background-color: #e5e7eb;
    color: #9ca3af;
}

QPushButton#primary_button {
    background-color: #4f46e5;
    color: white;
}

QPushButton#primary_button:hover {
    background-color: #4338ca;
}

QPushButton#primary_button:pressed {
    background-color: #3730a3;
}

QPushButton#feedback_correct {
    background-color: #dcfce7;
    color: #166534;
}

QPushButton#feedback_correct:hover {
    background-color: #bbf7d0;
}

QPushButton#feedback_wrong {
    background-color: #fee2e2;
    color: #991b1b;
}

QPushButton#feedback_wrong:hover {
    background-color: #fecaca;
}

QPushButton#logout_button {
    background-color: transparent;
    color: #6b7280;
    padding: 8px 12px;
}

QPushButton#logout_button:hover {
    background-color: #e5e7eb;
    color: #374151;
}
"""


class LoginScreen(QWidget):
    def __init__(self, login_callback):
        super().__init__()

        self.login_callback = login_callback

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(40, 40, 40, 40)
        outer_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        card.setMaximumWidth(420)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(14)

        title = QLabel("Text Classifier")
        title.setObjectName("title")

        subtitle = QLabel("Sign in to classify text and submit feedback.")
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)

        username_label = QLabel("Username")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")

        password_label = QLabel("Password")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.login_button.setObjectName("primary_button")
        self.login_button.setMinimumHeight(44)
        self.login_button.clicked.connect(self.handle_login)

        self.status_label = QLabel()
        self.status_label.setObjectName("error_label")
        self.status_label.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(12)

        layout.addWidget(username_label)
        layout.addWidget(self.username_input)

        layout.addWidget(password_label)
        layout.addWidget(self.password_input)

        layout.addSpacing(8)
        layout.addWidget(self.login_button)
        layout.addWidget(self.status_label)

        outer_layout.addWidget(card)
        self.setLayout(outer_layout)
        
    def reset(self):
        self.username_input.clear()
        self.password_input.clear()
        self.status_label.clear()

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        self.login_button.setEnabled(False)
        self.login_button.setText("Logging in…")
        self.status_label.clear()

        try:
            response = requests.post(
                f"{BASE_URL}/login",
                json={
                    "username": username,
                    "password": password,
                },
                timeout=10,
            )

        except requests.RequestException:
            self.status_label.setText("Cannot connect to server")

        else:
            if response.status_code == 200:
                data = response.json()
                self.login_callback(data["access_token"])
            elif response.status_code == 401:
                self.status_label.setText("Invalid username or password")
            else:
                self.status_label.setText("Login failed")

        finally:
            self.login_button.setEnabled(True)
            self.login_button.setText("Login")


class MainScreen(QWidget):
    def __init__(self, logout_callback, token_getter):
        super().__init__()

        self.logout_callback = logout_callback
        self.token_getter = token_getter
        self.current_prediction_id = None

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(30, 25, 30, 25)
        outer_layout.setSpacing(18)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Text Classifier")
        title.setObjectName("title")

        self.logout_button = QPushButton("Logout")
        self.logout_button.setObjectName("logout_button")
        self.logout_button.clicked.connect(self.logout_callback)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.logout_button)

        outer_layout.addLayout(header_layout)

        # Input card
        input_card = QFrame()
        input_card.setObjectName("card")

        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(20, 20, 20, 20)
        input_layout.setSpacing(12)

        input_title = QLabel("Enter text")
        input_title.setObjectName("section_title")

        input_subtitle = QLabel(
            "Enter a sentence and the model will classify its sentiment."
        )
        input_subtitle.setObjectName("subtitle")

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "Example: I absolutely love this product!"
        )
        self.text_input.setMinimumHeight(150)
        self.text_input.textChanged.connect(self.update_classify_button)

        self.classify_button = QPushButton("Classify")
        self.classify_button.setObjectName("primary_button")
        self.classify_button.setMinimumHeight(44)
        self.classify_button.setEnabled(False)
        self.classify_button.clicked.connect(self.handle_classify)

        input_layout.addWidget(input_title)
        input_layout.addWidget(input_subtitle)
        input_layout.addWidget(self.text_input)
        input_layout.addWidget(self.classify_button)

        outer_layout.addWidget(input_card)

        # Result card
        result_card = QFrame()
        result_card.setObjectName("card")

        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(20, 20, 20, 20)
        result_layout.setSpacing(8)

        result_title = QLabel("Result")
        result_title.setObjectName("section_title")

        self.result_label = QLabel("No classification yet")
        self.result_label.setObjectName("result_label")

        self.confidence_label = QLabel("Confidence: —")
        self.confidence_label.setObjectName("confidence_label")

        result_layout.addWidget(result_title)
        result_layout.addSpacing(4)
        result_layout.addWidget(self.result_label)
        result_layout.addWidget(self.confidence_label)

        outer_layout.addWidget(result_card)

        # Feedback card
        feedback_card = QFrame()
        feedback_card.setObjectName("card")

        feedback_layout = QVBoxLayout(feedback_card)
        feedback_layout.setContentsMargins(20, 20, 20, 20)
        feedback_layout.setSpacing(12)

        feedback_title = QLabel("Was the prediction correct?")
        feedback_title.setObjectName("section_title")

        feedback_buttons = QHBoxLayout()
        feedback_buttons.setSpacing(10)

        self.correct_button = QPushButton("Correct")
        self.correct_button.setObjectName("feedback_correct")
        self.correct_button.setMinimumHeight(42)
        self.correct_button.setEnabled(False)
        self.correct_button.clicked.connect(
            lambda: self.submit_feedback(True)
        )

        self.wrong_button = QPushButton("Wrong")
        self.wrong_button.setObjectName("feedback_wrong")
        self.wrong_button.setMinimumHeight(42)
        self.wrong_button.setEnabled(False)
        self.wrong_button.clicked.connect(
            lambda: self.submit_feedback(False)
        )

        feedback_buttons.addWidget(self.correct_button)
        feedback_buttons.addWidget(self.wrong_button)

        feedback_layout.addWidget(feedback_title)
        feedback_layout.addLayout(feedback_buttons)

        outer_layout.addWidget(feedback_card)

        outer_layout.addStretch()

        self.setLayout(outer_layout)

    def update_classify_button(self):
        has_text = bool(self.text_input.toPlainText().strip())
        self.classify_button.setEnabled(has_text)

    def handle_classify(self):
        text = self.text_input.toPlainText().strip()

        if not text:
            self.classify_button.setEnabled(False)
            return

        self.classify_button.setEnabled(False)
        self.classify_button.setText("Classifying…")

        self.correct_button.setEnabled(False)
        self.wrong_button.setEnabled(False)

        self.current_prediction_id = None

        token = self.token_getter()

        try:
            response = requests.post(
                f"{BASE_URL}/classify",
                headers={
                    "Authorization": f"Bearer {token}",
                },
                json={
                    "text": text,
                },
                timeout=30,
            )

        except requests.RequestException:
            self.show_message("Cannot connect to server")

        else:
            if response.status_code == 200:
                data = response.json()

                self.current_prediction_id = data["prediction_id"]

                self.result_label.setText(
                    f"Result: {data['label']}"
                )

                self.confidence_label.setText(
                    f"Confidence: {data['confidence']:.4f}"
                )

                self.correct_button.setEnabled(True)
                self.wrong_button.setEnabled(True)

            elif response.status_code == 401:
                self.session_expired()

            elif response.status_code == 422:
                self.show_message("Invalid text")

            else:
                self.show_message("Classification failed")

        finally:
            self.classify_button.setText("Classify")
            self.update_classify_button()

    def submit_feedback(self, is_correct):
        if self.current_prediction_id is None:
            return

        self.correct_button.setEnabled(False)
        self.wrong_button.setEnabled(False)

        clicked_button = (
            self.correct_button
            if is_correct
            else self.wrong_button
        )

        clicked_button.setText("Submitting…")

        token = self.token_getter()

        try:
            response = requests.post(
                f"{BASE_URL}/feedback",
                headers={
                    "Authorization": f"Bearer {token}",
                },
                json={
                    "prediction_id": self.current_prediction_id,
                    "is_correct": is_correct,
                },
                timeout=10,
            )

        except requests.RequestException:
            self.show_message("Cannot connect to server")

            self.correct_button.setEnabled(True)
            self.wrong_button.setEnabled(True)

        else:
            if response.status_code == 200:
                self.correct_button.setEnabled(False)
                self.wrong_button.setEnabled(False)

            elif response.status_code == 401:
                self.session_expired()

            elif response.status_code == 404:
                self.show_message("Prediction not found")

                self.correct_button.setEnabled(True)
                self.wrong_button.setEnabled(True)

            else:
                self.show_message("Could not submit feedback")

                self.correct_button.setEnabled(True)
                self.wrong_button.setEnabled(True)

        finally:
            self.correct_button.setText("Correct")
            self.wrong_button.setText("Wrong")

    def session_expired(self):
        self.show_message("Session expired – please log in again")
        self.logout_callback()

    def show_message(self, message):
        QMessageBox.warning(
            self,
            "Text Classifier",
            message,
        )

    def reset(self):
        self.text_input.clear()
        self.current_prediction_id = None

        self.result_label.setText("No classification yet")
        self.confidence_label.setText("Confidence: —")

        self.correct_button.setEnabled(False)
        self.wrong_button.setEnabled(False)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Text Classifier")
        self.resize(720, 700)
        self.setMinimumSize(600, 600)

        self.token = None

        self.stack = QStackedWidget()

        self.login_screen = LoginScreen(
            self.handle_login_success
        )

        self.main_screen = MainScreen(
            self.logout,
            self.get_token,
        )

        self.stack.addWidget(self.login_screen)
        self.stack.addWidget(self.main_screen)

        self.setCentralWidget(self.stack)
        self.stack.setCurrentIndex(0)

    def handle_login_success(self, token):
        self.token = token
        self.main_screen.reset()
        self.stack.setCurrentIndex(1)

    def get_token(self):
        return self.token

    def logout(self):
        self.token = None
        self.login_screen.reset()
        self.main_screen.reset()
        self.stack.setCurrentIndex(0)

    def closeEvent(self, event):
        self.token = None
        event.accept()


def main():
    app = QApplication(sys.argv)

    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLE)

    default_font = QFont("Segoe UI", 10)
    app.setFont(default_font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()