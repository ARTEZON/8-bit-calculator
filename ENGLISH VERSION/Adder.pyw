import os
import sys

from PySide6.QtWidgets import * # QApplication, QWidget, and others
from PySide6.QtCore import QFile, QCoreApplication, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap, QIcon, QFontDatabase


class Panel:
    def __init__(self):
        for addend in ('A', 'B'):
            for n in range(1, 9):
                setattr(self, f'switch_{addend}_{n}', False)
        self.input_A_decimal = 0
        self.input_A_binary = '0' * 8
        self.input_B_decimal = 0
        self.input_B_binary = '0' * 8
        self.sum_decimal = 0
        self.sum_binary = '0' * 8
        for n in range(1, 9):
            setattr(self, f'adder_{n}', Adder())
        for n in range(1, 9):
            setattr(self, f'bulb_{n}', False)
        self.info_string = 'Value range in unsigned mode: from 0 to 255'


class Settings:
    # modes:
    # 0 = unsigned
    # 1 = signed
    def __init__(self):
        #default
        self.mode = 0
        self.lang = 'en'
        self.theme = 'light'
    
    #def load_settings()

    def change_mode(self):
        if self.mode == 0:
            self.mode = 1
            main_window.btn_mode.setText("Mode: signed")
            panel.info_string = 'Value range in signed mode: from -128 to 127'
            main_window.info_label.setText(panel.info_string)

        elif self.mode == 1:
            self.mode = 0
            main_window.btn_mode.setText("Mode: unsigned")
            panel.info_string = 'Value range in unsigned mode: from 0 to 255'
            main_window.info_label.setText(panel.info_string)

        main_window.input_A_decimal.setValue(0)
        main_window.input_B_decimal.setValue(0)


class Adder:
    def __init__(self):
        self.A = False
        self.B = False
        self.CI = False
        self.S = False
        self.CO = False
    
    def xor(self, a, b):
        return (a or b) and (not(a and b))

    def half_adder(self, A, B):
        s = self.xor(A, B)
        c = A and B
        return (s, c)
    
    def adder(self, A, B, CI):
        ha1 = self.half_adder(A, B)
        ha2 = self.half_adder(CI, ha1[0])
        s = ha2[0]
        c = ha1[1] or ha2[1]
        return (s, c)


class Convert:
    def from_2_to_10(binary_string, mode):
        binary_string = str(binary_string)
        for d in binary_string:
            if d != '0' and d != '1':
                return None
        while len(binary_string) % 8 != 0:
            binary_string = '0' + binary_string
        digits = len(binary_string)

        decimal = 0
        digit = 0
        negative = (mode == 1 and binary_string[0] == '1')
        while(binary_string):
            if binary_string[-1] == '1':
                decimal += 2**digit
            binary_string = binary_string[:-1]
            digit += 1
        
        if negative:
            decimal -= 2**digits
        
        return decimal
    
    def from_10_to_2(integer, mode):
        try:
            integer = int(integer)
        except:
            return None
        negative = (integer < 0)
        integer = abs(integer)
        if mode == 0 and negative:
            return None
        
        binary = ''
        temp = integer
        while temp >= 2:
            binary = str(temp % 2) + binary
            temp //= 2
        binary = str(temp) + binary

        while len(binary) % 8 != 0:
            binary = '0' + binary
        digits = len(binary)
        if mode == 1 and not((-1 * 2**(digits - 1)) <= integer * (-1)**negative <= (2**(digits - 1) - 1)):
            binary = '0' + binary
            while len(binary) % 8 != 0:
                binary = '0' + binary
            digits = len(binary)

        if negative:
            binary = list(binary)
            binary[0] = '1'
            for i in range(1, digits):
                if binary[i] == '0': binary[i] = '1'
                else: binary[i] = '0'
            
            carry = 0
            for i in range(digits - 1, 0, -1):
                temp = int(binary[i]) + int(i == digits - 1) + carry
                carry = temp // 2
                temp = temp % 2
                binary[i] = str(temp)
            binary = ''.join(binary)
        
        return binary


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        load_ui(self, 'forms/main.ui')

        self.setWindowTitle('8-bit Adder Simulator by ARTEZON')
        self.setWindowIcon(QIcon('res/logo.png'))
        self.setFixedSize(780, 600)

        for addend in ('A', 'B'):
            for n in range(1, 9):
                setattr(self, f'switch_{addend}_{n}', self.findChild(QCheckBox, eval(f'\'switch_{addend}_{n}\'')))
        self.input_A_decimal = self.findChild(QSpinBox, "input_A_decimal")
        self.input_A_binary = self.findChild(QLabel, "input_A_binary")
        self.input_B_decimal = self.findChild(QSpinBox, "input_B_decimal")
        self.input_B_binary = self.findChild(QLabel, "input_B_binary")
        self.sum_decimal = self.findChild(QLCDNumber, "sum_decimal")
        self.sum_binary = self.findChild(QLabel, "sum_binary")
        for n in range(1, 9):
            setattr(self, f'adder_{n}', self.findChild(QWidget, eval(f'\'adder_{n}\'')))
            setattr(self, f'connect_A_{n}', self.findChild(QWidget, eval(f'\'connect_A_{n}\'')))
            setattr(self, f'connect_B_{n}', self.findChild(QWidget, eval(f'\'connect_B_{n}\'')))
            setattr(self, f'connect_CI_{n}', self.findChild(QWidget, eval(f'\'connect_CI_{n}\'')))
            setattr(self, f'connect_CO_{n}', self.findChild(QWidget, eval(f'\'connect_CO_{n}\'')))
            setattr(self, f'connect_S_{n}', self.findChild(QWidget, eval(f'\'connect_S_{n}\'')))
            setattr(self, f'wire_A_{n}', self.findChild(QWidget, eval(f'\'wire_A_{n}\'')))
            setattr(self, f'wire_B_{n}', self.findChild(QWidget, eval(f'\'wire_B_{n}\'')))
            setattr(self, f'wire_S_{n}', self.findChild(QWidget, eval(f'\'wire_S_{n}\'')))
            if n != 1: setattr(self, f'wire_carry_{n}', self.findChild(QWidget, eval(f'\'wire_carry_{n}\'')))

        for n in range(1, 9):
            setattr(self, f'bulb_{n}', self.findChild(QFrame, eval(f'\'bulb_{n}\'')))
        self.info_label = self.findChild(QLabel, "info_label")
        self.btn_mode = self.findChild(QPushButton, "btn_mode")
        self.btn_theme = self.findChild(QPushButton, "btn_theme")
        self.btn_lang = self.findChild(QPushButton, "btn_lang")
        self.btn_about = self.findChild(QPushButton, "btn_about")

        self.info_label.setText(panel.info_string)

        self.connect_signals()
        self.btn_mode.clicked.connect(settings.change_mode)
        # self.btn_theme.clicked.connect()
        # self.btn_lang.clicked.connect()
        self.btn_about.clicked.connect(open_about_window)
    
    def switch_updated(self, setting=None):
        self.disconnect_signals()
        update_state(trigger='switch')
        self.connect_signals()
    
    def decimal_input_field_updated(self, setting=None):
        self.disconnect_signals()
        update_state(trigger='decimal_input_field')
        self.connect_signals()
    
    def connect_signals(self):
        for addend in ('A', 'B'):
            for n in range(1, 9):
                getattr(self, f'switch_{addend}_{n}').stateChanged.connect(self.switch_updated)
        self.input_A_decimal.valueChanged.connect(self.decimal_input_field_updated)
        self.input_B_decimal.valueChanged.connect(self.decimal_input_field_updated)


    def disconnect_signals(self):
        for addend in ('A', 'B'):
            for n in range(1, 9):
                getattr(self, f'switch_{addend}_{n}').stateChanged.disconnect()
        self.input_A_decimal.valueChanged.disconnect()
        self.input_B_decimal.valueChanged.disconnect()


def update_state(trigger):
    if trigger == 'switch':
        for addend in ('A', 'B'):
            for n in range(1, 9):
                setattr(panel, f'switch_{addend}_{n}', getattr(main_window, f'switch_{addend}_{n}').isChecked())
        
        panel.input_A_binary = ''.join(map(str, map(int, [getattr(panel, f'switch_A_{n}') for n in range(8, 0, -1)])))
        panel.input_A_decimal = Convert.from_2_to_10(panel.input_A_binary, settings.mode)
        panel.input_B_binary = ''.join(map(str, map(int, [getattr(panel, f'switch_B_{n}') for n in range(8, 0, -1)])))
        panel.input_B_decimal = Convert.from_2_to_10(panel.input_B_binary, settings.mode)
        
    
    elif trigger == 'decimal_input_field':
        if (settings.mode == 0 and not(0 <= main_window.input_A_decimal.value() <= 255)) or (settings.mode == 1 and not(-128 <= main_window.input_A_decimal.value() <= 127)):
            main_window.input_A_decimal.setValue(panel.input_A_decimal)
            return
        if (settings.mode == 0 and not(0 <= main_window.input_B_decimal.value() <= 255)) or (settings.mode == 1 and not(-128 <= main_window.input_B_decimal.value() <= 127)):
            main_window.input_B_decimal.setValue(panel.input_B_decimal)
            return

        panel.input_A_decimal = main_window.input_A_decimal.value()
        panel.input_A_binary = Convert.from_10_to_2(panel.input_A_decimal, settings.mode)
        panel.input_B_decimal = main_window.input_B_decimal.value()
        panel.input_B_binary = Convert.from_10_to_2(panel.input_B_decimal, settings.mode)

        for addend in ('A', 'B'):
            for n in range(1, 9):
                setattr(panel, f'switch_{addend}_{n}', bool(int(getattr(panel, f'input_{addend}_binary')[-1 - n + 1])))
    #endif

    for addend in ('A', 'B'):
        for n in range(1, 9):
            getattr(panel, f'adder_{n}').A = getattr(panel, f'switch_A_{n}')
            getattr(panel, f'adder_{n}').B = getattr(panel, f'switch_B_{n}')
            if n == 1: getattr(panel, f'adder_{n}').CI = False
            else: getattr(panel, f'adder_{n}').CI = getattr(panel, f'adder_{n - 1}').CO
            exec(f'panel.adder_{n}.S, panel.adder_{n}.CO = panel.adder_{n}.adder(panel.adder_{n}.A, panel.adder_{n}.B, panel.adder_{n}.CI)')
    
    for n in range(1, 9):
        setattr(panel, f'bulb_{n}', getattr(panel, f'adder_{n}').S)

    panel.sum_binary = ''.join(map(str, map(int, [getattr(panel, f'bulb_{n}') for n in range(8, 0, -1)])))
    panel.sum_decimal = Convert.from_2_to_10(panel.sum_binary, settings.mode)

    if (settings.mode == 0 and not(0 <= panel.input_A_decimal + panel.input_B_decimal <= 255)) or (settings.mode == 1 and not(-128 <= panel.input_A_decimal + panel.input_B_decimal <= 127)):
        main_window.info_label.setText('ERROR: Integer overflow.')
        main_window.info_label.setStyleSheet('color: rgb(255, 0, 0);')
        main_window.sum_decimal.setStyleSheet('color: rgb(255, 0, 0);')
    else:
        main_window.info_label.setText(panel.info_string)
        main_window.info_label.setStyleSheet('color: rgb(0, 0, 0);')
        main_window.sum_decimal.setStyleSheet('color: rgb(0, 0, 0);')

    for addend in ('A', 'B'):
        for n in range(1, 9):
            getattr(main_window, f'switch_{addend}_{n}').setChecked(getattr(panel, f'switch_{addend}_{n}'))
    
    main_window.input_A_decimal.setValue(panel.input_A_decimal)
    main_window.input_A_binary.setText(panel.input_A_binary)
    main_window.input_B_decimal.setValue(panel.input_B_decimal)
    main_window.input_B_binary.setText(panel.input_B_binary)
    main_window.sum_decimal.display(panel.sum_decimal)
    main_window.sum_binary.setText(panel.sum_binary)

    for n in range(1, 9):
        # label_text = f'<p style="font-size:8pt;">Сумматор {n}<br/>CI: {getattr(panel, f"adder_{n}").CI}<br/>A: {getattr(panel, f"adder_{n}").A}<br/>B: {getattr(panel, f"adder_{n}").B}<br/>S: {getattr(panel, f"adder_{n}").S}<br/>CO: {getattr(panel, f"adder_{n}").CO}</p>'
        # getattr(main_window, f'adder_{n}').setText(label_text)
        color_ON = '#00aa00'
        color_OFF = '#8d8e8e'
        if getattr(panel, f'adder_{n}').A:
            color_A = color_ON
            wire_A = QPixmap("res/a_on.png")
            bool_A = 1
        else:
            color_A = color_OFF
            wire_A = QPixmap("res/a.png")
            bool_A = 0
        if getattr(panel, f'adder_{n}').B:
            color_B = color_ON
            wire_B = QPixmap("res/b_on.png")
            bool_B = 1
        else:
            color_B = color_OFF
            wire_B = QPixmap("res/b.png")
            bool_B = 0
        if getattr(panel, f'adder_{n}').CI:
            color_CI = color_ON
            wire_carry = QPixmap("res/carry_on.png")
            bool_CI = 1
        else:
            color_CI = color_OFF
            wire_carry = QPixmap("res/carry.png")
            bool_CI = 0
        if getattr(panel, f'adder_{n}').CO:
            color_CO = color_ON
            bool_CO = 1
        else:
            color_CO = color_OFF
            bool_CO = 0
        if getattr(panel, f'adder_{n}').S:
            color_S = color_ON
            wire_S = QPixmap("res/s_on.png")
            bool_S = 1
        else:
            color_S = color_OFF
            wire_S = QPixmap("res/s.png")
            bool_S = 0
        getattr(main_window, f'connect_A_{n}').setText(f'A<br><span style=" color:{color_A};">{bool_A}</span>')
        getattr(main_window, f'connect_B_{n}').setText(f'B<br><span style=" color:{color_B};">{bool_B}</span>')
        getattr(main_window, f'connect_CI_{n}').setText(f'CI<br><span style=" color:{color_CI};">{bool_CI}</span>')
        getattr(main_window, f'connect_CO_{n}').setText(f'<span style=" color:{color_CO};">{bool_CO}</span><br>CO')
        if n == 8:
            if panel.adder_8.CO: main_window.connect_CO_8.setText(f'<span style=" color:{color_CO};">{bool_CO}</span><br><span style=" color:#aa0000;">CO</span>')
            else: main_window.connect_CO_8.setText(f'<span style=" color:{color_CO};">{bool_CO}</span><br>CO')
        getattr(main_window, f'connect_S_{n}').setText(f'<span style=" color:{color_S};">{bool_S}</span><br>S')
        getattr(main_window, f'wire_A_{n}').setPixmap(wire_A)
        getattr(main_window, f'wire_B_{n}').setPixmap(wire_B)
        getattr(main_window, f'wire_S_{n}').setPixmap(wire_S)
        if n != 1: getattr(main_window, f'wire_carry_{n}').setPixmap(wire_carry)

    for n in range(1, 9):
        if (getattr(panel, f'bulb_{n}')):
            colorRGB = (0, 170, 0)
            style = r'QFrame {image: url("res/bulb_on.png");}'
        else:
            colorRGB = (170, 0, 0)
            style = r'QFrame {image: url("res/bulb_off.png");}'
        getattr(main_window, f'bulb_{n}').setStyleSheet(style)


class AboutWindow(QDialog):
    def __init__(self):
        super().__init__()
        load_ui(self, 'forms/about.ui')

        self.setWindowTitle('О программе')
        self.setWindowIcon(QIcon('res/logo.png'))
        self.setFixedSize(615, 320)
        self.setWindowModality(Qt.ApplicationModal)

        self.close_button = self.findChild(QPushButton, "close_button")
        self.close_button.clicked.connect(close_about_window)


def open_about_window():
    about_window.show()


def close_about_window():
    about_window.close()


def load_ui(parent, path):
    loader = QUiLoader()
    ui_file = QFile(path)
    ui_file.open(QFile.ReadOnly)
    loader.load(ui_file, parent)
    ui_file.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setAttribute(Qt.AA_EnableHighDpiScaling)
    settings = Settings()
    panel = Panel()
    QFontDatabase.addApplicationFont("res/Rubik-Black.ttf")
    QFontDatabase.addApplicationFont("res/Rubik-Bold.ttf")
    QFontDatabase.addApplicationFont("res/Rubik-ExtraBold.ttf")
    QFontDatabase.addApplicationFont("res/Rubik-Medium.ttf")
    QFontDatabase.addApplicationFont("res/Rubik-Regular.ttf")
    QFontDatabase.addApplicationFont("res/Rubik-SemiBold.ttf")
    QFontDatabase.addApplicationFont("res/DroidSansMono.ttf")
    QFontDatabase.addApplicationFont("res/Montserrat-Bold.otf")
    QFontDatabase.addApplicationFont("res/Montserrat-Medium.otf")
    QFontDatabase.addApplicationFont("res/Montserrat-Regular.otf")
    QFontDatabase.addApplicationFont("res/Montserrat-SemiBold.otf")
    main_window = MainWindow()
    about_window = AboutWindow()
    main_window.show()
    sys.exit(app.exec())
