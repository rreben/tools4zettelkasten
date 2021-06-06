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
