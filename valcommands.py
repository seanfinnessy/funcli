import click
import os
import pyautogui
import time
import sys


def no_credentials_file():
    with open('credentials.txt', 'r'):
        click.echo(
            f"Could not find credentials file. Please use 'add' command to create valid credentials.")
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
    Command for adding username and password for later use.
    '''
    if not os.path.exists('credentials.txt'):
        with open('credentials.txt', 'w') as f:
            f.write(username + ':' + password + '\n')

    else:
        with open('credentials.txt', 'r') as f:
            for line in f:
                if username + ':' in line:
                    click.echo(
                        "This username already exists. Please try a different one.")
                    sys.exit()
        with open('credentials.txt', "a") as f:
            f.write(username + ':' + password + '\n')
    click.echo("Added username and password to credentials file.")


@click.command('remove')
@click.option('--username', '-u', help="Your Valorant username", required=True, prompt="Username to remove")
def remove_user(username):
    '''
    Command for removing username and password from credentials file.
    '''
    if not os.path.exists('credentials.txt'):
        no_credentials_file()

    else:
        with open("credentials.txt", "r") as f:
            lines = f.readlines()
        with open("credentials.txt", "w") as f:
            for line in lines:
                if username + ':' not in line:
                    f.write(line)
        click.echo(f"Removed {username} from credentials file.")


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
        click.echo(f"Could not find password for {username}")
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

        click.echo(f"Successfully logged in as: {username}")
    except PermissionError:
        click.echo("Permission is denied.")


valcommands.add_command(login_user)
valcommands.add_command(create_user)
valcommands.add_command(remove_user)
