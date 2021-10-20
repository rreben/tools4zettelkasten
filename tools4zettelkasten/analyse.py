# analyse.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

import pprint as pp
from graphviz import Digraph
from . import handle_filenames as hf
from . import reorganize as ro


def show_tree_as_list(tree):
    pp.pprint(tree)


def show_graph_of_zettelkasten(
        list_of_filenames: list[str],
        list_of_links: list[ro.Link]):
    dot = Digraph(comment='Zettelkasten')

    # Nodes
    for filename in list_of_filenames:
        filename_components = hf.get_filename_components(filename=filename)
        print(filename_components[2], filename_components[1])
        dot.node(
            filename_components[2],
            filename_components[1],
            shape='box',
            style='rounded')

    # Edges
    for link in list_of_links:
        source_components = hf.get_filename_components(link.source)
        target_components = hf.get_filename_components(link.target)
        dot.edge(source_components[2], target_components[2])

    # Generate Output
    print(dot.source)
    dot.format = 'png'
    dot.render(view=True)
