import unittest
import logging.config
from uart.utils import json_parser
import uart.module as mod
import uart.bus as bus
import uart.settings as set
import uart.testbench as tb


class TestTestbench(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s', level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

        # Load the example JSON file
        json_file = "example/example_module.json"
        json = json_parser(json_file)
        self.set = set.Settings(json_file, json['settings'])
        self.bus = bus.Bus(json['bus'])
        self.mod = mod.Module(json['module'], self.bus, self.set)

    def test_scripts(self):
        self.logger.info("Testing TB Script generation...")
        with open('example/example_module_manual/scripts/simulate_axi_pif.do') as script_file:
            script_string = script_file.read()
        with open('example/example_module_manual/scripts/component_list.txt') as component_file:
            component_string = component_file.read()

        testbench = tb.Testbench(self.mod, self.bus, self.set)

        self.assertEqual(testbench.return_tcl_script(), script_string, ".tcl script must match manual file")
        self.assertEqual(testbench.return_uvvm_component_list(), component_string, ".txt file must match manual file")

    def test_tb(self):
        self.logger.info("Testing TB Sequencer generation...")
        with open('example/example_module_manual/tb/example_module_axi_pif_tb.vhd') as tb_file:
            tb_string = tb_file.read()

        testbench = tb.Testbench(self.mod, self.bus, self.set)

        self.assertEqual(testbench.return_vhdl_tb(), tb_string, ".vhd TB must match manual file")


if __name__ == '__main__':
    unittest.main()
