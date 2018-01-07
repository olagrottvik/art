from cursesmenu import CursesMenu
from cursesmenu.items import FunctionItem
from utils import jsonParser
from utils import cont
from utils import is_int
from utils import clearScreen
from utils import writeStringToFile
from module import Module
from module import Bus
from collections import OrderedDict
from prettytable import PrettyTable


class Editor(object):
    """Documentation for Editor

    """
    def __init__(self, edit, jsonfile, outputDir='output/', bus=None):
        self.jsonfile = jsonfile
        self.outputDir = outputDir
        self.recently_saved = False
        if bus is None:
            bus = {'bus_type': 'axi', 'data_width': 32, 'addr_width': 32}
        self.bus = Bus(bus)
        if edit:
            # Load the specified JSON file
            try:
                json = jsonParser(jsonfile)
                self.mod = Module(json, self.bus)
                self.recently_saved = True
            except Exception as e:
                print(str(e))
        else:
            # Get name, addrWidth, dataWidth and description
            print('Please enter some general information about your module.')
            print('All values can be changed at a later stage.')
            mod = OrderedDict()
            mod['name'] = input('Enter a module name: ')
            '''! @todo Add int check'''
            mod['addr_width'] = int(input("Enter the module's address width: "))
            mod['data_width'] = int(input("Enter the module's data width: "))
            mod['description'] = input('Enter a description for the module: ')
            mod['register'] = []
            self.mod = Module(mod, self.bus)

    def showMenu(self):
        self.menu = CursesMenu('art - Module Editor', self.setSubtitle())

        self.menu.append_item(FunctionItem('Edit name', self.editName))
        self.menu.append_item(FunctionItem('List registers', self.listRegisters))
        self.menu.append_item(FunctionItem('Add new register', self.addRegister))
        self.menu.append_item(FunctionItem('Remove register', self.removeRegister))
        self.menu.append_item(FunctionItem('Update addresses', self.updateAddresses))
        self.menu.append_item(FunctionItem('Save JSON', self.saveJSON))
        self.menu.show()

    def updateMenu(self):
        self.menu.subtitle = self.setSubtitle()

    def editName(self):
        print('Change the module name from current: ' + self.mod.name)
        self.mod.name = input('Enter new name: ')
        self.recently_saved = False
        self.updateMenu()

    def returnRegisters(self):
        while True:
            clearScreen()
            if len(self.mod.registers) < 1:
                print('No registers created at this point...')
                cont()
                return
            else:
                table = PrettyTable()
                table.field_names = ['#', 'Name', 'Mode', 'Address', 'Type', 'Length', 'Reset', 'Description']
                for i, reg in enumerate(self.mod.registers):
                    table.add_row([i, reg.name, reg.mode, hex(reg.address), reg.sig_type, reg.length,
                                   reg.reset, reg.description])
                return(table)

    def listRegisters(self):
        table = self.returnRegisters()
        if table is None:
            return
        print(table)
        print('\nEnter the register number for register details, or q to quit...')
        while True:
            choice = input('Choice: ')
            if self.valid_register_input(choice):
                break
            else:
                print(choice + ' is not a valid choice')
        if choice == 'q':
            return
        else:
            clearScreen()
            self.printRegister(int(choice), table)
            cont()

    def printRegister(self, regNum, table):
        reg = self.mod.registers[regNum]
        print(table.get_string(start=regNum, end=(regNum+1)))

        if len(reg.fields) > 0:
            print('\nFields:')
            table_fields = PrettyTable()
            table_fields.field_names = ['#', 'Name', 'Type', 'Position', 'Length', 'Reset', 'Description']
            for i, field in enumerate(reg.fields):

                table_fields.add_row([i, field.name, field.sig_type, field.get_pos_str(), field.length,
                                      field.reset, field.description])

            print(table_fields)

    def addRegister(self):
        reg = OrderedDict()

        print('Input register information (abort with Ctrl-C)')
        try:
            reg['name'] = input('Name: ')
            reg['description'] = input('Description: ')
            while True:
                try:
                    mode = int(input('Mode (0 = RW, 1 = RO): '))
                    if mode == 0:
                        reg['mode'] = 'rw'
                        break
                    elif mode == 1:
                        reg['mode'] = 'ro'
                        break
                    else:
                        print(str(mode) + ' is not a valid choice...')
                except Exception:
                    print('That is not a valid choice...')

            fields = []
            while True:
                field_dic = OrderedDict()
                add_fields = input('Do you want to add a field? (Y/n): ')
                if add_fields.upper() == 'N':
                    break
                elif add_fields.upper() == 'Y' or add_fields == '':
                    field_dic['name'] = input('Field name: ')
                    while True:
                        field_dic['type'] = input('Field type (sl/slv): ')
                        if field_dic['type'] != 'sl' and field_dic['type'] != 'slv':
                            print(field_dic['type'] + ' is not a valid choice...')
                        else:
                            break

                    if field_dic['type'] == 'slv':
                        while True:
                            try:
                                field_dic['length'] = int(input('Field length: '))
                                break
                            except Exception:
                                print('That is not an integer...')

                    else:
                        field_dic['length'] = 1

                    while True:
                        field_dic['reset'] = input('Field reset (default=0x0): ')

                        if field_dic['reset'] == '':
                            field_dic['reset'] = '0x0'
                            break
                        else:
                            try:
                                field_dic['reset'] = hex(int(field_dic['reset'], 16))
                                break
                            except Exception:
                                print(field_dic['reset'] + ' is not a valid reset value...')

                    field_dic['description'] = input('Field description: ')

                    fields.append(field_dic)

                else:
                    print(add_fields + ' is not a valid choice...')

            if len(fields) > 0:
                print('Register is of type: "fields"')
                reg['type'] = 'fields'
                reg['fields'] = fields

            else:
                while True:

                    reg['type'] = input('Type (DEFAULT/slv/sl): ')
                    if reg['type'] in ['default', 'slv', 'sl']:
                        break
                    elif reg['type'] == '':
                        reg['type'] = 'default'
                        break
                    else:
                        print(reg['type'] + ' is not a valid register type...')

            if reg['type'] == 'slv':
                while True:
                    try:
                        reg['length'] = int(input('Length: '))
                        break
                    except Exception:
                        print('That is not a valid length...')

            if input('Auto-assign address? (Y/n): ').upper() == 'N':
                while True:
                    try:
                        reg['address'] = input('Address (hex): ')
                        reg['address'] = hex(int(reg['address'], 16))
                        break

                    except Exception:
                        print(reg['address'] + ' is not a valid address...')

            if reg['type'] != 'fields':
                while True:
                    reg['reset'] = input('Reset (default=0x0): ')

                    if reg['reset'] == '':
                        reg['reset'] = '0x0'
                        break
                    else:
                        try:
                            reg['reset'] = hex(int(reg['reset'], 16))
                            break
                        except Exception:
                            print(reg['reset'] + ' is not a valid reset value...')

            table = PrettyTable()
            table.field_names = ['#', 'Name', 'Mode', 'Address', 'Type', 'Length', 'Reset', 'Description']

            # Table values based on what values exists
            table_name = reg['name']
            table_mode = reg['mode']

            if 'address' in reg:
                table_address = reg['address']
            else:
                table_address = 'auto'

            table_type = reg['type']

            if reg['type'] == 'fields':
                table_length = 'auto'
            elif 'length' in reg:
                table_length = reg['length']
            else:
                table_length = self.mod.busDataWitdh

            if reg['type'] == 'fields':
                table_reset = 'auto'
            elif 'reset' in reg:
                table_reset = reg['reset']
            else:
                table_reset = 'auto'

            table_description = reg['description']

            table.add_row([len(self.mod.registers), table_name, table_mode, table_address, table_type,
                           table_length, table_reset, table_description])

            print(table)

            if 'fields' in reg:
                print('\nFields:')
                table_fields = PrettyTable()
                table_fields.field_names = ['#', 'Name', 'Type', 'Length', 'Reset', 'Description']
                for i, field in enumerate(reg['fields']):

                    table_fields.add_row([i, field['name'], field['type'], field['length'],
                                          field['reset'], field['description']])

                print(table_fields)

            if input('Confirm creation of register? (Y/n): ').upper() != 'N':
                self.mod.addRegister(reg)

                self.recently_saved = False
                self.updateMenu()
            else:
                return

        except KeyboardInterrupt:
            print('\nAdding register aborted!')
            cont()

        except Exception as e:
            print('\nAdding register failed!')
            print(str(e))
            cont()

    def removeRegister(self):
        table = self.returnRegisters()
        if table is None:
            return
        print(table)
        print('\nEnter the register number for removal, or q to quit...')
        while True:
            choice = input('Choice: ')
            if self.valid_register_input(choice):
                break
            else:
                print(choice + ' is not a valid choice')
        if choice == 'q':
            return
        else:
            clearScreen()
            self.printRegister(int(choice), table)

            if input('Are you sure you want to delete this register? (y/N): ').upper != 'Y':
                del self.mod.registers[int(choice)]

        self.recently_saved = False
        self.updateMenu()

    def updateAddresses(self):
        self.mod.updateAddresses()
        print("Addresses are updated..")
        self.recently_saved = False
        self.updateMenu()
        cont()

    def saveJSON(self):
        print('Saving ' + self.jsonfile + ' ...')

        # Get JSON with addresses
        json = self.mod.printJSON(True)
        try:
            writeStringToFile(json, self.jsonfile, None)
        except Exception:
            print('Saving failed...')
            cont()
            return

        self.recently_saved = True
        cont()
        self.updateMenu()

    def setSubtitle(self):
        if self.recently_saved:
            s = ' - SAVED'
        else:
            s = ' - NOT SAVED'
        return self.mod.name + ' / ' + str(self.mod.addrWidth) + ' / ' + str(self.mod.dataWidth) + s

    def valid_register_input(self, s):
        if s == 'q':
            return True
        elif is_int(s):
            index = int(s)
            for i, reg in enumerate(self.mod.registers):
                if index == i:
                    return True
        return False
