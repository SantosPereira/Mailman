import click
from mailman.src.main import main
from pathlib import Path


home = Path.home()

Path(f"{home}/.backup").mkdir(parents=True, exist_ok=True)

@click.command()
@click.option('-s', '--output', 'output', required=False, default=f"{home}/.backup/apps.json")
def run(output):
    # """Simple program that greets NAME for a total of COUNT times."""
    main(output_file=output)


if __name__ == '__main__':
    run()
