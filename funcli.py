import click


@click.command()
@click.option('--name', '-n', help="Name of the person to say hello", required=True, prompt="Your name, please?\n")
@click.argument('number')
def funcli(name, number):
    '''
    This prints "Hello, {name}!"
    '''
    for _ in range(int(number)):
        print("A super important text for " + name + ":")
        print("You've been a great person to talk with...")
