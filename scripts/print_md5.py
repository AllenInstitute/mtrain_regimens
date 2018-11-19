import hashlib
import click

@click.command()
@click.option('-f','--filename',default='',help='Input file to use for hash computation')
def main(filename):

    with open(filename, 'r') as f:
        print hashlib.md5(f.read()).hexdigest()

if __name__ == '__main__':
    main()