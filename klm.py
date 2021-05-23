#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This python program was implemented by Michael Meckl.
"""

import sys
import os
import argparse


"""
The KLM default values are taken from Card, S. K., Moran, T. P., & Newell, A. (1980). The keystroke-level model for
user performance time with interactive systems. Communications of the ACM, 23(7), 396-410. The value for the
M-operator was taken from Kieras, D. (2001). Using the keystroke-level model to estimate execution times.
University of Michigan, 555.
"""
KLM_DEFAULT_VALUES = {
    "K": 0.28,  # Average nonsecretarial typist (40 wpm), 0.20 for average skilled typist (55 wpm)
    "P": 1.1,
    "H": 0.4,
    "B": 0.1,
    "M": 1.20,  # 1.35 according to Card et al.
    # "D": 9*Nd + 0.16*Id,
}

KLM_CUSTOM_VALUES = {
    # TODO add own values after 6.2 is finished!
    "K": 0.0,
    "P": 0.0,
    "H": 0.0,
    "B": 0.0,
    "M": 1.20,
}


def parse_klm_file(file_name: str) -> str:
    """
    Parses the given file and returns all klm operators in it.

    :param file_name: the path to the klm input file
    :return: a string containing all klm operators in the order they were found within the file
    """

    # check if the file exists
    if os.path.isfile(file_name):
        with open(file_name) as setup_file:
            # read in content
            content = setup_file.read()

            # make text uppercase so everything will match the dict values no matter in which case it was entered
            content = content.upper()

            # split on line break (this removes the line breaks too in contrast to readlines()) and remove all comments
            operators = []
            for line in content.splitlines():
                # find the index in the string when the comment starts
                comment_index = line.find("#")
                # and remove everything from this index onwards as we don't need it
                line_without_comment = line[:line.find("#")] if comment_index != -1 else line
                if line_without_comment != "":
                    # save line without the trailing whitespaces if there were actual operators besides the comment
                    operators.append(line_without_comment.rstrip())

            # operators = [line[:line.find("#")].rstrip() if line.find("#") != -1 else line.rstrip()
            #              for line in content.splitlines()]

            operator_string = "".join(operators).replace(" ", "")  # join all operators to one string without spaces
            print(f"Input operators were: {operator_string}")
            return operator_string
    else:
        sys.stderr.write("Given setup file does not exist!")
        exit(1)


def calculate_completion_time(operators: str, klm_value_dict: dict[str, float]) -> int:
    """
    Calculates a prediction for the task completion time for the given operators based on the values specified in the
    klm_value_dict.

    :param operators: a string containing all operators
    :param klm_value_dict: a python dictionary containing time values (in seconds) for the klm operators
    :return: the calculated time for all operators in seconds
    """

    task_completion_time = 0  # in seconds
    tmp_number = ""  # temp variable for storing the count before some operators

    for operator in operators:
        if klm_value_dict.get(operator, -1) != -1:  # check if the operator is a valid klm operator
            operator_time = klm_value_dict.get(operator)
            task_completion_time += operator_time if tmp_number == "" else int(tmp_number) * operator_time
            tmp_number = ""  # reset temp variable

        elif operator.isdigit():
            tmp_number += operator  # append the digit string to the temp number: for 130 it would be "1", "13", "130"

        else:
            sys.stderr.write(f"Given operator {operator} is neither a valid klm operator nor a digit!")

    return task_completion_time


def main():
    # parse command line input and print out some helpful information
    parser = argparse.ArgumentParser(description="A small program to parse klm operators given as a file and output"
                                                 " the calculated task completion time for these operators.")
    parser.add_argument("klm_file", help="A file containing the klm operators (can contain python comments (#) too)",
                        type=str)
    # parser.add_argument("-c", "--use-custom", help="use custom values for the klm operators instead of the default",
    #                     action="store_true")  # store_true sets the value to True if specified and to False if not
    args = parser.parse_args()
    input_file = args.klm_file

    # parse input file with the klm operators
    parsed_operators = parse_klm_file(input_file)

    # calculate task completion times for default and custom klm values
    predicted_time = calculate_completion_time(operators=parsed_operators, klm_value_dict=KLM_CUSTOM_VALUES)
    print(f"Predicted task completion time for the given operators using custom klm values: "
          f"{predicted_time:0.3f} seconds.")
    predicted_time = calculate_completion_time(operators=parsed_operators, klm_value_dict=KLM_DEFAULT_VALUES)
    print(f"Predicted task completion time for the given operators using default klm values: "
          f"{predicted_time:0.3f} seconds.")


if __name__ == '__main__':
    main()
