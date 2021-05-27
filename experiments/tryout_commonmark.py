import commonmark
from pprint import pprint

teststring = """
---
layout: post
title: Blogging Like a Hacker
---

# A Title
some text

and a [[wikilink]]

[[wikilink|link]]
"""

# print(commonmark.commonmark(teststring))
parser = commonmark.Parser()
ast = parser.parse(teststring)
pprint(commonmark.dumpAST(ast))
#renderer = commonmark.HtmlRenderer()
renderer = commonmark.ReStructuredTextRenderer()
html = renderer.render(ast)
pprint(html)
