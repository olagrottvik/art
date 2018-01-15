from utils import indentString
from utils import jsonParser
from utils import add_line_breaks
# from utils import compareJSON
# from utils import jsonToString
from exceptions import InvalidAddress
from exceptions import InvalidRegister

from bus import Bus

from register import Register

import json
from collections import OrderedDict


def test():
    #try:
        a = jsonParser('module2.json')
        axi = {'bus_type': 'axi', 'data_width': 32, 'addr_width': 32}
        bus = Bus(axi)
        mod = Module(a, bus)
        # print(mod)
        # print(mod.returnModulePkgVHDL())

        # print(mod.printJSON(False))
        # print(mod.printJSON(True))
        # print(jsonToString())
        # print(compareJSON(jsonToString(), mod.printJSON(False), True))
        # print(mod.returnRegisterPIFVHDL())
        # print(mod.returnBusPkgVHDL())
        # print(mod.returnModuleVHDL())

    #except Exception as e:
        #print(str(e))


class Module:
    """! @brief Managing module information


    """

    def __init__(self, mod, bus):
        """! @brief
        """
        self.bus = bus
        self.registers = []
        self.addresses = []
        self.name = mod['name']
        self.addrWidth = mod['addr_width']
        self.dataWidth = mod['data_width']
        self.description = add_line_breaks(mod['description'], 25)
        for reg in mod['register']:
            self.addRegister(reg)

    def addRegister(self, reg):
        if self.registerValid(reg):
            if "address" in reg:
                addr = int(reg['address'], 16)
                if self.isAddressFree(addr):
                    self.isAddressOutOfRange(addr)
                    self.addresses.append(addr)
                    self.registers.append(Register(reg, addr, self.dataWidth))
                else:
                    raise InvalidAddress(reg['name'], addr)
            else:
                addr = self.getNextAddress()
                self.addresses.append(addr)
                self.registers.append(Register(reg, addr, self.dataWidth))
        else:
            raise InvalidRegister(reg)

    def returnRegisterPIFVHDL(self):
        s = 'library ieee;\n'
        s += 'use ieee.std_logic_1164.all;\n'
        s += 'use ieee.numeric_std.all;\n'
        s += '\n'
        s += 'use work.' + self.name + '_pif_pkg.all;\n\n'
        s += 'entity ' + self.name + '_' + self.bus.bus_type + '_pif is\n\n'

        s += indentString('port (')

        par = ''
        par += '\n-- register record signals\n'
        par += 'axi_ro_regs : in  t_' + self.name + '_ro_regs := '
        par += 'c_' + self.name + '_ro_regs;\n'
        par += 'axi_rw_regs : out t_' + self.name + '_rw_regs := '
        par += 'c_' + self.name + '_rw_regs;\n'
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
        par += self.name + '_rw_regs := c_' + self.name + '_rw_regs;\n\n'

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

        s += indentString('p_awready : process(clk)\n')
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

        s += indentString('p_awaddr : process(clk)\n')
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

        s += indentString('p_wready : process(clk)\n')
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
        s += indentString('p_mm_select_write : process(clk)\n')
        s += indentString('begin\n')

        s += indentString('if rising_edge(clk) then\n', 2)
        
        s += indentString("if areset_n = '0' then\n", 3)

        # Assign default values
        s += indentString('\naxi_rw_regs_i <= c_', 4)
        s += self.name + '_rw_regs;\n\n'

        
        s += indentString("elsif (slv_reg_wren = '1') then\n", 3)
        s += '\n'
        s += indentString('case awaddr_i is\n\n', 4)

        # create a generator for looping through all rw regs
        gen = (reg for reg in self.registers if reg.mode == "rw")
        for reg in gen:
            s += indentString('when C_ADDR_', 5)
            s += reg.name.upper() + ' =>\n\n'
            par = ''
            if reg.sig_type == 'fields':

                for field in reg.fields:
                    par += 'axi_rw_regs_i.' + reg.name + '.' + field.name
                    par += ' <= wdata('
                    par += field.get_pos_vhdl()
                    par += ');\n'

            elif reg.sig_type == 'default':
                par += 'axi_rw_regs_i.' + reg.name + ' <= wdata;\n'
            elif reg.sig_type == 'slv':
                par += 'axi_rw_regs_i.' + reg.name + ' <= wdata('
                par += str(reg.length - 1) + ' downto 0);\n'
            elif reg.sig_type == 'sl':
                par += 'axi_rw_regs_i.' + reg.name + ' <= wdata(0);\n'

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
        s += indentString("araddr_i  <= (others => '0');\n", 4)
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
        s += indentString('case araddr_i is\n', 2)
        s += '\n'
        # Generator for looping through all "readable registers, rw&ro
        gen = [reg for reg in self.registers
               if reg.mode == "ro" or reg.mode == "rw"]
        for reg in gen:
            s += indentString('when C_ADDR_', 3)
            s += reg.name.upper() + ' =>\n\n'
            par = ''

            if reg.sig_type == 'fields':

                for field in reg.fields:
                    par += 'reg_data_out('
                    par += field.get_pos_vhdl()

                    if reg.mode == 'rw':
                        par += ') <= axi_rw_regs_i.'
                    elif reg.mode == 'ro':
                        par += ') <= axi_ro_regs.'
                    else:
                        raise Exception("Unknown error occurred")
                    par += reg.name + '.' + field.name + ';\n'

            elif reg.sig_type == 'default':
                par += 'reg_data_out <= '
                if reg.mode == 'rw':
                    par += 'axi_rw_regs_i.'
                elif reg.mode == 'ro':
                    par += 'axi_ro_regs.'
                else:
                    raise Exception("Unknown error occurred")
                par += reg.name + ';\n'

            elif reg.sig_type == 'slv':
                par += 'reg_data_out('
                par += str(reg.length - 1) + ' downto 0) <= '
                if reg.mode == 'rw':
                    par += 'axi_rw_regs_i.'
                elif reg.mode == 'ro':
                    par += 'axi_ro_regs.'
                else:
                    raise Exception("Unknown error occurred")
                par += reg.name + ';\n'

            elif reg.sig_type == 'sl':
                par += 'reg_data_out(0) <= '
                if reg.mode == 'rw':
                    par += 'axi_rw_regs_i.'
                elif reg.mode == 'ro':
                    par += 'axi_ro_regs.'
                else:
                    raise Exception("Unknown error occurred")
                par += reg.name + ';\n'

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
        s += indentString('end process p_output;\n')
        s += '\n'

        s += 'end behavior;'

        return s

    def returnModulePkgVHDL(self):
        s = 'library ieee;\n'
        s += 'use ieee.std_logic_1164.all;\n'
        s += 'use ieee.numeric_std.all;\n'
        s += '\n'
        s += "package " + self.name + "_pif_pkg is"
        s += "\n\n"

        par = ''
        par += "constant C_" + self.name.upper()
        par += "_ADDR_WIDTH : natural := " + str(self.addrWidth) + ";\n"
        par += "constant C_" + self.name.upper()
        par += "_DATA_WIDTH : natural := " + str(self.dataWidth) + ";\n"
        par += "\n"

        par += "subtype t_" + self.name + "_addr is "
        par += "std_logic_vector(C_" + self.name.upper() + "_ADDR_WIDTH-1 "
        par += "downto 0);\n"

        par += "subtype t_" + self.name + "_data is "
        par += "std_logic_vector(C_" + self.name.upper() + "_DATA_WIDTH-1 "
        par += "downto 0);\n"
        par += "\n"

        for reg in self.registers:
            par += "constant C_ADDR_" + reg.name.upper()
            par += " : t_" + self.name + "_addr := " + str(self.addrWidth)
            par += 'X"' + '%X' % reg.address + '";\n'
        par += '\n'
        s += indentString(par)

        s += indentString("-- RW Register Record Definitions\n\n")

        # Create all types for RW registers with records
        for reg in self.registers:
            if reg.mode == "rw" and reg.sig_type == "fields":
                s += indentString("type t_" + self.name + "_rw_")
                s += reg.name + " is record\n"

                for field in reg.fields:
                    s += indentString(field.name, 2) + " : "
                    if field.sig_type == "slv":
                        s += "std_logic_vector(" + str(field.length - 1)
                        s += " downto 0);\n"
                    elif field.sig_type == "sl":
                        s += "std_logic;\n"
                    else:
                        import ipdb; ipdb.set_trace()
                        raise RuntimeError(
                            "Something went wrong..." + field.sig_type)
                s += indentString("end record;\n\n")

        # The RW register record type
        s += indentString("type t_" + self.name + "_rw_regs is record\n")
        for reg in self.registers:
            if reg.mode == "rw":
                s += indentString(reg.name, 2) + " : "
                if reg.sig_type == "default" or (reg.sig_type == "slv" and reg.length == self.dataWidth):
                    s += "t_" + self.name + "_data;\n"
                elif reg.sig_type == "slv":
                    s += "std_logic_vector(" + \
                        str(reg.length - 1) + " downto 0);\n"
                elif reg.sig_type == "sl":
                    s += "std_logic;\n"
                elif reg.sig_type == "fields":
                    s += "t_" + self.name + "_rw_" + reg.name + ";\n"
                else:
                    import ipdb; ipdb.set_trace()
                    raise RuntimeError("Something went wrong...")
        s += indentString("end record;\n")
        s += "\n"

        s += indentString("-- RW Register Reset Value Constant\n\n")

        s += indentString("constant c_") + self.name + "_rw_regs : t_"
        s += self.name + "_rw_regs := (\n"
        gen = [reg for reg in self.registers if reg.mode == 'rw']

        for i, reg in enumerate(gen):
            par = ''
            par += reg.name + ' => '

            # RW default values must be declared
            if reg.sig_type == 'default' or reg.sig_type == 'slv':
                if reg.reset == "0x0":
                    par += "(others => '0')"
                else:
                    par += str(reg.length) + 'X"'
                    par += format(int(reg.reset, 16), 'X') + '"'

            elif reg.sig_type == 'fields':

                if len(reg.fields) > 1:
                    par += '(\n'
                else:
                    par += '('

                for j, field in enumerate(reg.fields):
                    if len(reg.fields) > 1:
                        par += indentString(field.name + ' => ')
                    else:
                        par += field.name + ' => '

                    if field.sig_type == 'slv':

                        if field.reset == "0x0":
                            par += "(others => '0')"
                        else:
                            par += str(field.length) + 'X"'
                            par += format(int(field.reset, 16), 'X') + '"'

                    elif field.sig_type == 'sl':
                        par += "'" + format(int(field.reset, 16), 'X') + "'"

                    if j < len(reg.fields) - 1:
                        par += ',\n'

                par += ')'

            elif reg.sig_type == 'sl':
                par += "'" + format(int(reg.reset, 16), 'X') + "'"

            if i < len(gen) - 1:
                par += ','
            else:
                par += ');'
            par += '\n'

            s += indentString(par, 2)
        s += '\n'

        s += indentString("-- RO Register Record Definitions\n\n")

        # Create all types for RO registers with records
        for reg in self.registers:
            if reg.mode == "ro" and reg.sig_type == "fields":
                s += indentString("type t_" + self.name + "_ro_")
                s += reg.name + " is record\n"

                for field in reg.fields:
                    s += indentString(field.name, 2) + " : "
                    if field.sig_type == "slv":
                        s += "std_logic_vector(" + str(field.length - 1)
                        s += " downto 0);\n"
                    elif field.sig_type == "sl":
                        s += "std_logic;\n"
                    else:
                        import ipdb; ipdb.set_trace()
                        raise RuntimeError("Something went wrong... WTF?")
                s += indentString("end record;\n\n")

        # The RO register record type
        s += indentString("type t_" + self.name + "_ro_regs is record\n")
        for reg in self.registers:
            if reg.mode == "ro":
                s += indentString(reg.name, 2) + " : "
                if reg.sig_type == "default" or (reg.sig_type == "slv" and reg.length == self.dataWidth):
                    s += "t_" + self.name + "_data;\n"
                elif reg.sig_type == "slv":
                    s += "std_logic_vector(" + \
                        str(reg.length - 1) + " downto 0);\n"
                elif reg.sig_type == "sl":
                    s += "std_logic;\n"
                elif reg.sig_type == "fields":
                    s += "t_" + self.name + "_ro_" + reg.name + ";\n"
                else:
                    import ipdb; ipdb.set_trace()
                    raise RuntimeError(
                        "Something went wrong... What now?" + reg.sig_type)
        s += indentString("end record;\n")
        s += "\n"

        s += indentString("-- RO Register Reset Value Constant\n\n")

        s += indentString("constant c_") + self.name + "_ro_regs : t_"
        s += self.name + "_ro_regs := (\n"
        gen = [reg for reg in self.registers if reg.mode == 'ro']

        for i, reg in enumerate(gen):
            par = ''
            par += reg.name + ' => '

            # RO default values must be declared
            if reg.sig_type == 'default' or reg.sig_type == 'slv':
                if reg.reset == "0x0":
                    par += "(others => '0')"
                else:
                    par += str(reg.length) + 'X"'
                    par += format(int(reg.reset, 16), 'X') + '"'

            elif reg.sig_type == 'fields':
                if len(reg.fields) > 1:
                    par += '(\n'
                else:
                    par += '('

                for j, field in enumerate(reg.fields):
                    if len(reg.fields) > 1:
                        par += indentString(field.name + ' => ')
                    else:
                        par += field.name + ' => '

                    if field.sig_type == 'slv':

                        if field.reset == "0x0":
                            par += "(others => '0')"
                        else:
                            par += str(field.length) + 'X"'
                            par += format(int(field.reset, 16), 'X') + '"'

                    elif field.sig_type == 'sl':
                        par += "'" + format(int(field.reset, 16), 'X') + "'"

                    if j < len(reg.fields) - 1:
                        par += ',\n'

                par += ')'

            elif reg.sig_type == 'sl':
                par += "'" + format(int(reg.reset, 16), 'X') + "'"

            else:
                import ipdb; ipdb.set_trace()

            if i < len(gen) - 1:
                par += ','
            else:
                par += ');'
            par += '\n'

            s += indentString(par, 2)
        s += '\n'

        s += "end package " + self.name + "_pif_pkg;"

        return s

    def returnModuleVHDL(self):
        s = 'library ieee;\n'
        s += 'use ieee.std_logic_1164.all;\n'
        s += 'use ieee.numeric_std.all;\n'
        s += '\n'
        s += 'use work.' + self.bus.bus_type + '_pkg.all;\n'
        s += 'use work.' + self.name + '_pif_pkg.all;\n'
        s += '\n'

        s += 'entity ' + self.name + ' is\n'
        s += '\n'
        s += indentString('port (\n')
        s += '\n'
        par = ''
        par += '-- ' + self.bus.bus_type.upper() + ' Bus Interface\n'
        par += self.bus.bus_type + '_clk      : in  std_logic;\n'
        par += self.bus.bus_type + '_areset_n : in  std_logic;\n'
        par += self.bus.bus_type + '_in       : in  t_' + \
            self.bus.bus_type + '_interconnect_to_slave;\n'
        par += self.bus.bus_type + '_out      : out t_' + \
            self.bus.bus_type + '_slave_to_interconnect\n'
        par += ');\n'
        s += indentString(par, 2)
        s += '\n'
        s += 'end entity ' + self.name + ';\n'
        s += '\n'

        s += 'architecture behavior of ' + self.name + ' is\n'
        s += '\n'

        s += indentString('signal ' + self.bus.bus_type + '_rw_regs : t_')
        s += self.name + '_rw_regs := c_' + self.name + '_rw_regs;\n'
        s += indentString('signal ' + self.bus.bus_type + '_ro_regs : t_')
        s += self.name + '_ro_regs := c_' + self.name + '_ro_regs;\n'

        s += '\n'

        s += 'begin\n'
        s += '\n'

        s += indentString('i_' + self.name + '_' + self.bus.bus_type + '_pif ')
        s += ': entity work.' + self.name + '_' + self.bus.bus_type + '_pif\n'
        s += indentString('port map (\n', 2)

        par = ''
        par += self.bus.bus_type + '_ro_regs => ' + self.bus.bus_type + '_ro_regs,\n'
        par += self.bus.bus_type + '_rw_regs => ' + self.bus.bus_type + '_rw_regs,\n'
        par += 'clk         => ' + self.bus.bus_type + '_clk,\n'
        par += 'areset_n    => ' + self.bus.bus_type + '_areset_n,\n'
        par += 'awaddr      => ' + self.bus.bus_type + '_in.awaddr(C_'
        par += self.name.upper() + '_ADDR_WIDTH-1 downto 0),\n'
        par += 'awvalid     => ' + self.bus.bus_type + '_in.awvalid,\n'
        par += 'awready     => ' + self.bus.bus_type + '_out.awready,\n'
        par += 'wdata       => ' + self.bus.bus_type + '_in.wdata(C_'
        par += self.name.upper() + '_DATA_WIDTH-1 downto 0),\n'
        par += 'wvalid      => ' + self.bus.bus_type + '_in.wvalid,\n'
        par += 'wready      => ' + self.bus.bus_type + '_out.wready,\n'
        par += 'bresp       => ' + self.bus.bus_type + '_out.bresp,\n'
        par += 'bvalid      => ' + self.bus.bus_type + '_out.bvalid,\n'
        par += 'bready      => ' + self.bus.bus_type + '_in.bready,\n'
        par += 'araddr      => ' + self.bus.bus_type + '_in.araddr(C_'
        par += self.name.upper() + '_ADDR_WIDTH-1 downto 0),\n'
        par += 'arvalid     => ' + self.bus.bus_type + '_in.arvalid,\n'
        par += 'arready     => ' + self.bus.bus_type + '_out.arready,\n'
        par += 'rdata       => ' + self.bus.bus_type + '_out.rdata(C_'
        par += self.name.upper() + '_DATA_WIDTH-1 downto 0),\n'
        par += 'rresp       => ' + self.bus.bus_type + '_out.rresp,\n'
        par += 'rvalid      => ' + self.bus.bus_type + '_out.rvalid,\n'
        par += 'rready      => ' + self.bus.bus_type + '_in.rready\n'
        par += ');\n'
        s += indentString(par, 3)

        # If bus data width is larger than module data width, set the unused bits to zero
        if self.bus.data_width > self.dataWidth:
            s += indentString('-- Set unused bus data bits to zero\n')
            s += indentString(self.bus.bus_type +
                              '_out.rdata(C_' + self.bus.bus_type.upper())
            s += '_DATA_WIDTH-1 downto C_' + self.name.upper() + '_DATA_WIDTH)'
            s += " <= (others => '0');\n"

        s += '\n'
        s += 'end architecture behavior;'

        return s

    def printJSON(self, includeAddress=False):
        """! @brief Returns JSON string

        """
        dic = OrderedDict()

        dic["name"] = self.name

        dic["bus"] = self.bus.return_JSON()
        
        dic["addr_width"] = self.addrWidth
        dic["data_width"] = self.dataWidth

        dic["register"] = []

        for i, reg in enumerate(self.registers):
            regDic = OrderedDict()

            regDic["name"] = reg.name
            regDic["mode"] = reg.mode
            regDic["type"] = reg.sig_type

            if includeAddress:
                regDic["address"] = str(hex(reg.address))

            if (reg.sig_type != "default" and reg.sig_type != "fields" and
                    reg.sig_type != "sl"):
                regDic["length"] = reg.length

            if reg.sig_type != "fields":
                regDic["reset"] = reg.reset

            if reg.sig_type == "fields" and len(reg.fields) > 0:
                regDic["fields"] = []
                for field in reg.fields:
                    regDic["fields"].append(field.returnDic())

            regDic["description"] = reg.description

            dic["register"].append(regDic)

        dic["description"] = self.description
        return json.dumps(dic, indent=4)

    def getNextAddress(self):
        """! @brief Will get the next address based on the byte-addressed scheme

        """
        addr = 0
        foundAddr = False
        while (not foundAddr):
            self.isAddressOutOfRange(addr)
            if self.isAddressFree(addr):
                self.addresses.append(addr)
                return addr
            else:
                # force integer division to prevent float
                addr += self.dataWidth // 8

    def isAddressOutOfRange(self, addr):
        if addr > pow(2, self.addrWidth) - 1:
            raise RuntimeError("Address " + hex(addr) +
                               " is definetely out of range...")
        return True

    def isAddressFree(self, addr):
        for address in self.addresses:
            if address == addr:
                return False
        # If loop completes without matching addresses
        return True

    def updateAddresses(self):
        self.addresses = []
        for reg in self.registers:
            addr = self.getNextAddress()
            self.addresses.append(addr)
            reg.address = addr
            

    def registerValid(self, reg):
        if set(("name", "mode", "type", "description")).issubset(reg):
            return True
        elif set(("name", "mode", "fields", "description")).issubset(reg):
            return True
        else:
            return False

    def __str__(self):
        string = "Name: " + self.name + "\n"
        string += "Address width: " + str(self.addrWidth) + "\n"
        string += "Data width: " + str(self.dataWidth) + "\n"
        string += "Description: " + self.description + "\n\n"
        string += "Registers: \n"
        for i, reg in enumerate(self.registers):
            string += indentString(str(reg), 1)
        return string


