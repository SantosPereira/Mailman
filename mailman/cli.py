import click
from mailman.main import main


@click.command()
@click.option('-s', '--output', 'output', required=False, default="./out/apps.json")
def run(output):
    # """Simple program that greets NAME for a total of COUNT times."""
    main(output_file=output)


if __name__ == '__main__':
    run()
