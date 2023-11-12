import json
import logging
from argparse import ArgumentParser

class Shortest_path:
    
    def __init__(self, json_file_name, path_from: str, path_to: str,
                 both_directed: bool = False, evocation_flag: bool = False):
        with open(json_file_name, "r") as f:
            self.json_file = json.load(f)
        self.path_from = path_from
        self.path_to = path_to
        self.both_directed = both_directed
        self.evocation_flag = evocation_flag

    def get_path(self) -> list:
        self.sum_map = dict()

        def calculate_dict():
            curweight = 0
            curset = {self.path_from}
            self.sum_map[self.path_from] = 0
            while curset:
                newset = set()
                curweight += 1
                for rec in curset:
                    newset.update(filter(lambda a: a not in self.sum_map, near_nodes(rec)))
                self.sum_map.update(dict.fromkeys(newset, curweight))
                if self.path_to in newset:
                    return True
                curset = newset
            return False
                

        def get_path_from_dict():
            # Check if path_to in sum_map. If not means there's no path, return empty sequence
            ## Outdated. This condition checks in calculate dict
            if self.path_to not in self.sum_map:
                return []

            # Choose would we pick forward links to search path or not
            near_nodes = None
            if self.both_directed:
                near_nodes = lambda a: self.json_file[a]["forward"] + self.json_file[a]["backward"]
            else:
                near_nodes = lambda a: self.json_file[a]["backward"]

            out = []
            out.append(self.path_to)
            cur_weight = self.sum_map[self.path_to]
            curnode = self.path_to
            while curnode != self.path_from:
                for i in near_nodes(curnode):
                    if i in self.sum_map and self.sum_map[i] == cur_weight - 1:
                        curnode = i
                        cur_weight -= 1
                        break
                out.append(curnode)
            return out
        
        self.near_nodes = None
        if self.both_directed:
            near_nodes = lambda a: self.json_file[a]["forward"] + self.json_file[a]["backward"]
        else:
            near_nodes = lambda a: self.json_file[a]["forward"]

        if not calculate_dict():
            return []
        out = get_path_from_dict()
        out.reverse()
        return out



            

        

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--file", help="File where from we loads", type=str)
    parser.add_argument("-f", "--from", help="Start page", type=str, required=True, dest="ffrom")
    parser.add_argument("-t", "--to" ,help="Finish page", type=str, required=True)
    parser.add_argument("-n", "--non-directed", help="Specify if graph is bidirected or not", action="store_true")
    parser.add_argument("-v", "--verbose", help="Is print full path", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    init_file = "wiki.json"
    both_directed = False
    evocation_flag = False
    from_page = ""
    to_page = ""

    # print(dir(args))
    if args.file:
        init_file = args.file
    if args.ffrom and args.to:
        from_page = args.ffrom
        to_page = args.to

    if args.non_directed:
        both_directed = True
    if args.verbose:
        evocation_flag = True

    sp = Shortest_path(init_file, from_page, to_page, both_directed, evocation_flag).get_path()
    if sp:
        if evocation_flag:
            for i in range(len(sp)):
                sp[i] = sp[i][sp[i].find("/wiki/") + 6:].replace("_", " ")
            for i in sp[:-1]:
                print(f"'{i}' -> ", end="")
            print(f"'{sp[-1]}'")
        print(len(sp))
    else:
        if evocation_flag:
            print("There's is no route")
        print(-1)
    
