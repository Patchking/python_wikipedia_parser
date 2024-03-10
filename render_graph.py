import json
import networkx as nx
import matplotlib.pyplot as plt
import logging
from argparse import ArgumentParser
from pyvis.network import Network

class Render_graph:
    json_file = None
    nx_graph = None

    def math_function(self, x):
         return 10 + x * 2

    def __init__(self, json_file):
        self.json_file = json_file

        with open(json_file, "r") as f:
            self.json_file = json.load(f)

        self.nx_graph = nx.Graph()

        for rec in self.json_file:
            backward_references = len(self.json_file[rec]["backward"])
            self.nx_graph.add_node(rec, size=self.math_function(backward_references))

        for rec in self.json_file:
            for cur_forward in self.json_file[rec]["forward"]:
                if self.nx_graph.has_node(cur_forward):
                    self.nx_graph.add_edge(rec, cur_forward)
        
        print("Graph size is", self.nx_graph.size())

    def save_as_image(self, filename):
        nx.draw(self.nx_graph, with_labels=False, node_size=1)
        plt.savefig(filename, dpi=1500, facecolor="y", orientation="portrait",  transparent=True, bbox_inches="tight", pad_inches=0)
    
    def save_as_html(self, filename):
        nt = Network("100vh", "100%", notebook=True)
        nt.from_nx(self.nx_graph)
        nt.set_options("""
        const options = {
        "physics": {
            "barnesHut": {
            "centralGravity": 0.4,
            "springLength": 250,
            "springConstant": 0.01,
            "damping": 0.1
            },
            "maxVelocity": 4,
            "minVelocity": 0.75
        }
        }           """)
        nt.show(filename)
        

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-s", "--source", help="Enter source file", type=str)
    parser.add_argument("--image" ,help="Enter out image name", type=str)
    parser.add_argument("--html", help="Enter out html name", type=str)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    source = "wiki.json"
    image = ""
    html = ""

    if args.source:
        source = args.source
    if args.image:
        image = args.image
    if args.html:
        html = args.html
    if not image and not html:
        print("At least --image or --html must be specifyed! Abort")
        exit()

    graph = Render_graph(source)
    if image:
        graph.save_as_image(image)
    if html:
        graph.save_as_html(html)