import click


@click.group()
def messages():
    pass


@click.command(help='rename files from input for moving into the Zettelkasten')
def stage():
    click.echo('stage input')


@click.command(help='add ids, consecutive numbering, keep links life')
def reorganize():
    click.echo('reorganize')


messages.add_command(stage)
messages.add_command(reorganize)
