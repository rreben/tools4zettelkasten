# analyse.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

from graphviz import Digraph
from . import handle_filenames as hf


def show_graph_of_zettelkasten(list_of_filenames, list_of_links):
    dot = Digraph(comment='Zettelkasten')

    # Goal
    for filename in list_of_filenames:
        filename_components = hf.get_filename_components(filename=filename)
        print(filename_components[2], filename_components[1])
        dot.node(
            filename_components[2],
            filename_components[1],
            shape='box',
            style='rounded')

    for link in list_of_links:
        source_components = hf.get_filename_components(link.source)
        target_components = hf.get_filename_components(link.target)
        dot.edge(source_components[2], target_components[2])
    # Edges
    # dot.edge('0', '1')
    # dot.edge('0', '2')
    # dot.edge('1', '1.1')
    # dot.edge('2', '2.1')

    # Generate Output
    print(dot.source)
    dot.format = 'png'
    dot.render(view=True)
