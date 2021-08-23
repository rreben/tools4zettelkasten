Setup the Dev Environment
=========================

psioniq Extension
-----------------

Load the psioniq Extension for VSCode and add the following configuration. To the ``settings.json`` in ``.vscode`` folder.

.. code-block:: JSON

  {
    "psi-header.config": {
        "license": "MIT",
    "author": "Dr. Rupert Rebentisch"
    },
    "psi-header.templates": [
        {"language": "*",
            "template": [
                "<<filename>>",
                "Copyright (c) <<year>> <<author>>",
                "Licensed under the MIT license"
            ],
            "changeLogCaption": "HISTORY:"
        }
    ],
    "psi-header.lang-config": [
        {"language": "python",
        "begin": "",
        "prefix": "# ",
        "end": ""
        }
    ]
    }

Enable the Debugger
-------------------

In VS Code there are two debuggers. There is the pdb command line debugger which
is accessible via the terminal and the VS-Code own debugger that is integrated
in the environment.

You have a special view for running tests and debugging them.

.. image:: images/Lab2.jpg

You also can run and start individual tests from the source file.

.. image:: images/lab.jpg

For this to work the setting of the debugger and the test engine have to be in sync.

Start the detection of tests with ``Python: Discover Tests`` from the command palette. 
Specify ``tests`` as the test directory.

For more information look at the `VSCode Documentation <https://code.visualstudio.com/docs/python/testing>`_