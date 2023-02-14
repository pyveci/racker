###################
Racker release docs
###################


1. Install release tools: ``pip install --editable=.[release]``
2. Bump version in ``setup.py`` and update ``CHANGES.rst``
3. Commit changes: ``git commit -m "Release 0.3.0" setup.py CHANGES.rst``
4. Create tag and push: ``git tag 0.3.0; git push; git push --tags``
5. Build packages: ``python -m build``
6. Upload packages: ``twine upload --skip-existing dist/*{.tar.gz,.whl}``
