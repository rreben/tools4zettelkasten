# Generate the docs

1. Edit the rst files in the master branch as needed
2. You might want to edit the release number in ``conf.py``
3. Comit and push
4. To generate the docs navigate to the docs_source folder 
5. run ``Make clean`` and a ``Make Clear``  
6. Now switch to the gh-pages branch with ``git checkout gh-pages``
7. run ``Make clean`` and a ``Make Clear``  again to wipe out all generated docs in this branch
8. Use ``git merge master`` to fetch all the changes from the master
9. Generate the docs and copy it to the docs folder wit ``make html``
10. Commit the generated files to the gh-pages branch
11. Go back to the master branch wit ``git checkout master``
12. Push all branches to the remote repo on Github
13. Check the Github pages.

