package = []
require = ["ext-autodoc"]

conf_py = '''
extensions.append('sphinx.ext.autosummary')
autosummary_generate = True
'''