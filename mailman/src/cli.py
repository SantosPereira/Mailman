import click
from mailman.src.main import export, __import, save_dotfile
from pathlib import Path


home = Path.home()

Path(f"{home}/.backup").mkdir(parents=True, exist_ok=True)

@click.group()
def cli():
    """Multi package manager tool to export/import lists of installed packages, OS configurations and variables"""
    pass


@cli.command("import")
@click.argument('source', required=True, default=f"{home}/.backup")
def __import(source):
    """Import previous system configuration backup"""
    __import(source=source)


@cli.command()
@click.option('-s', '--output', 'output', required=False, default=f"{home}/.backup/apps.json")
def export(output):
    """Export system configurations about packages and environment variables"""
    export(output_file=output)


@cli.command()
@click.argument('dotfile', required=True)
def dotfile(dotfile):
    """Create a symlink of a dotfile, storing the source at a common place"""
    save_dotfile(file=dotfile)


if __name__ == '__main__':
    cli()
