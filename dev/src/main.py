'''
Author: Alex Hernandez
Date: 4/10/2024



Notes: This class is to instantiate the supervisor class


* Tests connections based on arguments (provided as a dict or JSON to the constructor)
*
*
*

'''
import pyvisa


class Supervisor:
    def __init__(self, options_dict):
        ''' options_dict structure has to be {requested_equipment_list: {eq1: gpib_address, eq1}, {equipment_options: {eq1: {option1, option2, option3...}}}, {more options}}'''
        self.options = options_dict
        #by default setting validation to false:
        self.ready = False
        self.__test_options__(self.options)
        '''some more stuff'''

    def __test_options__(self):
        '''Grab all resources'''
        resource_list = pyvisa.ResourceManager().list_resources()

        ''' get key,value pair from "requested_eq_list" node of dictionary, getting all key-value pairs of eq_name: gpib_address'''
        for equipment, gpib_address in self.options["requested_equipment_list"].keys(),self.options["requested_equipment_list"].values() :
            if gpib_address in resource_list:
                print(equipment + "is visible")
            else:
                print(equipment + "is not detected, please connect and/or initialize equipment in MAX")
        if we_fail_the_test
            return False
        if we_pass_the_test
            return True

