import sys
import subprocess
import unicodedata
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QLineEdit, QPushButton, QWidget, QScrollArea, QFrame, QMessageBox, QDialog
)
from PyQt5.QtGui import QFont, QGuiApplication, QPixmap
from PyQt5.QtCore import Qt
import qrcode
from PIL import Image

def limpiar_nombre_red(nombre):
    """Normaliza el nombre de la red eliminando caracteres no ASCII."""
    return ''.join(c for c in unicodedata.normalize('NFKD', nombre) if ord(c) < 128)


class QRWindow(QDialog):
    """Ventana flotante para mostrar el código QR."""
    def __init__(self, qr_img_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Código QR de la Red")
        self.setGeometry(300, 300, 300, 300)
        self.setStyleSheet("background-color: #121212; color: #ffffff;")

        layout = QVBoxLayout(self)

        # Mostrar el código QR
        qr_label = QLabel(self)
        pixmap = QPixmap(qr_img_path)
        qr_label.setPixmap(pixmap)
        qr_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(qr_label)

        # Botón para cerrar la ventana
        close_button = QPushButton("Cerrar", self)
        close_button.setStyleSheet(
            "background-color: #333333; color: #ffcc00; font-size: 14px; padding: 10px 15px; "
            "border-radius: 5px; border: 1px solid #555555;"
        )
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)


class WifiApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Información de Redes y Contraseñas")
        self.setGeometry(200, 100, 900, 700)
        self.setStyleSheet("background-color: #121212; color: #ffffff;")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        title_label = QLabel("Información de Redes y Contraseñas")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #ff6f61; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        instructions = QLabel(
            "Instrucciones:\n"
            "- 'Mostrar Redes' para listar redes disponibles.\n"
            "- Ingresa el nombre de una red y 'Mostrar Contraseña'.\n"
            "- Usa 'Copiar Contraseña' para copiar.\n"
            "- 'Exportar Datos' guarda en un archivo.\n"
            "- Botón 'Limpiar' borra todo el contenido.\n"
            "- 'Generar QR' para crear un código QR de la red seleccionada.\n"
        )
        instructions.setFont(QFont("Arial", 12))
        instructions.setStyleSheet("color: #b0b0b0; margin: 5px;")
        main_layout.addWidget(instructions)

        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        self.redes_texto = self.crear_area_texto()
        content_layout.addWidget(self.crear_scroll_area(self.redes_texto))

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #444444;")
        content_layout.addWidget(separator)

        self.contrasena_texto = self.crear_area_texto()
        content_layout.addWidget(self.crear_scroll_area(self.contrasena_texto))

        input_layout = QHBoxLayout()
        main_layout.addLayout(input_layout)

        self.red_input = QLineEdit()
        self.red_input.setPlaceholderText("Nombre de la red")
        self.red_input.setFont(QFont("Arial", 12))
        self.red_input.setStyleSheet("padding: 5px; background-color: #1e1e1e; color: #ffffff;")
        input_layout.addWidget(self.red_input)

        botones = [
            ("Mostrar Redes", self.mostrar_redes),
            ("Mostrar Contraseña", self.mostrar_contrasena),
            ("Copiar Contraseña", self.copiar_contrasena),
            ("Exportar Datos", self.exportar_datos),
            ("Limpiar", self.limpiar_texto),
            ("Generar QR", self.generar_qr),
        ]
        for texto, funcion in botones:
            input_layout.addWidget(self.crear_boton(texto, funcion))

    def crear_area_texto(self):
        text_edit = QTextEdit(readOnly=True)
        text_edit.setFont(QFont("Courier", 10))
        text_edit.setStyleSheet("background-color: #1e1e1e; color: #76ff76; padding: 10px; border: none;")
        return text_edit

    def crear_scroll_area(self, widget):
        scroll_area = QScrollArea(widgetResizable=True)
        scroll_area.setWidget(widget)
        scroll_area.setStyleSheet("background-color: #1e1e1e; border: none;")
        return scroll_area

    def crear_boton(self, texto, funcion):
        btn = QPushButton(texto)
        btn.clicked.connect(funcion)
        btn.setStyleSheet(
            "background-color: #333333; color: #ffcc00; font-size: 14px; padding: 10px 15px; "
            "border-radius: 5px; border: 1px solid #555555;"
        )
        return btn

    def ejecutar_comando(self, comando):
        try:
            return subprocess.check_output(comando, shell=True, text=True, errors='ignore')
        except subprocess.CalledProcessError as e:
            return str(e)

    def mostrar_redes(self):
        resultado = self.ejecutar_comando("netsh wlan show profile")
        self.redes_texto.setText(f"Redes disponibles:\n{resultado}")

    def mostrar_contrasena(self):
        clave = self.red_input.text().strip()
        if not clave:
            self.contrasena_texto.setText("Debe ingresar el nombre de la red.")
            return
        clave_limpia = limpiar_nombre_red(clave)
        resultado = self.ejecutar_comando(f'netsh wlan show profile name="{clave_limpia}" key=clear')
        mensaje = f"Información para la red '{clave}':\n{resultado}" if "Perfil de" in resultado else f"No se encontró el perfil para '{clave}'."
        self.contrasena_texto.setText(mensaje)

    def copiar_contrasena(self):
        texto = self.contrasena_texto.toPlainText()
        if texto.strip():
            QGuiApplication.clipboard().setText(texto)
            QMessageBox.information(self, "Copiar Contraseña", "La información se ha copiado al portapapeles.")
        else:
            QMessageBox.warning(self, "Copiar Contraseña", "No hay información para copiar.")

    def exportar_datos(self):
        try:
            with open("wifi_info.txt", "w", encoding="utf-8") as archivo:
                archivo.write("Redes disponibles:\n")
                archivo.write(self.redes_texto.toPlainText())
                archivo.write("\n\nInformación de la red seleccionada:\n")
                archivo.write(self.contrasena_texto.toPlainText())
            QMessageBox.information(self, "Exportar Datos", "La información se ha exportado a 'wifi_info.txt'.")
        except Exception as e:
            QMessageBox.critical(self, "Exportar Datos", f"Error al exportar datos: {str(e)}")

    def limpiar_texto(self):
        self.redes_texto.clear()
        self.contrasena_texto.clear()

    def generar_qr(self):
        clave = self.red_input.text().strip()
        if not clave:
            QMessageBox.warning(self, "Generar QR", "Debe ingresar el nombre de la red.")
            return

        clave_limpia = limpiar_nombre_red(clave)
        resultado = self.ejecutar_comando(f'netsh wlan show profile name="{clave_limpia}" key=clear')

        if "Perfil de" not in resultado:
            QMessageBox.warning(self, "Generar QR", f"No se encontró el perfil para '{clave}'.")
            return

        # Extraer la contraseña de la red
        for linea in resultado.splitlines():
            if "Contenido de la clave" in linea:
                contrasena = linea.split(":")[1].strip()
                break
        else:
            QMessageBox.warning(self, "Generar QR", "No se pudo encontrar la contraseña de la red.")
            return

        # Crear el texto para el código QR
        qr_text = f"WIFI:S:{clave_limpia};T:WPA;P:{contrasena};;"

        # Generar el código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        qr_img_path = "wifi_qr.png"
        img.save(qr_img_path)

        # Mostrar el código QR en una ventana flotante
        self.qr_window = QRWindow(qr_img_path, self)
        self.qr_window.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = WifiApp()
    ventana.show()
    sys.exit(app.exec_())
