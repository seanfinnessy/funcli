import click
import os
import pyautogui
import time
import sys

from cryptography.fernet import Fernet
from util.lookup_functions import GameSetup, LocalSetup, LobbySetup


def create_key():
    '''
    Generate key
    '''
    key = Fernet.generate_key()
    if os.path.exists(os.environ['USERPROFILE'] + '\Desktop\ValCLI\key.key'):
        return

    with open(os.path.expanduser("~\Desktop\ValCLI\key.key"), "wb") as key_file:
        key_file.write(key)


def load_key():
    '''
    Load key from directory
    '''
    return open(os.path.expanduser("~\Desktop\ValCLI\key.key"), "rb").read()


def no_credentials_file():
    click.secho(
        f"Could not find credentials file. Please use 'add' command to create valid credentials.", fg='red')
    sys.exit()


def error_check(check, message):
    if check == -1:
        click.secho(message, fg='red')
        sys.exit()
    return


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
    Add USERNAME and PASSWORD to credentials file. Password is encrypted.
    '''
    # Create a key
    create_key()
    crypter = Fernet(load_key())
    enc_password = crypter.encrypt(password.encode("ascii")).decode()

    if not os.path.exists(os.path.expanduser("~\Desktop\ValCLI\credentials.txt")):
        if not os.path.exists(os.environ['USERPROFILE'] + '\Desktop\ValCLI'):
            os.mkdir(os.environ['USERPROFILE'] + '\Desktop\ValCLI')
        with open(os.path.expanduser("~\Desktop\ValCLI\credentials.txt"), 'w') as f:
            f.write(username + ':' + password + '\n')

    else:
        with open(os.path.expanduser("~\Desktop\ValCLI\credentials.txt"), 'r') as f:
            for line in f:
                if username + ':' in line:
                    click.secho(
                        "This username already exists. Please try a different one.", fg='red')
                    sys.exit()
        with open(os.path.expanduser("~\Desktop\ValCLI\credentials.txt"), "a") as f:
            f.write(username + ':' + enc_password + '\n')
    click.secho("Added username and password to credentials file.", fg='green')


@click.command('remove')
@click.option('--username', '-u', help="Valorant username you wish to remove", required=True, prompt="Username")
def remove_user(username):
    '''
    Remove USERNAME and PASSWORD from credentials file.
    '''
    if not os.path.exists(os.path.expanduser("~\Desktop\ValCLI\credentials.txt")):
        no_credentials_file()

    else:
        username_flag = False
        with open(os.path.expanduser("~\Desktop\ValCLI\credentials.txt"), "r") as f:
            lines = f.readlines()
            for line in lines:
                if username + ':' in line:
                    username_flag = True
        with open(os.path.expanduser("~\Desktop\ValCLI\credentials.txt"), "w") as f:
            for line in lines:
                if username + ':' not in line:
                    f.write(line)

        if username_flag is True:
            click.secho(
                f"Removed {username} from credentials file.", fg='green')
        else:
            click.secho(
                f"Could not find {username} in credentials file.", fg='red')

# TODO: Need to add handling for if info is incorrect.


@click.command('login')
@click.argument('username')
def login_user(username):
    '''
    Log into Valorant by providing a valid username.
    '''

    # Check if credential file exists
    if not os.path.exists(os.path.expanduser("~\Desktop\ValCLI\credentials.txt")):
        no_credentials_file()

    # Get password
    click.echo(f"Collecting password for {username}...")
    password = ""
    with open(os.path.expanduser("~\Desktop\ValCLI\credentials.txt"), 'r') as f:
        for line in f:
            if username + ':' in line:
                # Create engine
                crypter = Fernet(load_key())
                password = line.split(":", 1)[1]
                # Encode password to get decrypted. Decode to read string.
                password = crypter.decrypt(password.encode("ascii")).decode()
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


@click.command('lookup')
@click.option('--name', '-n', help="Valorant in game name", required=True, prompt="Game Name")
@click.option('--tag', '-t', help="Valorant in game tag", required=True, prompt="Game Tag")
def lookup_user(name, tag):
    '''
    Lookup a Valorant user using their IGN and TAG.
    '''

    # Retrieve lockfile
    lockfile_dict = GameSetup.get_lockfile()
    error_check(lockfile_dict,
                "Lockfile not found. Make sure your game is open and running.")

    # Send friend request to get PUUID
    click.echo("Fetching player info...")
    player_puuid = LocalSetup(lockfile_dict).send_friend(name, tag)
    error_check(
        player_puuid, "Error finding player. Please check your spelling.")

    # Get region
    region = LocalSetup(lockfile_dict).get_region()
    error_check(region, "Could not retrieve region.")

    # Get headers
    headers, self_puuid = LocalSetup(lockfile_dict).get_headers()
    error_check(headers, "Could not retrieve headers or puuid.")

    # Get latest season ID
    season_id = LobbySetup(headers).get_latest_season_id(region)
    error_check(season_id, "Could not retrieve season ID.")

    # Get player rank ratings
    player_mmr_dict, win_percent = LobbySetup(headers).get_player_mmr(
        player_id=player_puuid, seasonID=season_id, region=region)
    click.echo(click.style("Rank: ", fg='green') + click.style(
        player_mmr_dict["CurrentRank"] + ', ' + str(player_mmr_dict["RankRating"]) + " RR.", fg='blue'))
    click.echo(click.style("Leaderboard Position: ", fg='green') +
               click.style(player_mmr_dict["Leaderboard"], fg='blue'))
    click.echo(click.style("Win Percent (this act): ", fg='green') +
               click.style(str(win_percent) + "%.", fg='blue'))


valcommands.add_command(login_user)
valcommands.add_command(create_user)
valcommands.add_command(remove_user)
valcommands.add_command(lookup_user)

if __name__ == 'main':
    valcommands()