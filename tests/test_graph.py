import os
from importlib.machinery import SourceFileLoader
from unittest import TestCase
from System.Graph import Graph

TESTS_DIR = os.path.dirname(__file__)


class TestGraph(TestCase):
    graph_config = os.path.join(TESTS_DIR, "fixtures", "cnv.config")
    cycle_config = os.path.join(TESTS_DIR, "fixtures", "cycle.config")

    def setUp(self):
        cc = SourceFileLoader(
            "CloudConductor",
            os.path.join(os.path.dirname(TESTS_DIR), "CloudConductor")
        ).load_module()
        cc.configure_import_paths()

    def test_graph_to_text(self):
        g = Graph(self.graph_config)
        # Convert graph to text
        text = str(g)
        # Convert text to list of lines and remove blank lines
        out_lines = [line for line in text.split("\n") if line.strip()]
        with open(self.graph_config, "r") as config_file:
            # Read lines from config file and remove blank lines
            in_lines = [line for line in config_file if line.strip()]
        # Compare lines from graph object and lines from config file
        # The number of line from Graph object should be greater or equal
        # As converting from Graph object include default settings.
        self.assertGreaterEqual(len(out_lines), len(in_lines))
        sorted_lines = [sorted("".join(line.split())) for line in out_lines]
        for line in in_lines:
            sorted_line = sorted("".join(line.split()))
            self.assertIn(sorted_line, sorted_lines, "\n\n\"%s\" not found str(graph):\n%s" % (line, "\n".join(out_lines)))

    def test_graph_with_cycle(self):
        """Tests initializing a Graph object with cycle in the graph config."""
        # When runtime is not set, initializing graph with cycle will raise IOError
        with self.assertRaises(IOError):
            g = Graph(self.cycle_config)