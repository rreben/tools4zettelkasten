Publish on PyPi
===============

We follow the excellent advice in
https://www.codementor.io/@arpitbhayani/host-your-python-package-using-github-on-pypi-du107t7ku

First we have to create an account on PyPi and on testpipy.
Go to https://pypi.python.org and https://testpypi.python.org respectively.

We store the user names and password in a ``~/.pypirc``
file in our home directory (**not** the project directory).

The file has the following format:

.. code-block:: linux-config

    [distutils]
    index-servers =
        pypi
        testpypi

    [pypi]
    username:<username>
    password:<password>

    [testpypi]
    username:<username>
    password:<password>

Use the following command to register your package
and to check your settings in ``setup.py`` and ``setup.cfg``:

.. code-block:: sh

    python setup.py register -r pypitest

