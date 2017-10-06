from utils import indentString
from utils import jsonParser
from exceptions import *
import sys


def test():
    try:
        
        a = jsonParser()
        mod = Module(a)
        #print(mod)
        #print(mod.returnModulePkgVHDL())

        #print(mod.printJSON(True))
        print(mod.returnRegisterPIFVHDL())

    except Exception as e:
        print(str(e))

class Module:
    """! @brief


    """

    def __init__(self, mod):
        """! @brief

        """
        self.name = mod['name']
        self.addr_width = mod['addr_width']
        self.data_width = mod['data_width']
        self.description = mod['description']
        self.registers = []
        self.addresses = []
        self.addRegisters(mod['register'])
        
        

    def addRegisters(self, regs):
        for i in regs:
            if self.registerValid(i):
                # Check if size is specified
                if "address" in i:
                    addr = int(i['address'], self.addr_width)
                    if self.isAddressIsFree(addr):
                        self.isAddressOutOfRange(addr)
                        self.addresses.append(addr)
                        self.registers.append(Register(i, addr,
                                                       self.data_width))
                    else:
                        raise InvalidAddress(i['name'], addr)
                else:
                    self.registers.append(Register(i, self.getNextAddress(),
                                                   self.data_width))
            else:
                raise InvalidRegister(i)

    def returnRegisterPIFVHDL(self):

        s = 'use work.' + self.name + '.all;\n\n'
        s += 'entity ' + self.name + '_axi_pif is\n\n'

        s += indentString('port (')

        par = ''
        par += '-- register record signals\n'
        par += 'axi_ro_regs : in  t_' + self.name + '_ro_regs;\n'
        par += 'axi_rw_regs : out t_' + self.name + '_rw_regs;\n'
        par += '\n'
        par += '-- bus signals\n'
        par += 'clk         : in  std_logic;\n'
        par += 'areset_n    : in  std_logic;\n'
        par += 'awaddr      : in  t_' + self.name + '_addr;\n'
        par += 'awvalid     : in  std_logic;\n'
        par += 'awready     : out std_logic;\n'
        par += 'wdata       : in  t_' + self.name + '_data;\n'
        par += 'wvalid      : in  std_logic;\n'
        par += 'wready      : out std_logic;\n'
        par += 'bresp       : out std_logic_vector(1 downto 0);\n'
        par += 'bvalid      : out std_logic;\n'
        par += 'bready      : in  std_logic;\n'
        par += 'araddr      : in  t_' + self.name + '_addr;\n'
        par += 'arvalid     : in  std_logic;\n'
        par += 'arready     : out std_logic;\n'
        par += 'rdata       : out t_' + self.name + '_data;\n'
        par += 'rresp       : out std_logic_vector(1 downto 0);\n'
        par += 'rvalid      : out std_logic;\n'
        par += 'rready      : in  std_logic\n'
        par += ');\n'
        s += indentString(par, 2)
        
        s += 'end ' + self.name + '_axi_pif;\n\n'

        
        s += 'architecture behavior of ' + self.name + '_axi_pif is\n\n'

        par = ''
        par += '-- internal signal for readback' + '\n'
        par += 'signal axi_rw_regs_i : t_'
        par += self.name + '_rw_regs;\n\n'

        par += '-- internal bus signals for readback\n'
        par += 'signal awaddr_i      : t_' + self.name + '_addr;\n'
        par += 'signal awready_i     : std_logic;\n'
        par += 'signal wready_i      : std_logic;\n'
        par += 'signal bresp_i       : std_logic_vector(1 downto 0);\n'
        par += 'signal bvalid_i      : std_logic;\n'
        par += 'signal araddr_i      : t_' + self.name + '_addr;\n'
        par += 'signal arready_i     : std_logic;\n'
        par += 'signal rdata_i       : t_' + self.name + '_data;\n'
        par += 'signal rresp_i       : std_logic_vector(1 downto 0);\n'
        par += 'signal rvalid_i      : std_logic;\n\n'

        par += 'signal slv_reg_rden : std_logic;\n'
        par += 'signal slv_reg_wren : std_logic;\n'
        par += 'signal reg_data_out : t_' + self.name + '_data;\n'
        par += '-- signal byte_index   : integer' + '; -- unused\n\n'
        s += indentString(par)

        s += 'begin\n\n'
        s += indentString('axi_rw_regs <= axi_rw_regs_i') + ';\n'
        s += '\n'

        par = ''
        par += 'awready <= awready_i;\n'
        par += 'wready  <= wready_i;\n'
        par += 'bresp   <= bresp_i;\n'
        par += 'bvalid  <= bvalid_i;\n'
        par += 'arready <= arready_i;\n'
        par += 'rdata   <= rdata_i;\n'
        par += 'rresp   <= rresp_i;\n'
        par += 'rvalid  <= rvalid_i;\n'
        par += '\n'

        s += indentString(par)
        

        s += indentString('p_awready : process(clk);\n')
        s += indentString('begin\n')
        s += indentString('if rising_edge(clk) then\n', 2)
        s += indentString("if areset_n = '0' then\n", 3)
        s += indentString("awready_i <= '0';\n", 4)
        s += indentString("elsif (awready_i = '0' and awvalid = '1' ", 3)
        s += "and wvalid = '1') then\n"
        s += indentString("awready_i <= '1';\n", 4)
        s += indentString('else\n', 3)
        s += indentString("awready_i <= '0';\n", 4)
        s += indentString('end if;\n', 3)
        s += indentString('end if;\n', 2)
        s += indentString('end process p_awready;\n')
        s += '\n'

        s += indentString('p_awaddr : process(clk);\n')
        s += indentString('begin\n')
        s += indentString('if rising_edge(clk) then\n', 2)
        s += indentString("if areset_n = '0' then\n", 3)
        s += indentString("awaddr_i <= (others => '0');\n", 4)
        s += indentString("elsif (awready_i = '0' and awvalid = '1' ", 3)
        s += "and wvalid = '1') then\n"
        s += indentString("awaddr_i <= awaddr;\n", 4)
        s += indentString('end if;\n', 3)
        s += indentString('end if;\n', 2)
        s += indentString('end process p_awaddr;\n')
        s += '\n'

        s += indentString('p_wready : process(clk);\n')
        s += indentString('begin\n')
        s += indentString('if rising_edge(clk) then\n', 2)
        s += indentString("if areset_n = '0' then\n", 3)
        s += indentString("wready_i <= '0';\n", 4)
        s += indentString("elsif (wready_i = '0' and awvalid = '1' ", 3)
        s += "and wvalid = '1') then\n"
        s += indentString("wready_i <= '1';\n", 4)
        s += indentString('else\n', 3)
        s += indentString("wready_i <= '0';\n", 4)
        s += indentString('end if;\n', 3)
        s += indentString('end if;\n', 2)
        s += indentString('end process p_wready;\n')
        s += '\n'

        s += indentString('slv_reg_wren <= wready_i and wvalid and awready_i and awvalid;\n')
        s += '\n'
        s += indentString('p_mm_select_write : process(clk);\n')
        s += indentString('begin\n')
        s += indentString("if areset_n = '0' then\n", 2)

        # Assign default values
        # @todo Ensure that record entries' and registers' default values are
        # assigned properly
        par = ''
        # create a generator for looping through all rw regs
        gen = (reg for reg in self.registers if reg.mode == "rw")
        for reg in gen:

            if reg.regtype == 'record':

                for entry in reg.entries:
                    par += 'axi_rw_regs_i.'
                    par += reg.name + '.' + entry['name'] + ' <= '
                    if entry['type'] == 'slv':
                        par += "(others => '0');\n"
                    elif entry['type'] == 'sl':
                        par += "'0';\n"
                    else:
                        raise UndefinedEntryType("Unknown entry type: " + entry['type'])
            elif reg.regtype == 'slv' or reg.regtype == 'default':
                par += 'axi_rw_regs_i.'
                par += reg.name + " <= (others => '0');\n"
            elif reg.regtype == 'sl':
                par += 'axi_rw_regs_i.'
                par += reg.name + " <= '0';\n"
            else:
                raise UndefinedRegisterType("Unknown register type: " + reg.regtype)
        par += '\n'
        s += indentString(par, 3)

        s += indentString('elsif rising_edge(clk) then\n', 2)
        s += indentString("if (slv_reg_wren = '1') then\n", 3)
        s += '\n'
        s += indentString('case awaddr_i is\n', 4)

        # create a generator for looping through all rw regs
        gen = (reg for reg in self.registers if reg.mode == "rw")
        for reg in gen:
            s += indentString('when C_ADDR_', 5)
            s += reg.name.upper() + ' =>\n\n'
            par = ''
            if reg.regtype == 'record':

                lasthigh = -1
                for entry in reg.entries:
                    par += 'axi_rw_regs_i.' + reg.name + '.' + entry['name']
                    par += ' <= wdata('
                    if entry['type'] == 'sl':
                        lasthigh += 1
                        par += str(lasthigh)
                    elif entry['type'] == 'slv':
                        lasthigh += 1
                        par += str(entry['length'] + lasthigh - 1)
                        par += ' downto '
                        par += str(lasthigh)
                        lasthigh+= entry['length'] - 1
                    else:
                        raise UndefinedEntryType("Unknown entry type: " + entry['type'])
                    par += ');\n'
                    

            elif reg.regtype == 'default':
                par += 'axi_rw_regs_i.' + reg.name + ' <= wdata;\n'
            elif reg.regtype == 'slv':
                par += 'axi_rw_regs_i.' + reg.name + ' <= wdata('
                par += str(reg.length-1) + ' downto 0);\n'
            elif reg.regtype == 'sl':
                par += 'axi_rw_regs_i.' + reg.name + ' <= wdata(0);\n'
            else:
                raise UndefinedRegisterType("Unknown register type: " + reg.regtype)
            s += indentString(par, 6)            
            s += '\n'

        s += indentString('when others =>\n', 5)
        s += indentString('null;\n', 6)
        s += '\n'
        s += indentString('end case;\n', 4)
        s += indentString('end if;\n', 3)
        s += indentString('end if;\n', 2)
        s += indentString('end process p_mm_select_write;\n')
        s += '\n'

        s += indentString('p_write_response : process(clk)\n')
        s += indentString('begin\n')
        s += indentString('if rising_edge(clk) then\n', 2)
        s += indentString("if areset_n = '0' then\n", 3)
        s += indentString("bvalid_i <= '0';\n", 4)
        s += indentString('bresp_i  <= "00";\n', 4)
        s += indentString("elsif (awready_i = '1' and awvalid = '1' and ", 3)
        s += "wready_i = '1' and wvalid = '1' and bvalid_i = '0') then\n"
        s += indentString("bvalid_i <= '1';\n", 4)
        s += indentString('bresp_i  <= "00";\n', 4)
        s += indentString("elsif (bready = '1' and bvalid_i = '1') then\n", 3)
        s += indentString("bvalid_i <= '0';\n", 4)
        s += indentString('end if;\n', 3)
        s += indentString('end if;\n', 2)
        s += indentString('end process p_write_response;\n')
        s += '\n'

        s += indentString('p_arready : process(clk)\n')
        s += indentString('begin\n')
        s += indentString('if rising_edge(clk) then\n', 2)
        s += indentString("if areset_n = '0' then\n", 3)
        s += indentString("arready_i <= '0';\n", 4)
        s += indentString("araddr_i  <= (others => '0';\n", 4)
        s += indentString("elsif (arready_i = '0' and arvalid = '1') then\n", 3)
        s += indentString("arready_i <= '1';\n", 4)
        s += indentString('araddr_i  <= araddr;\n', 4)
        s += indentString('else\n', 3)
        s += indentString("arready_i <= '0';\n", 4)
        s += indentString('end if;\n', 3)
        s += indentString('end if;\n', 2)
        s += indentString('end process p_arready;\n')
        s += '\n'

        s += indentString('p_arvalid : process(clk)\n')
        s += indentString('begin\n')
        s += indentString('if rising_edge(clk) then\n', 2)
        s += indentString("if areset_n = '0' then\n", 3)
        s += indentString("rvalid_i <= '0';\n", 4)
        s += indentString('rresp_i  <= "00";\n', 4)
        s += indentString("elsif (arready_i = '1' and arvalid = '1' and ", 3)
        s += "rvalid_i = '0') then\n"
        s += indentString("rvalid_i <= '1';\n", 4)
        s += indentString('rresp_i  <= "00";\n', 4)
        s += indentString("elsif (rvalid_i = '1' and rready = '1') then\n", 3)
        s += indentString("rvalid_i <= '0';\n", 4)
        s += indentString('end if;\n', 3)
        s += indentString('end if;\n', 2)
        s += indentString('end process p_arvalid;\n')
        s += '\n'

        s += indentString('slv_reg_rden <= arready_i and arvalid and ')
        s += '(not rvalid_i);\n'
        s += '\n'
        s += indentString('p_mm_select_read : process (all)\n')
        s += indentString('begin\n')
        s += '\n'
        s += indentString("reg_data_out <= (others => '0');\n", 2)
        s += '\n'
        s += indentString('case aradrr_i is\n', 2)
        s += '\n'
        # Generator for looping through all "readable registers, rw&ro
        gen = [reg for reg in self.registers
               if reg.mode == "ro" or reg.mode == "rw"]
        for reg in gen:
            s += indentString('when C_ADDR_', 3)
            s += reg.name.upper() + ' =>\n\n'
            par = ''
            
            if reg.regtype == 'record':

                lasthigh = -1
                for entry in reg.entries:
                    lasthigh += 1
                    par += 'reg_data_out('

                    if entry['type'] == 'sl':
                        par += str(lasthigh)
                    elif entry['type'] == 'slv':
                        par += str(entry['length'] + lasthigh - 1)
                        par += ' downto ' + str(lasthigh)
                        lasthigh += entry['length'] - 1
                    else:
                        raise UndefinedEntryType('Unknown entry type: ' + entry['type'])
                    if reg.mode == 'rw':
                        par += ') <= axi_rw_regs_i.'
                    elif reg.mode == 'ro':
                        par += ') <= axi_ro_regs_i.'
                    else:
                        raise Exception("Unknown error occurred")
                    par += reg.name + '.' + entry['name'] + ';\n'

            elif reg.regtype == 'default':
                par += 'reg_data_out <= '
                if reg.mode == 'rw':
                    par += 'axi_rw_regs_i.'
                elif reg.mode == 'ro':
                    par += 'axi_ro_regs_i.'
                else:
                        raise Exception("Unknown error occurred")
                par += reg.name + ';\n'

            elif reg.regtype == 'slv':
                par += 'reg_data_out('
                par += str(reg.length-1) + ' downto 0) <= '
                if reg.mode == 'rw':
                    par += 'axi_rw_regs_i.'
                elif reg.mode == 'ro':
                    par += ') <= axi_ro_regs_i.'
                else:
                        raise Exception("Unknown error occurred")
                par += reg.name + ';\n'

            elif reg.regtype == 'sl':
                par += 'reg_data_out(0) <= '
                if reg.mode == 'rw':
                    par += 'axi_rw_regs_i.'
                elif reg.mode == 'ro':
                    par += ') <= axi_ro_regs_i.'
                else:
                        raise Exception("Unknown error occurred")
                par += reg.name + ';\n'

            else:
                raise UndefinedRegisterType("Unknown register type: " + reg.regtype)
            s += indentString(par, 4)
            s += '\n'

        s += indentString('when others =>\n', 3)
        s += indentString('null;\n', 4)
        s += '\n'
        s += indentString('end case;\n', 2)
        s += indentString('end process p_mm_select_read;\n')
        s += '\n'

        s += indentString('p_output : process(clk)\n')
        s += indentString('begin\n')
        s += indentString('if rising_edge(clk) then\n', 2)
        s += indentString("if areset_n = '0' then\n", 3)
        s += indentString("rdata_i <= (others => '0');\n", 4)
        s += indentString("elsif (slv_reg_rden = '1') then\n", 3)
        s += indentString("rdata_i <= reg_data_out;\n", 4)
        s += indentString('end if;\n', 3)
        s += indentString('end if;\n', 2)
        s += indentString('end process p_arvalid;\n')
        s += '\n'

        s += 'end behavior;'
        
        return s


    def returnModulePkgVHDL(self):
        s = "package " + self.name + "_pkg is"
        s += "\n\n"

        par = ''
        par += "constant C_" + self.name.upper()
        par += "_ADDR_WIDTH : natural := " + str(self.addr_width) + ";\n"
        par += "constant C_" + self.name.upper()
        par += "_DATA_WIDTH : natural := " + str(self.data_width) + ";\n"
        par += "\n"

        par += "subtype t_" + self.name + "_addr is "
        par += "std_logic_vector(C_" + self.name.upper() + "_ADDR_WIDTH-1 "
        par += "downto 0);\n"

        par += "subtype t_" + self.name + "_data is "
        par += "std_logic_vector(C_" + self.name.upper() + "_DATA_WIDTH-1 "
        par += "downto 0);\n"
        par += "\n"

        for i in self.registers:
            par += "constant C_ADDR_" + i.name.upper()
            par += " : t_" + self.name + "_addr := " + str(self.addr_width)
            par += 'X"' + '%X' % i.address + '";\n'
        par += '\n'
        s += indentString(par)
        
        # Create all types for RW registers with records
        for i in self.registers:
            if i.mode == "rw" and i.regtype == "record":
                s += indentString("type t_" + self.name + "_rw_")
                s += i.name + " is record\n"

                for j in i.entries:
                    s += indentString(j['name'], 2) + " : "
                    if j['type'] == "slv":
                        s += "std_logic_vector(" + str(j['length']-1)
                        s += " downto 0);\n"
                    elif j['type'] == "sl":
                        s += "std_logic;\n"
                    else:
                        raise RuntimeError("Something went wrong..." + j['type'])
                s += indentString("end record;\n")
        s += "\n"

                
        # The RW register record type
        s += indentString("type t_" + self.name + "_rw_regs is record")
        for i in self.registers:
            if i.mode == "rw":
                s += indentString(i.name, 2) + " : "
                if i.regtype == "default" or (i.regtype == "slv" and i.length == self.data_width):
                    s += "t_" + self.name + "_data;\n"
                elif i.regtype == "slv":
                    s += "std_logic_vector(" + str(i.length-1) + " downto 0);\n"
                elif i.regtype == "sl":
                    s += "std_logic;\n"
                elif i.regtype == "record":
                    s += "t_" + self.name + "_rw_" + i.name + ";\n"
                else:
                    raise RuntimeError("Something went wrong... What?")
        s += indentString("end record;\n")
        s += "\n"

        # Create all types for RO registers with records
        for i in self.registers:
            if i.mode == "ro" and i.regtype == "record":
                s += indentString("type t_" + self.name + "_ro_")
                s += i.name + " is record\n"

                for j in i.entries:
                    s += indentString(j['name'], 2) + " : "
                    if j['type'] == "slv":
                        s += "std_logic_vector(" + str(j['length']-1)
                        s += " downto 0);\n"
                    elif j['type'] == "sl":
                        s += "std_logic;\n"
                    else:
                        raise RuntimeError("Something went wrong... WTF?")
                s += indentString("end record;\n")
        s += "\n"

        # The RO register record type
        s += indentString("type t_" + self.name + "_ro_regs is record")
        s += "\n"
        for i in self.registers:
            if i.mode == "ro":
                s += indentString(i.name, 2) + " : "
                if i.regtype == "default" or (i.regtype == "slv" and i.length == self.data_width):
                    s += "t_" + self.name + "_data;\n"
                elif i.regtype == "slv":
                    s += "std_logic_vector(" + str(i.length-1) + " downto 0);\n"
                elif i.regtype == "sl":
                    s += "std_logic;\n"
                elif i.regtype == "record":
                    s += "t_" + self.name + "_ro_" + i.name + ";\n"
                else:
                    raise RuntimeError("Something went wrong... What now?" + i.regtype)
        s += indentString("end record;\n")
        s += "\n"

        s += "end package " + self.name + "_pkg;"
        
        return s
        

    def printJSON(self, includeAddress=False):
        """! @brief Returns JSON string

        """
        string = '{ "name": "'
        string += self.name + '",\n'
        string += indentString('"addr_width": ')
        string += str(self.addr_width) + ',\n'
        string += indentString('"data_width": ')
        string += str(self.data_width) + ',\n'

        string += indentString('"register": [') + '\n'

        for i, reg in enumerate(self.registers):

            string += indentString('{"name": "', 3)
            string += reg.name + '",\n'
            string += indentString('"mode": "', 3)
            string += reg.mode + '",\n'
            string += indentString('"type": "', 3)
            string += reg.regtype + '",\n'

            if includeAddress:
                string += indentString('"address": "', 3)
                string += str(hex(reg.address)) + '",\n'

            if reg.length != 0:

                string += indentString('"length": ', 3)
                string += str(reg.length) + ',\n'

            if len(reg.entries) > 0:
                string += indentString('"entries": [', 3) + '\n'

                for j, entry in enumerate(reg.entries):
                    string += indentString('{"name": "', 4)
                    string += entry['name'] + '", "type": "' + entry['type'] + '"'

                    if entry['type'] == 'slv':
                        string += ', "length": ' + str(entry['length'])

                    if j < len(reg.entries)-1:
                        string += '},\n'
                    else:
                        string += '}\n'
                        

                string += indentString('],', 3) + '\n'
                
            string += indentString('"description": "', 3)
            string += reg.description + '"\n'

            if i < len(self.registers)-1:
                string += indentString('},', 3) + '\n'
            else:
                string += indentString('}', 3) + '\n'

        string += indentString('],', 2) + '\n'
        string += indentString('"description": "', 2)
        string += self.description + '"\n'

        string += '}'

        return string
        

    def getNextAddress(self):
        """! @brief Will get the next address based on the byte-addressed scheme
        
        """
        addr = 0
        foundAddr = False
        while (not foundAddr):
            self.isAddressOutOfRange(addr)
            if self.isAddressIsFree(addr):
                self.addresses.append(addr)
                return addr
            else:
                # force integer division to prevent float
                addr += self.data_width//8

    def isAddressOutOfRange(self, addr):
        if addr > pow(2, self.addr_width)-1:
            raise RuntimeError("Address " + hex(addr) + " is definetely out of range...")
        return True

    def isAddressIsFree(self, addr):
        for i in self.addresses:
            if i == addr:
                return False

        # If loop completes without matching addresses
        return True

    def registerValid(self, reg):
        if set(("name", "mode", "type", "description")).issubset(reg):
            return True
        else:
            return False

    def __str__(self):
        string = "Name: " + self.name + "\n"
        string += "Address width: " + str(self.addr_width) + "\n"
        string += "Data width: " + str(self.data_width) + "\n"
        string += "Description: " + self.description + "\n"
        for i, reg in enumerate(self.registers):
            string += "Register " + str(i) + "\n"
            string += indentString(str(reg), 2)
        return string



class Register:
    """! @brief


    """

    def __init__(self, reg, address, mod_data_length):
        self.name = reg['name']
        self.mode = reg['mode']
        self.description = reg['description']
        self.address = address
        self.regtype = ""
        self.length = 0
        self.entries = []
        
        if reg['type'] == 'default':
           self.regtype = 'default'
        elif reg['type'] == 'slv':
            self.regtype = 'slv'
            self.length = reg['length']
        elif reg['type'] == 'sl':
            self.regtype = 'sl'
            self.length = 0
        elif reg['type'] == 'record':
            self.regtype = 'record'
            for entry in reg['entries']:
                if entry['type'] == 'slv':
                    self.entries.append({'name': entry['name'],
                                        'type': 'slv',
                                         'length': entry['length']})
                    self.length += entry['length']
                elif entry['type'] == 'sl':
                    self.entries.append({'name': entry['name'],
                                         'type': 'sl', 'length': 1})
                    self.length += 1
                else:
                    raise UndefinedEntryType(entry['type'])
        else:
            raise UndefinedRegisterType(reg['type'])

        # Perform check that data bits are not exceeded
        self.checkRegisterDataLength(mod_data_length)
        

    def __str__(self):
        string = "Name: " + self.name + "\n"
        string = "Address: " + hex(self.address) + "\n"
        string += "Mode: " + self.mode + "\n"
        string += "Type: " + self.regtype + "\n"
        string += "Length: " + str(self.length)
        if self.regtype == 'record':

            for i in self.entries:
                string += "\n"
                string += indentString("Name: " + i['name'] +
                                       " Type: " + i['type'] +
                                       " Length: " + str(i['length']))

        string += "\nDescription: " + self.description
        return string

    def checkRegisterDataLength(self, module):
        """! @brief Controls that the combined data bits in entries does not 
        exceed data bits of module
        
        """
        if self.length > module:
            raise ModuleDataBitsExceeded(self.name, self.length, module)
