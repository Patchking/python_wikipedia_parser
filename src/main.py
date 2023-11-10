from ex00.cache_wiki import Cache_wiki
from ex02.render_graph import Render_graph
import os
import json


def main():
    wiki = Cache_wiki(max_discovered_links=1500).getlist()
    with open("wiki.json", "w") as f:
        json.dump(wiki, f)
    render = Render_graph(os.getcwd() + "/wiki.json")
    render.save_as_html(os.getcwd() + "/graph.html")
    # render.save_as_image(os.getcwd() + "/graph.png")

if __name__ == "__main__":
    main()