Publish on PyPi
===============

We follow the excellent advice in
https://www.codementor.io/@arpitbhayani/host-your-python-package-using-github-on-pypi-du107t7ku

Perparation
-----------

First we have to create an account on PyPi and on testpipy.
Go to https://pypi.python.org and https://testpypi.python.org respectively.

Next get the API tokens from the account.

We store the user names and password in a ``~/.pypirc``
file in our home directory (**not** the project directory).

The file has the following format:

.. code-block:: linux-config

    [distutils]
    index-servers =
        pypi
        testpypi
        testpypi

    [pypi]
    username:<username>
    password:<password>

    [testpypi]
    username:<username>
    password:<password>

    [testpypi]
    username = __token__
    password = pypi-AgENdG...some...token..SlYKYg

The file must not contain a repository entry. Because then twine will not
default to the pypi server but will return a deprecated error. See
https://packaging.python.org/guides/migrating-to-pypi-org/ for details.

Use the following command to register your package
and to check your settings in ``setup.py`` and ``setup.cfg``:

.. code-block:: sh

    python setup.py register -r pypitest

Prepare the package and publish on GitHub
-----------------------------------------

1. Change the version number in ``tools4zettel/__init__.py``
2. Test tools4zettelkasten with all pytest testsuites.
3. Update the documentation in the gh-pages branch.
4. Commit everything an push to master.
5. Use the "Create a new release" function in the github UI.
6. Take version number as the release tag on the github UI.
7. You will get a link to the assets (tar.gz) and (.zip) file.


Make a release package
----------------------

1. Right now we have to edit the release number also in ``setup.py``.
2. Use ``pip install --editable .`` to install the package locally.
   This is just a test. Use ``uninstall`` to remove the package.
3. Use ``python -m build`` to build the package.
   You will now have a tar.gz file and a .whl file in the ``dist/`` directory.
4. We use ``python -m twine upload --repository testpypi dist/*``
   to upload the package to testpypi.
5. Create a new fresh virtualenv and install the package via ``python3 -m pip
   install --extra-index-url https://pypi.org/simple/ --index-url
   https://test.pypi.org/simple/  tools4zettelkasten``. Dabei ist der Parameter
   ``--extra-index-url`` notwendig, damit auch Dependencies installiert werden
   können, die nur auf PyPi nicht jedoch auf testpipy verfügbar sind.
6. Run the tests with ``python -m tools4zettelkasten``. Try the commands
   show, analyse and start.
7. We use ``python -m twine upload --repository pypi dist/*``
   to upload the package to pypi.

