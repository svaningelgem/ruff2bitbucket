# 0.3.0
* Reducing python minimal version to 3.7. This is the lowest version that ruff can be installed with.

# 0.2.0
* Adding `__version__`
* Adjusted logger levels
* Bugfix for `distutils.spawn.has_executable` which is deprectated in py3.10 in favor of `shutil.which`
* Bugfix for error when the insight triggered an error on BitBucket
* Bugfix for wrong variable name causing the program to crash during upload of a code insight.

# 0.1.0
* First version supporting basic ruff validation of a repository.
