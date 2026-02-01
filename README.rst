==================
tools4zettelkasten
==================

This project provides tools to setup a digital Zettelkasten System based on
simple interlinked markdown files. It supports managing an alphanumeric
ordering of your Zettel-files (reordering of "Folgezettel") and analyse and
display the structure of your Zettelkasten.

.. start_marker_what_is_a_zettelkasten_do_not_remove

What is a Zettelkasten?
=======================
A Zettelkasten is a structured collection of notes. The Zettelkasten is a tool
to approach complex ideas and concepts. It serves to support and structure
one's thinking about essential topics. Thus the note box can help to formulate
and publish own thoughts.

Zettel is the German word for a small piece of paper, and Kasten means box. So
a Zettelkasten is a box full of small pieces of paper. Therefore a Zettelkasten
is often referred to as a slip box.

The idea of a slip box goes back to Niklas Luhmann (1927-1998) [1]. An
exceptionally productive sociologist measured by his publications. Söhnke
Ahrens explained Luhmann's approach in his book “Das Zettelkasten-Prinzip” [2]
and contributed significantly to popularizing the concept. The book was
translated into English under “How to take smart notes.“ Through this title,
one can find numerous explanations of the methodology on the Internet.

How to set up a digital Zettelkasten?
=====================================

To use the system, you don't need any special software. Any Editor (e.g.
VSCode, Atom, Vim, etc.) capable of editing Markdown can be used.

Every slip (zettel)  is a simple markdown file. These markdown files might
contain images or mathematical formulas.

Using the Zettelkasten is 95% about how to write notes and how to name them.
Just 5% is about organizing these notes with ``tools4zettelkasten``. Please
refer to my "step by step guide" on how to setup a Zettelkasten.
https://www.mycelium-of-knowledge.org/step-by-step-instructions-for-setup-and-use-of-the-zettelkasten/

.. end_marker_what_is_a_zettelkasten_do_not_remove

.. start_marker_how_to_use_tools4zettelkasten_do_not_remove

How to use ``tools4zettelkasten``?
==================================

Start ``tools4zettelkasten``
----------------------------
The Zettelkasten tools provide a set of tools to manipulate the markdown files
to significantly improve the handling of a big number of zettel / markdown
files. With Zettelkasten you can effortlessly change the hierachy as well as
the interlinks of your Zettelkasten.

.. code-block:: sh

    python -m tools4zettelkasten

Will open a help page with all available commands. You can get further
information about a command (e.g. for the command ``stage``) by typing:

.. code-block:: sh

    python -m tools4zettelkasten stage --help

The Zettelkasten shows the zettel files as html and provides a simple
webeserver to do so. It uses flask, a markdown to html converter and bootstrap
to do so in a responsive GUI.

Features of ``tools4zettelkasten``
----------------------------------

``tools4zettelkasten`` provides a set of tools to manipulate the markdown files
to significantly improve the handling of a big number of zettel / markdown
files. With Zettelkasten you can effortlessly change the hierachy as well as
the interlinks of your Zettelkasten.

With the ``stage`` command you can rename all Zettel / Markdown files in the
input directory, so that they conform to the naming convention. (have a look at
my
https://www.mycelium-of-knowledge.org/step-by-step-instructions-for-setup-and-use-of-the-zettelkasten/
for more information on how and why (!) you should name the files accodring to
the naming convention). The name will be formed from the title in the markdown
file (e.g. ``title`` in ``# title``).

With the ``reorganize`` command you can change the alphanumeric numbering of
the Zettel / Markdown files in your Zettelkasten directory.

Suppose you have a Zettelkasten with the following files:

.. code-block:: sh

    ...
    01_12_Quality_of_notes_eccb21483.md
    01_12a_How_to_integrate_notes_into_the_note_box_e0d27e3ad.md
    01_12a_1_Integration_of_fleeting_notes_97a19382a.md
    01_12a_2_Integration_of_literature_notes_ec83f31a2.md
    01_12b_Working_with_alphanumeric_Ordering_en036a6bd.md
    01_13_How_to_revisit_notes_a161a7e7c.md
    ...

The after using the ``reorganize`` command, the files will be renamed as
follows:

.. code-block:: sh

    ...
    01_12_Quality_of_notes_eccb21483.md
    01_13_How_to_integrate_notes_into_the_fleeting_box_e0d27e3ad.md
    01_13_1_Integration_of_fleeting_notes_97a19382a.md
    01_13_2_Integration_of_literature_notes_ec83f31a2.md
    01_14_Working_with_alphanumeric_Ordering_en036a6bd.md
    01_15_How_to_revisit_notes_a161a7e7c.md
    ...

This way you will always have a clean alphanumeric numbering of the Zettel /
Markdown files.

.. end_marker_how_to_use_tools4zettelkasten_do_not_remove

.. start_marker_how_to_set_up_tools4zettelkasten_do_not_remove

How to setup the tools4zettelkasten?
====================================

Right now ``tools4zettelkasten`` is still in alpha mode. You need to download
or clone the repo. You can start the scripts via the command line:

.. code-block:: sh

    python -m tools4zettelkasten

You will have to install the missing dependencies via pip. So you may want to
use a virtual environment. See https://rreben.github.io/tools4zettelkasten/ for
further information.

I am planning to publish ``tools4zettelkasten`` as a package on PyPI. So you
can install it via pip.

First of all you have to tell ``tools4zettelkasten`` where to find the
directory of your zettelkasten.

You could use the following directory structure: We store the Markdown files in
a simple folder with the following directory structure:

.. code-block:: sh

    ├── input/
    │   └── images/
    └── mycelium/
        └── images/

Any other directory structure is possible, but you need to have the images in
the ``images/`` directory, if you want to use the flask server.

First of all use the ``settings`` command to show the current configuration:

.. code-block:: sh

    python -m tools4zettelkasten settings

In MacOS you can use the following command to set the environment variables:

.. code-block:: sh

    export ZETTELKASTEN=/Users/me/Documents/zettelkasten/mycelium/
    export ZETTELKASTEN_INPUT=/Users/me/Documents/zettelkasten/input/

Where ``/Users/me/Documents/zettelkasten/mycelium/``  is the directory of your
zettelkasten and ``/Users/me/Documents/zettelkasten/input/`` is the directory
of your input folder.

.. end_marker_how_to_set_up_tools4zettelkasten_do_not_remove

How to use the tools4zettelkasten with Docker?
==============================================

A docker image is can be build with the following command:

.. code-block:: sh

    docker build -t tools4zettelkasten .

The docker image can be started with the following command:

.. code-block:: sh

    docker run -it -v $(pwd)/../zettelkasten:/app/zettelkasten --rm tools4zettelkasten bash

You should then see the container in Docker Desktop. You can then use the
command line to run the tools4zettelkasten. in the terminal.

.. code-block:: sh

    python -m tools4zettelkasten stage

The flask server can be started with the following command:

.. code-block:: sh

    run -it --rm -p 5000:5000 -v $(pwd)/../zettelkasten:/app/zettelkasten tools4zettelkasten

The flask server can be accessed via http://localhost:5000.




How to contribute?
==================

See https://rreben.github.io/tools4zettelkasten/ for more information on how to
build and use this project.

See https://www.mycelium-of-knowledge.org/ for a discussion of the project.

The documentation can also be found at
https://tools4zettelkasten.readthedocs.io/en/latest/
