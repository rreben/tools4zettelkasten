# analyse.py
# Copyright (c) 2021 Dr. Rupert Rebentisch
# Licensed under the MIT license

import pprint as pp
from graphviz import Digraph
from . import handle_filenames as hf
from . import reorganize as ro
from . import settings as st
from . import flask_views as fv
from .persistency import PersistencyManager
from textwrap import fill


def create_graph_input(persistency_manager: PersistencyManager):
    persistencyManager = PersistencyManager(
        st.ZETTELKASTEN)
    list_of_filenames = persistencyManager.get_list_of_filenames()
    list_of_explicit_links = ro.get_list_of_links(persistencyManager)
    tokenized_list = ro.generate_tokenized_list(
        persistencyManager.get_list_of_filenames())
    tree = ro.generate_tree(tokenized_list)
    list_of_structure_links = ro.get_hierarchy_links(tree)
    list_of_links = list_of_structure_links + list_of_explicit_links
    return list_of_filenames, list_of_links, tree


def show_tree_as_list(tree):
    pp.pprint(tree)


def create_graph_of_zettelkasten(
        list_of_filenames: list[str],
        list_of_links: list[ro.Link],
        url_in_nodes: bool) -> Digraph:
    dot = Digraph(comment='Zettelkasten')

    # Nodes
    for filename in list_of_filenames:
        note = hf.create_Note(filename)
        title_of_node = (
            note.ordering.replace('_', ' ') +
            ' ' + note.base_filename.replace("_", " "))
        if url_in_nodes:
            dot.node(
                note.id,
                fill(title_of_node, width=30),
                shape='box',
                URL=fv.url_for_file(filename),
                style='rounded')
        else:
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

    return dot


def show_graph_of_zettelkasten(dot: Digraph):
    # Generate Output
    print(dot.source)
    dot.format = 'png'
    dot.render(view=True)
