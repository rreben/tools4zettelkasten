# define regex for Wiki links
WIKI_PATTERN = (
    r'\[\['                   # [[
    r'([\s\S]+?\|[\s\S]+?)'   # Page 2|Page 2
    r'\]\](?!\])'             # ]]
)

# define how to parse matched item


def parse_wiki(inline, m, state):
    # ``inline`` is ``md.inline``, see below
    # ``m`` is matched regex item
    text = m.group(1)
    title, link = text.split('|')
    return 'wiki', link, title

# define how to render HTML


def render_html_wiki(link, title):
    return f'<a href="{link}">{title}</a>'


def plugin_wiki(md):
    # this is an inline grammar, so we register wiki rule into md.inline
    md.inline.register_rule('wiki', WIKI_PATTERN, parse_wiki)

    # add wiki rule into active rules
    md.inline.rules.append('wiki')

    # add HTML renderer
    if md.renderer.NAME == 'html':
        md.renderer.register('wiki', render_html_wiki)
