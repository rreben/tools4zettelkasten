# analyse.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

import pprint as pp
from graphviz import Digraph
from . import handle_filenames as hf
from . import reorganize as ro
from . import settings as st
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
        title_of_node = (
            note.ordering.replace('_', ' ') +
            ' ' + note.base_filename.replace("_", " "))
        dot.node(
            note.id,
            fill(title_of_node, width=30),
            shape='box',
            style='rounded')

    # Edges
    for link in list_of_links:
        source_note = hf.create_Note(link.source)
        target_note = hf.create_Note(link.target)
        if link.description == st.DIRECT_DAUGHTER_ZETTEL:
            dot.edge(source_note.id, target_note.id, color='blue')
        elif link.description == st.DIRECT_SISTER_ZETTEL:
            dot.edge(source_note.id, target_note.id)
        else:
            dot.edge(source_note.id, target_note.id, color='red')

    # Generate Output
    print(dot.source)
    dot.format = 'png'
    dot.render(view=True)
