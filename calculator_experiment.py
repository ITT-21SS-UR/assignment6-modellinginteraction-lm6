"""
This script was written by Johannes Lorper
"""

import sys
import os
import time
from PyQt5 import QtWidgets, QtCore, uic
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
                columns=['timeStamp', 'eventType', 'isMouse', 'klmId', 'argument'])
        return calculator_data

    def set_logfile_name(self, new_logfile_name):
        self.__log_file_name = new_logfile_name
        self.__calculator_data = self.__init_study_data()

    def add_new_log_data(self, time_stamp, event_type, is_mouse, klm_id, argument):
        log_data = {'timeStamp': time_stamp, 'eventType': event_type, 'isMouse': is_mouse, 'klmId': klm_id,
                    'argument': argument}
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
    def __init__(self, participantid=0):
        super().__init__()
        self._participant_id = participantid
        self._condition_list = [0, 1, 2, 3]
        self._balanced_condition_list = self.__get_balanced_condition_list(self._condition_list, self._participant_id)
        self._current_condition_index = 0

        self.__ui = uic.loadUi("calculator_experiment.ui", self)
        self.__equation_text = ""
        self.__equation_label = self.__ui.EquationLabel
        self.__result_text = ""
        self.__result_label = self.__ui.ResultLabel
        self.__allowed_numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        self.__allowed_operators = ["/", "*", "+", "-", "(", ")"]
        self._setup_keys()
        self._logfile_name = f"calculator_experiment_p_{participantid}.csv"
        self._calculatorLogger = CalculatorLogger(self._logfile_name)
        self._mouse_move_path = []
        self.setup_experiment_ui()
        self.__ui.stackedWidget.setCurrentIndex(self._balanced_condition_list[self._current_condition_index])
        self.show()

    def __get_balanced_condition_list(self, condition_list, participant_id):
        condition_count = len(condition_list)

        # First we need to create a balanced latin square according to our number of conditions:
        # https://medium.com/@graycoding/balanced-latin-squares-in-python-2c3aa6ec95b9
        balanced_order = [[((j // 2 + 1 if j % 2 else condition_count - j // 2) + i) % condition_count + 1 for j in
                           range(condition_count)] for i in range(condition_count)]
        if condition_count % 2:  # Repeat reversed for odd n
            balanced_order += [seq[::-1] for seq in balanced_order]
        order_for_participant = balanced_order[participant_id % condition_count]

        # Now we will reorder our conditions-list with the balanced-latin-square order we created above
        # https://stackoverflow.com/questions/2177590/how-can-i-reorder-a-list/2177607
        for i in range(len(order_for_participant)):
            order_for_participant[i] -= 1

        return [condition_list[i] for i in order_for_participant]

    def setup_experiment_ui(self):
        self.__ui.Condition1_text.insertPlainText(" Add the numbers from 1 to 20 using only the mouse")
        self.__ui.Condition2_text.insertPlainText(" Add the numbers from 1 to 20 using only the keyboard")
        self.__ui.Condition3_text.insertPlainText(" Calculate the result of (3*3 + 4*4) ∗ 15.2 using only the mouse.")
        self.__ui.Condition4_text.insertPlainText(
            " Calculate the result of (3*3 + 4*4) ∗ 15.2 using only the keyboard.")

        self.__ui.Condition1_start.clicked.connect(lambda: self._condition_started(1))
        self.__ui.Condition2_start.clicked.connect(lambda: self._condition_started(2))
        self.__ui.Condition3_start.clicked.connect(lambda: self._condition_started(3))
        self.__ui.Condition4_start.clicked.connect(lambda: self._condition_started(4))

    def _condition_started(self, id):
        self.__ui.stackedWidget.setCurrentIndex(4)
        self._calculatorLogger.add_new_log_data(time.time(), "task_started", None, None, self._balanced_condition_list[self._current_condition_index])

    # add a new input to our equation and equation-label
    def __add_to_equation(self, new_input):
        self.__equation_text += new_input
        self.__equation_label.setText(self.__equation_text)

    # execute an input command
    def __execute_command(self, command):
        if command == "=":
            self.__equation_text = ""
            self.__equation_label.setText(self.__equation_text)
            self._calculatorLogger.add_new_log_data(time.time(), "task_finished", None, None,
                                                    self._balanced_condition_list[self._current_condition_index])
            self.__result_text = self.__calculate_result()
            self.__result_label.setText(self.__result_text)
            self._current_condition_index += 1

            if self._current_condition_index > 3:
                sys.exit()
            self.__ui.stackedWidget.setCurrentIndex(self._balanced_condition_list[self._current_condition_index])
        elif command == "Clear":
            self.__equation_text = ""
            self.__equation_label.setText(self.__equation_text)
            self._calculatorLogger.add_new_log_data(time.time(), "task_restarted", None, None,
                                                    self._balanced_condition_list[self._current_condition_index])
        elif command == "DEL":
            self.__equation_text = self.__equation_text[:-1]
            self.__equation_label.setText(self.__equation_text)

    # calculates and returns the result of the equation by using the eval() function,
    # returns "Err" string if the equation cant be solved
    def __calculate_result(self):
        try:
            result = str(eval(self.__equation_text))
            return result
        except Exception:
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
                                self.__ui.NumButton_DecPoint, self.__ui.BracketButton_Open,
                                self.__ui.BracketButton_Close]

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
        self.__ui.NumButton_Clear.clicked.connect(lambda: self.__mouse_input_command("Clear"))
        self.__ui.NumButton_Clear.installEventFilter(self)
        self.__ui.NumButton_Delete.clicked.connect(lambda: self.__mouse_input_command("DEL"))
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
            self.__keyboard_input_command("DEL")
        elif event.text() == "." or event.text() == ",":
            self.__keyboard_input_number_or_operator(".")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    if len(sys.argv) > 1:
        participant_id = int(sys.argv[1])
        calculator = IttCalculator(participant_id)
    else:
        calculator = IttCalculator()
    sys.exit(app.exec_())
