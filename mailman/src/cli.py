import click
from mailman.src.main import main
from pathlib import Path


home = Path.home()

Path(f"{home}/.backup").mkdir(parents=True, exist_ok=True)

@click.command()
@click.option('-s', '--output', 'output', required=False, default=f"{home}/.backup/apps.json")
def run(output):
    """Export system configurations about packages and environment variables"""
    main(output_file=output)


if __name__ == '__main__':
    run()
