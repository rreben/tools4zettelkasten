Layout of the development project
=================================

The project layout follows a proposal from Martin Heinz [1].

**.vscode/** contains a json file that stores some settings for Visual Studio
Code

**ArbeitMitDemZettelkasten.code-workspace** has some specific data for the
Workspace in VSCode.

**docs/** contains the website with the project documentation on github pages.
You have to change to the ``gh-pages`` branch in order to view or change these
files.

**docs_source/** contains all the source files of the documentation, to create
the docs on gh-pages. I could not put these files in the docs folder, because
this would collide with the structure that gh-pages are expecting. In order to
use gh-pages, we have to provide an index.html file in the docs directory
(together with all the other html files and ressources).

**experiments/** is a folder to try new libraries and python recipes. These
experiments have a temporary value and are not part of the project.

**flask_frontend/** Contains all the templates, CSS files and static content
that flask needs to generate the view of the Zettelkasten in the Browser

**tests/** contains everything to test the project, especially the python
unittests

**zettelkasten_tools/** contains the source code of the tools and the backend
of the flask

**.gitignore** holds the configuration which artefacts will NOT be put under
version control

**LICENSE** is the file with the project license (MIT-license)

**README.rst** is the file that is first shown on the repo on Github.



[1]: Heinz, Martin, „Ultimate Setup for Your Next Python Project“, Martin Heinz
Personal Website & Blog. https://martinheinz.dev/blog/14
