import os
from importlib.machinery import SourceFileLoader
from unittest import TestCase
from System.Graph import Graph, Task

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
            Graph(self.cycle_config)

    def test_add_and_remove_task(self):
        g = Graph(self.graph_config)
        # Adding a duplicate task should raise a RuntimeError
        task = Task("split_sample", **dict(
            module="SampleSplitter",
            submodule="SampleSplitter",
            final_output=None,
        ))
        with self.assertRaises(RuntimeError):
            g.add_task(task)

        # TODO: Adding a new task does not check if input from is valid.

        # Add a new task
        task_id = "test_task"
        task = Task(task_id, **dict(
            module="SampleSplitter",
            submodule="SampleSplitter",
            final_output=None,
            input_from=["plot_denoise_cr", "call_crs"]
        ))
        g.add_task(task)
        added_task = g.tasks.get(task_id)
        self.assertEqual(added_task, task)
        # TODO: Graph.adj_list is not updated when using add_task()

        # Remove a task that does not exist will raise a RuntimeError
        with self.assertRaises(RuntimeError):
            g.remove_task("ABC")
        # Remove a task
        # The task_id should be removed from g.tasks and g.adj_list
        remove_task_id = "model_segments"
        g.remove_task(remove_task_id)
        self.assertNotIn(remove_task_id, g.tasks.keys())
        self.assertNotIn(remove_task_id, g.adj_list.keys())
        for adj_list in g.adj_list.values():
            self.assertNotIn(remove_task_id, adj_list)

    def test_get_parents_and_children(self):
        g = Graph(self.graph_config)
        # Parents
        # Split_sample has no parent
        self.assertEqual(g.get_parents("split_sample"), [])
        # Node with one parent
        parents = g.get_parents("collect_read_counts")
        self.assertEqual(["split_sample"], parents)
        # Node does not exist
        with self.assertRaises(RuntimeError):
            g.get_parents("ABC")

        # Children
        # Node with one child
        children = g.get_children("collect_read_counts")
        self.assertEqual(["denoise_read_counts"], children)
        # Node with two children
        children = g.get_children("denoise_read_counts")
        self.assertEqual(len(children), 2)
        self.assertIn("plot_denoise_cr", children)
        self.assertIn("model_segments", children)
        # Node with on child
        children = g.get_children("plot_denoise_cr")
        self.assertEqual(len(children), 0)
        # Node does not exist
        with self.assertRaises(RuntimeError):
            g.get_children("ABC")