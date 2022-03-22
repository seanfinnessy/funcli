import click
import os
import pyautogui
import time
import sys


def no_credentials_file():
    click.secho(
        f"Could not find credentials file. Please use 'add' command to create valid credentials.", fg='red')
    sys.exit()


@click.group()
def valcommands():
    '''
    Commands for Valorant
    '''


@click.command("add")
@click.option('--username', '-u', help="Your Valorant username", required=True, prompt="Username")
@click.option('--password', '-p', help="Password belonging to your username", required=True, hide_input=True, confirmation_prompt=True, prompt="Password")
def create_user(username, password):
    '''
    Command for adding username and password to credentials file.
    '''
    if not os.path.exists('credentials.txt'):
        with open('credentials.txt', 'w') as f:
            f.write(username + ':' + password + '\n')

    else:
        with open('credentials.txt', 'r') as f:
            for line in f:
                if username + ':' in line:
                    click.secho(
                        "This username already exists. Please try a different one.", fg='red')
                    sys.exit()
        with open('credentials.txt', "a") as f:
            f.write(username + ':' + password + '\n')
    click.secho("Added username and password to credentials file.", fg='green')


@click.command('remove')
@click.option('--username', '-u', help="Valorant username you wish to remove", required=True, prompt="Username")
def remove_user(username):
    '''
    Command for removing username and password from credentials file.
    '''
    if not os.path.exists('credentials.txt'):
        no_credentials_file()

    else:
        username_flag = False
        with open("credentials.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                if username + ':' in line:
                    username_flag = True
        with open("credentials.txt", "w") as f:
            for line in lines:
                if username + ':' not in line:
                    f.write(line)

        if username_flag is True:
            click.secho(
                f"Removed {username} from credentials file.", fg='green')
        else:
            click.secho(
                f"Could not find {username} in credentails file.", fg='red')


@click.command(name='login')
@click.argument('username')
def login_user(username):
    '''
    Command for logging into Valorant by providing a valid username.
    '''
    # Check if credential file exists
    if not os.path.exists('credentials.txt'):
        no_credentials_file()

    # Get password
    click.echo(f"Collecting password for {username}...")
    password = ""
    with open('credentials.txt', 'r') as f:
        for line in f:
            if username + ':' in line:
                # Seperate after colon and limit to one split
                password = line.split(":", 1)[1]
    if password == "":
        click.secho(f"Could not find password for {username}.", fg='red')
        sys.exit()

    # Login using credentials found
    try:
        # Open riot launcher
        os.startfile(
            'C:\\Riot Games\\Riot Client\\RiotClientServices.exe')

        # wait for riot launcher to open
        click.echo("Waiting for launcher to open...")
        time.sleep(5)

        # type in username and password
        pyautogui.typewrite(username)
        pyautogui.press('tab')
        pyautogui.typewrite(password)
        pyautogui.press('enter')
        time.sleep(3)

        # hit tab 5 times to switch to valorant
        for _ in range(5):
            pyautogui.press('tab')
        pyautogui.press('enter')
        time.sleep(1)

        # tab hit 5 times to switch to enter button
        for _ in range(5):
            pyautogui.press('tab')
        pyautogui.press('enter')

        click.secho(f"Successfully logged in as: {username}.", fg='green')
    except PermissionError:
        click.secho("Permission is denied.", fg='red')


valcommands.add_command(login_user)
valcommands.add_command(create_user)
valcommands.add_command(remove_user)
