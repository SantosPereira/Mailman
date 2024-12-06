import click
from mailman.src.main import __export, import_config, centralize_dotfiles
from pathlib import Path


home = Path.home()

temp_dir = "/tmp/mailman"

Path(f"{temp_dir}").mkdir(parents=True, exist_ok=True)

@click.group()
def cli():
    """Multi package manager tool to export/import lists of installed packages, OS configurations and variables"""
    pass


@cli.command("import")
@click.argument('source', required=True)
def import_from_zip(source):
    """Import previous system configuration backup"""
    import_config(source)


@cli.command()
@click.option('-s', '--output', 'output', required=False, default=f"{temp_dir}/apps.json")
def export(output):
    """Export system configurations about packages and environment variables"""
    __export(output)


@cli.command()
@click.argument('dotfile', required=True)
def dotfile(dotfile):
    """Create a symlink of a dotfile, storing the source at a common place"""
    centralize_dotfiles(file=dotfile)


if __name__ == '__main__':
    cli()
