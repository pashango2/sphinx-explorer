package = [
    "commonmark",
    "recommonmark"
]

conf_py = '''
source_suffix = [source_suffix, '.md']

from recommonmark.parser import CommonMarkParser
source_parsers = {
    '.md': CommonMarkParser,
}

from recommonmark.transform import AutoStructify
github_doc_root = 'https://github.com/rtfd/recommonmark/tree/master/doc/'

def setup(app):
    app.add_config_value('recommonmark_config', {
            'url_resolver': lambda url: github_doc_root + url,
            'auto_toc_tree_section': 'Contents',
            }, True)
    app.add_transform(AutoStructify)
'''

