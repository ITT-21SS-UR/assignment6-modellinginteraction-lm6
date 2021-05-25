import sys
import os
import time
import math
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import QPushButton

import pandas as pd


class CalculatorLogger:

    def __init__(self, logfile):
        self.__log_file_name = logfile
        self.__calculator_data = self.__init_study_data()

    def __init_study_data(self):
        # check if the file already exists
        if os.path.isfile(self.__log_file_name):
            calculator_data = pd.read_csv(self.__log_file_name)
        else:
            calculator_data = pd.DataFrame(
                columns=['timeStamp', 'eventType', 'isMouse', 'klmId', 'button'])
        return calculator_data

    def add_new_log_data(self, time_stamp, event_type, is_mouse, klm_id, button):
        log_data = {'timeStamp': time_stamp, 'eventType': event_type, 'isMouse': is_mouse, 'klmId': klm_id, 'button': button}
        print(log_data)
        self.__calculator_data = self.__calculator_data.append(log_data, ignore_index=True)
        self.__calculator_data.to_csv(self.__log_file_name, index=False)
        with open(self.__log_file_name) as file:
            print(file.readlines()[-1])


# decorator for logging all inputs
def input_logging_decorator(function):
    def wrapper(*args, **kwargs):
        print('New input via {}: {}'.format(function.__name__, args[1]))
        return function(*args, **kwargs)

    return wrapper


class IttCalculator(QtWidgets.QWidget):
    def __init__(self, logfile=None):
        super().__init__()
        self.__ui = uic.loadUi("calculator.ui", self)
        self.__equation_text = ""
        self.__equation_label = self.__ui.EquationLabel
        self.__result_text = ""
        self.__result_label = self.__ui.ResultLabel
        self.__allowed_numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        self.__allowed_operators = ["/", "*", "+", "-"]
        self._setup_keys()
        self._logfile_name = logfile if logfile is not None else "calculatorLog.csv"
        self._calculatorLogger = CalculatorLogger(logfile)
        self._mouse_move_path = []
        self.show()

    # add a new input to our equation and equation-label
    def __add_to_equation(self, new_input):
        self.__equation_text += new_input
        self.__equation_label.setText(self.__equation_text)

    # execute an input command
    def __execute_command(self, command):
        if command == "=":
            self.__result_text = self.__calculate_result()
            self.__result_label.setText(self.__result_text)
        elif command == "DEL":
            self.__equation_text = ""
            self.__equation_label.setText(self.__equation_text)
        elif command == "Clear":
            self.__equation_text = self.__equation_text[:-1]
            self.__equation_label.setText(self.__equation_text)

    # calculates and returns the result of the equation by using the eval() function,
    # returns "Err" string if the equation cant be solved
    def __calculate_result(self):

        try:
            result = str(eval(self.__equation_text))
            return result
        except:
            return "Err"

    # sends a new keyboard "command" input (enter, clear or backspace) to the log (through the decorator)
    # and to the executes_command() function
    @input_logging_decorator
    def __keyboard_input_command(self, new_input):
        self._calculatorLogger.add_new_log_data(time.time(), "keyStroke", False, 'k', new_input)
        self.__execute_command(new_input)

    # sends a new mouse "command" input (enter, clear or backspace) to the log (through the decorator)
    # and to the execute_command() function
    @input_logging_decorator
    def __mouse_input_command(self, button):
        self._calculatorLogger.add_new_log_data(time.time(), "mouseClick", True, 'B', button)
        self.__execute_command(button)

    # sends a new keyboard "number or operator" input to the log (through the decorator)
    # and to the add_to_equation() function
    @input_logging_decorator
    def __keyboard_input_number_or_operator(self, new_input):
        self._calculatorLogger.add_new_log_data(time.time(), "keyStroke", False, 'k', new_input)
        self.__add_to_equation(new_input)

    # sends a new mouse "number or operator" input to the log (through the decorator)
    # and to the add_to_equation() function
    @input_logging_decorator
    def __mouse_input_number_or_operator(self, button):
        self._calculatorLogger.add_new_log_data(time.time(), "mouseClick", True, 'B', button)
        self.__add_to_equation(button)

    def _setup_keys(self) -> None:
        self.__DIGIT_KEYS = [self.__ui.NumButton_0, self.__ui.NumButton_1,
                             self.__ui.NumButton_2, self.__ui.NumButton_3,
                             self.__ui.NumButton_4, self.__ui.NumButton_5,
                             self.__ui.NumButton_6, self.__ui.NumButton_7,
                             self.__ui.NumButton_8, self.__ui.NumButton_9]

        self.__OPERATOR_KEYS = [self.__ui.NumButton_Multiply, self.__ui.NumButton_Divide,
                                self.__ui.NumButton_Add, self.__ui.NumButton_Subtract,
                                self.__ui.NumButton_DecPoint]

        self.__KEYBOARD_KEYS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "+", "-", "*", "/"]

        # don't let user edit input field directly for now
        self._setup_listeners()

    def _setup_listeners(self) -> None:
        for button in self.__DIGIT_KEYS + self.__OPERATOR_KEYS:
            # lambda taken from
            # https://stackoverflow.com/questions/18836291/lambda-function-returning-false#comment45916219_18862798
            button.clicked.connect(
                lambda ignore, x=button.text(): self.__mouse_input_number_or_operator(x)
            )
            button.installEventFilter(self)

        self.__ui.NumButton_Enter.clicked.connect(lambda: self.__mouse_input_command("="))
        self.__ui.NumButton_Enter.installEventFilter(self)
        self.__ui.NumButton_Clear.clicked.connect(lambda: self.__mouse_input_command("DEL"))
        self.__ui.NumButton_Clear.installEventFilter(self)
        self.__ui.NumButton_Delete.clicked.connect(lambda: self.__mouse_input_command("Clear"))
        self.__ui.NumButton_Delete.installEventFilter(self)

    # EventFilter to log mouse movement over buttons
    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.HoverEnter:
            if self._mouse_move_path[-1:] != source:
                # We use "Px" here because its not the whole pointing even "P", but just a part of it
                self._calculatorLogger.add_new_log_data(time.time(), "mouseMove", True, "Px", source.text())
        return False



    # registers all relevant key press events
    def keyPressEvent(self, event):
        if event.text() in self.__allowed_numbers:
            self.__keyboard_input_number_or_operator(event.text())
        elif event.text() in self.__allowed_operators:
            self.__keyboard_input_number_or_operator(event.text())
        elif event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self.__keyboard_input_command("=")
        elif event.key() == QtCore.Qt.Key_Backspace:
            self.__keyboard_input_command("Clear")
        elif event.text() == "." or event.text() == ",":
            self.__keyboard_input_number_or_operator(".")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    logfile_name = sys.argv[1]
    calculator = IttCalculator(logfile_name)
    sys.exit(app.exec_())
