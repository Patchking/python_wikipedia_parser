import logging
from urllib.parse import urlparse, unquote
import requests
from requests.adapters import SSLError
from argparse import ArgumentParser
from bs4 import BeautifulSoup as bs
import json


class Cache_wiki():
    discovered_links = 0
    known_nodes = dict()
    parsed_nodes = set()

    def __init__(self, initial_link = "https://en.wikipedia.org/wiki/Erd%C5%91s_number",
                 max_depth = 3, max_discovered_links = 1000) -> list:

        self.initial_link = unquote(initial_link)
        self.max_depth = max_depth
        self.max_discovered_links = max_discovered_links

    def getlist(self):
        """parse and get list themself. The only one important function"""
        # Starting parsing wikipeadia
        ## Parsing initial page 
        logging.info(f"""\n\\\\\\\\\\\\\\\\\\\\Currently we are on depth 0\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n""")
        self.known_nodes[self.initial_link] = {"forward": [], "backward": []}
        set_of_pages_to_parse = self.parse_page(self.initial_link)
        logging.info(f"page {unquote(self.initial_link)} visited. 1/1")

        ## Going through all parsed links and discover even more links!
        try:
            for i in range(self.max_depth):
                logging.info(f"""\n\\\\\\\\\\\\\\\\\\\\Currently we are on depth {i + 1}\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n""")
                cur_set_of_pages_to_parse = set()
                cur_pages_count = len(set_of_pages_to_parse)
                cur_page_number = 0
                for link in set_of_pages_to_parse:
                    cur_page_number += 1
                    logging.info(f"page {unquote(link)} visited. {cur_page_number}/{cur_pages_count}")
                    logging.info(f"Total {self.discovered_links} explored")
                    got_pages = self.parse_page(link)
                    cur_set_of_pages_to_parse |= got_pages
                    if self.discovered_links >= self.max_discovered_links:
                        raise Exception
                set_of_pages_to_parse = cur_set_of_pages_to_parse
        except Exception as e:
            logging.info(f"Parsing stopped because limit of known pages was hit ({self.max_discovered_links})")

        listocheck = dict(filter(lambda a: len(a[1]["backward"]) >= 2 or len(a[1]["forward"]) > 0, self.known_nodes.items()))
        # listocheck.sort(key=lambda a: a[1]["counter"], reverse=True)
        # for i in listocheck:
        #     i = unquote(i[0])
        return listocheck

    def reconstructing_link(self, href, link) -> str:
            """Some links in wikipedia has relative links. To fix this we use this function.
            its trying to reconstuct first link using second one. On practice this function 
            will substitute the missing parts of the first link from the second link"""
            if not href:
                return ""
            href_parse = urlparse(href)
            link_parse = urlparse(link)

            netloc = None
            path = None
            if href_parse.netloc:
                netloc = href_parse.netloc
            else:
                netloc = link_parse.netloc
            if href_parse.path:
                path = href_parse.path
            else:
                path = link_parse.path
            
            return "https://" + netloc + path

    def parse_page(self, link: str) -> set:
        """Parse pages and find new links. All found links adds to self.known_nodes"""
        def add_direct_connection(str1, str2):
            self.known_nodes[str1]["forward"].append(str2)
            self.known_nodes[str2]["backward"].append(str1)

        # If page already parsed return empty set
        if link in self.parsed_nodes:
            return set()

        self.parsed_nodes.add(link)
        page = ""
        try:
            page = requests.get(link)
        except SSLError as e:
            logging.error(f"Link {link} can't be reached")
            return set()

        soup = bs(page.text, "html.parser")
        
        out = set()
        for a_tag in soup.find_all("a"):
            href = a_tag.get("href")
            # Filtering links that doesnt refer to wikipedia pages
            if href and href.find("/wiki/") != -1 and href.find(":") == -1:
                href = unquote(href)
                href = self.reconstructing_link(href, link)
                # if link has meet on this page before skip link and going to next
                if href in out or href == link:
                    continue
                if href in self.known_nodes:
                    pass
                else:
                    self.known_nodes[href] = {"forward": [], "backward": []}
                    self.discovered_links += 1
                add_direct_connection(link, href)
                out.add(href)
                if self.discovered_links >= self.max_discovered_links:
                    return out
        return out
    

def main():
    parser = ArgumentParser()
    parser.add_argument("-p", "--page", help="Require url for wiki page", type=str)
    parser.add_argument("-d", "--max-depth" ,help="Require depth of parsing", type=int)
    parser.add_argument("-l", "--max-page-stored", help="Require max links count to be saved in json", type=int)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    initial_link = "https://en.wikipedia.org/wiki/Erd%C5%91s_number"
    max_depth, max_discovered_links = 3, 1000
    if args.page:
        initial_link = args.page
    if args.max_depth:
        if args.max_depth < 0:
            max_depth = 0
        else:
            max_depth = args.max_depth
    if args.max_page_stored:
        if args.max_page_stored > 0:
            max_discovered_links = args.max_page_stored
    wiki = Cache_wiki(initial_link, max_depth, max_discovered_links).getlist()
    with open("wiki.json", "w") as f:
        json.dump(wiki, f)

if __name__ == "__main__":
    main()