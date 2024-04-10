'''
Author: Alex Hernandez
Date: 4/10/2024



Notes: This class is to instantiate the supervisor class


* Tests connections based on arguments (provided as a dict or JSON to the constructor)
*
*
*

'''


class Supervisor:
    def __init__(self, options_dict):
        ''' options_dict structure has to be {requested_equipment_list: {eq1: gpib_address, eq1}, {equipment_options: {eq1: {option1, option2, option3...}}}, {more options}}'''
        self.options = options_dict
        #by default setting validation to false:
        self.ready = False
        self.__test__(self.options)
        '''some more stuff'''

    def __test__(self):
        if we_fail_the_test
            return False
        if we_pass_the_test
            return True

