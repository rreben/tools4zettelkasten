Generate the docs
=================

Create and edit the source files for the docs
---------------------------------------------
1. To generate the docs navigate to the docs_source folder 
2. Edit the rst files in the master branch as needed
3. You might want to edit the release number in ``conf.py``
4. Use ``make html`` to generate the documentation
5. Check the generated documentation by openening ``docs/index.html`` in a browser
6. Use ``make clear`` to remove the generated html documentation
7. Comit and push the doc source files.

Publish the documentation
-------------------------

I use Github pages to host the documentation. The configuration can be done in the projects / repo settings under pages.

Github pages expects the html files in the docs directory, with an ``index.html`` file as root. The Github pages are drawn from a special ``gh-pages`` branch (so there is now interference with day to day.

There should be a ``.nojkyll`` file in the docs folder in order to stop the templating engine of Github pages to modify the html files. The ``.nojkyll`` is an empty file, just for signalling purposes, it will not be removed by ``make clear``

The Makefile first creates the documentation in the build folder via ``sphinx`` (target ``html``). Then the html documentation is copied to the docs folder. This step is necessary, as ``sphinx`` won't create an ``index.html`` file in the root directory of the build folder, but in a ``html`` subfolder instead.

There is an additional target ``clear`` in the Makefile, that will delete all files (except the ``.nojekyll`` file) from the docs directory.

We will also delete all auto-generated files via the ``clear`` target.

The autogeneration of the ``modules.rst`` file and a file for each module is done via the sphinx-apidoc command which is configured in the Makefile.

1.  Now switch to the gh-pages branch with ``git checkout gh-pages``
2.  run ``Make clean`` and a ``Make Clear``  again to wipe out all generated docs in this branch
3. Use ``git merge master`` to fetch all the changes from the master
4. Generate the docs and copy it to the docs folder wit ``make html``
5. Commit the generated files to the gh-pages branch
6. Push gh-pages to the remote repo on Github
7. Go back to the master branch wit ``git checkout master``
8. Check the Github pages.

