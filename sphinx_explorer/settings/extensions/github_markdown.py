#!/usr/bin/env python

from __future__ import absolute_import

import re
from markdown import Markdown
from markdown.util import AMP_SUBSTITUTE, HTML_PLACEHOLDER_RE
from markdown.odict import OrderedDict
from docutils import nodes
from docutils import parsers

try:
    from html import entities
except ImportError:
    import htmlentitydefs as entities

MAILTO = ('\x02amp\x03#109;\x02amp\x03#97;\x02amp\x03#105;\x02amp\x03#108;'
          '\x02amp\x03#116;\x02amp\x03#111;\x02amp\x03#58;\x02')
INLINE_NODES = (
    nodes.emphasis,
    nodes.strong,
    nodes.literal,
    nodes.reference,
    nodes.image,
)
HAVING_BLOCK_NODE = (
    nodes.list_item,
)


class SectionPostprocessor(object):
    def run(self, node):
        i = 0
        while i < len(node):
            if isinstance(node[i], nodes.section):
                for subnode in node[i + 1:]:
                    if isinstance(subnode, nodes.section) and subnode['level'] == node[i]['level']:
                        break
                    node.remove(subnode)
                    node[i] += subnode

                self.run(node[i])

            i += 1

        return node


class StripPostprocessor(object):
    def run(self, node):
        class FakeStripper(object):
            def strip(self):
                return node

        return FakeStripper()


def unescape_email(text):
    result = []
    n = len(AMP_SUBSTITUTE)
    for char in text.split(';'):
        if char.startswith(AMP_SUBSTITUTE + "#"):
            result.append(chr(int(char[n + 1:])))
        elif char.startswith(AMP_SUBSTITUTE):
            result.append(entities.name2codepoint.get(char[n:]))
        else:
            result.append(char)
    return ''.join(result)


class Serializer(object):
    def __init__(self, markdown):
        self.markdown = markdown

    def __call__(self, element):
        return self.visit(element)

    def visit(self, element):
        method = "visit_%s" % element.tag
        if not hasattr(self, method):
            raise RuntimeError('Unknown element: %r' % element)
        else:
            return getattr(self, method)(element)

    def unescape_char(self, text, rawHtml=False):
        def unescape(matched):
            return chr(int(matched.group(1)))

        def expand_rawhtml(matched):
            html_id = int(matched.group(1))
            html, safe = self.markdown.htmlStash.rawHtmlBlocks[html_id]
            if rawHtml or re.match(r'(&[\#a-zA-Z0-9]*;)', html):
                return html  # unescape HTML entities only
            else:
                return matched.group(0)

        text = re.sub('\x02(\d\d)\x03', unescape, text)
        text = HTML_PLACEHOLDER_RE.sub(expand_rawhtml, text)
        return text

    def make_node(self, cls, element):
        node = cls()
        having_block_node = cls in HAVING_BLOCK_NODE
        if element.text and element.text != "\n":
            text = self.unescape_char(element.text)
            if HTML_PLACEHOLDER_RE.search(text):
                html_text = self.unescape_char(text, rawHtml=True)
                if html_text.startswith("<!--math"):
                    g = re.match(r"<!--math(.*?)-->", html_text, re.DOTALL)
                    if g:
                        node += nodes.math(
                            text=g.group(1).strip(),
                            latex=g.group(1).strip()
                        )
                else:
                    node += nodes.raw(format='html', text=html_text)
            elif having_block_node:
                node += nodes.paragraph(text=text)
            else:
                node += nodes.Text(text)
        for child in element:
            subnode = self.visit(child)
            if having_block_node and isinstance(subnode, INLINE_NODES):
                all_nodes_is_in_paragraph = True
                if len(node) == 0:
                    node += nodes.paragraph()
                node[0] += subnode
            else:
                all_nodes_is_in_paragraph = False
                node += subnode

            if child.tail and child.tail != "\n":
                tail = self.unescape_char(child.tail)
                if HTML_PLACEHOLDER_RE.search(tail):
                    node += nodes.raw(format='html', text=tail)
                elif all_nodes_is_in_paragraph:
                    node[0] += nodes.Text(tail)
                elif having_block_node:
                    node += nodes.paragraph(text=tail)
                else:
                    node += nodes.Text(tail)

        return node

    def visit_div(self, element):
        return self.make_node(nodes.container, element)

    def visit_headings(self, element):
        section = nodes.section(level=int(element.tag[1]))
        section += self.make_node(nodes.title, element)
        return section

    visit_h1 = visit_headings
    visit_h2 = visit_headings
    visit_h3 = visit_headings
    visit_h4 = visit_headings
    visit_h5 = visit_headings
    visit_h6 = visit_headings

    def visit_p(self, element):
        return self.make_node(nodes.paragraph, element)

    def visit_em(self, element):
        return self.make_node(nodes.emphasis, element)

    def visit_strong(self, element):
        return self.make_node(nodes.strong, element)

    def visit_code(self, element):
        return nodes.literal(text=self.unescape_char(element.text))

    def visit_a(self, element):
        refnode = self.make_node(nodes.reference, element)
        href = element.get('href')
        if href:
            if href.startswith(MAILTO):
                refnode['refuri'] = unescape_email(href)
                if href.endswith(refnode[0]):
                    refnode.pop(0)
                    refnode.insert(0, nodes.Text(refnode['refuri'][7:]))  # strip mailto:
            else:
                refnode['refuri'] = href
        if element.get('title'):
            refnode['reftitle'] = self.unescape_char(element.get('title'))
        return refnode

    def visit_img(self, element):
        image = self.make_node(nodes.image, element)
        if element.get('alt'):
            image['alt'] = self.unescape_char(element.get('alt'))
        if element.get('src'):
            image['uri'] = self.unescape_char(element.get('src'))
        if element.get('title'):
            # FIXME: Sphinx does not process reftitle attribute
            image['reftitle'] = self.unescape_char(element.get('title'))
        return image

    def visit_ul(self, element):
        return self.make_node(nodes.bullet_list, element)

    def visit_ol(self, element):
        return self.make_node(nodes.enumerated_list, element)

    def visit_li(self, element):
        return self.make_node(nodes.list_item, element)

    def visit_pre(self, element):
        return nodes.literal_block(text=self.unescape_char(element[0].text))

    def visit_blockquote(self, element):
        return self.make_node(nodes.literal_block, element)

    def visit_br(self, _):
        return nodes.raw(format='html', text="<br/>")

    def visit_table(self, element):
        headers = []
        rows = [[]]
        for ch_element in element.iter():
            if ch_element.tag == "th":
                headers.append(ch_element.text)
            elif ch_element.tag == "td":
                rows[-1].append((ch_element.text, ch_element.attrib.get("align")))
            elif ch_element.tag == "tr":
                if rows[-1]:
                    rows.append([])

        # Not: http://agateau.com/2015/docutils-snippets/
        table_node = nodes.table()
        tgroup_node = nodes.tgroup(cols=len(headers))
        table_node += tgroup_node

        # add colspec
        for x in range(len(headers)):
            tgroup_node += nodes.colspec(colwidth=1)

        # add thead
        thead_node = nodes.thead()
        tgroup_node += thead_node

        header_row_node = nodes.row()
        thead_node += header_row_node
        for header in headers:
            entry = nodes.entry()
            header_row_node += entry
            entry += nodes.paragraph(text=header)

        # add tbody
        tbody_node = nodes.tbody()
        tgroup_node += tbody_node
        for row in rows:
            row_node = nodes.row()
            for text, align in row:
                entry = nodes.entry()
                row_node += entry
                entry += nodes.paragraph(text=text, align=align)

            tbody_node += row_node

        return table_node


def md2node(text):
    md = Markdown(["gfm"])
    md.serializer = Serializer(md)
    md.stripTopLevelTags = False
    md.postprocessors = OrderedDict()
    md.postprocessors['section'] = SectionPostprocessor()
    md.postprocessors['strip'] = StripPostprocessor()
    text = preprocess(text)
    return md.convert(text)


def preprocess(text):
    parse_re = re.compile("^\s*```\s*math\s*$")
    end_re = re.compile("^\s*```\s*$")

    new_lines = []
    for line in text.splitlines():
        if parse_re.match(line):
            new_lines += ["<!--math"]
        elif end_re.match(line):
            new_lines += ["-->"]
        else:
            new_lines += [line]

    return "\n".join(new_lines)


class MarkdownParser(parsers.Parser):
    def parse(self, inputstring, document):
        self.setup_parse(inputstring, document)
        self.document = document
        for node in md2node(inputstring):
            self.document += node

        # assign IDs to all sections
        for node in self.document.traverse(nodes.section):
            self.document.note_implicit_target(node)
        self.finish_parse()
