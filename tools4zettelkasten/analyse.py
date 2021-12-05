# analyse.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

import pprint as pp
from graphviz import Digraph
from . import handle_filenames as hf
from . import reorganize as ro
from textwrap import fill


def show_tree_as_list(tree):
    pp.pprint(tree)


def show_graph_of_zettelkasten(
        list_of_filenames: list[str],
        list_of_links: list[ro.Link]):
    dot = Digraph(comment='Zettelkasten')

    # Nodes
    for filename in list_of_filenames:
        note = hf.create_Note(filename)
        dot.node(
            note.id,
            fill(note.base_filename.replace("_", " "), width=30),
            shape='box',
            style='rounded')

    # Edges
    for link in list_of_links:
        source_note = hf.create_Note(link.source)
        target_note = hf.create_Note(link.target)
        dot.edge(source_note.id, target_note.id)

    # Generate Output
    print(dot.source)
    dot.format = 'png'
    dot.render(view=True)
