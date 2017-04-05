package = [
    "nbsphinx",
]

conf_py = '''
extensions.append('nbsphinx')
exclude_patterns.append('**.ipynb_checkpoints')
'''