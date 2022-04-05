import os
from time import sleep
import requests
import urllib3
import base64

from util.conversions import number_to_ranks

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class GameSetup:
    '''
    Basic utility needed for Valorant Local API.
    '''
    @staticmethod
    def get_lockfile():
        try:
            with open(os.path.join(os.getenv('LOCALAPPDATA'), R'Riot Games\Riot Client\Config\lockfile')) as lockfile:
                data = lockfile.read().split(':')
                keys = ['name', 'PID', 'port', 'password', 'protocol']
                # dict constructor and zip function used to create dict with lockfile data.
                return (dict(zip(keys, data)))
        except:
            return -1

    @staticmethod
    def get_current_version():
        try:
            response = requests.get(
                "https://valorant-api.com/v1/version", verify=False)
            res_json = response.json()
            client_version = res_json['data']['riotClientVersion']
            return client_version
        except:
            return -1


class LocalSetup:
    '''
    Get user's region and headers for API.
    '''

    def __init__(self, lockfile):
        self.lockfile = lockfile
        self.local_headers = {'Authorization': 'Basic ' +
                              base64.b64encode(('riot:' + self.lockfile['password']).encode()).decode()}

    def get_region(self):
        try:
            response = requests.get(
                f"https://127.0.0.1:{self.lockfile['port']}/product-session/v1/external-sessions", headers=self.local_headers, verify=False)
            res_json = response.json()
            return list(res_json.values())[0]['launchConfiguration']['arguments'][3].split("=")[1]
        except:
            return -1

    def get_headers(self):
        try:
            response = requests.get(
                f"https://127.0.0.1:{self.lockfile['port']}/entitlements/v1/token", headers=self.local_headers, verify=False)
            entitlements = response.json()
            puuid = entitlements['subject']
            headers = {
                'Authorization': f"Bearer {entitlements['accessToken']}",
                'X-Riot-Entitlements-JWT': entitlements['token'],
                'X-Riot-ClientPlatform': "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
                'X-Riot-ClientVersion': GameSetup.get_current_version()
            }
            return headers, puuid
        except:
            return -1

    def send_friend(self, game_name: str, game_tag: str):
        json = {
            'game_name': game_name,
            'game_tag': game_tag
        }

        try:
            response_current = requests.get(
                f"https://127.0.0.1:{self.lockfile['port']}/chat/v4/friends", headers=self.local_headers, verify=False)
            if response_current.ok:
                response_current_json = response_current.json()
                for friend in response_current_json["friends"]:
                    if game_name.lower() == str(friend["game_name"]).lower() and game_tag.lower() == str(friend["game_tag"]).lower():
                        return friend["puuid"]

            response_post = requests.post(
                f"https://127.0.0.1:{self.lockfile['port']}/chat/v4/friendrequests", headers=self.local_headers, verify=False, json=json)
            sleep(1)

            if response_post.ok:
                response_get = requests.get(
                    f"https://127.0.0.1:{self.lockfile['port']}/chat/v4/friendrequests", headers=self.local_headers, verify=False)
                sleep(1)

                if response_get.ok:
                    response_get_json = response_get.json()
                    puuid = response_get_json['requests'][-1]['puuid']
                    json_cancel = {'pid': puuid}
                    response_cancel = requests.delete(
                        f"https://127.0.0.1:{self.lockfile['port']}/chat/v4/friendrequests", headers=self.local_headers, verify=False, json=json_cancel)

                    if response_cancel.ok:
                        return puuid
            else:
                return -1
        except:
            return -1


class LobbySetup:
    '''
    Retrieve lobby details. Must be in game.
    '''

    def __init__(self, headers):
        self.headers = headers

    def get_latest_season_id(self, region):
        try:
            response = requests.get(
                f"https://shared.{region}.a.pvp.net/content-service/v3/content", headers=self.headers, verify=False)
            content = response.json()
            for season in content["Seasons"]:
                if season["IsActive"]:
                    return season["ID"]
        except:
            return -1

    def get_player_mmr(self, region, player_id, seasonID):
        response = requests.get(
            f"https://pd.{region}.a.pvp.net/mmr/v1/players/{player_id}", headers=self.headers, verify=False)
        keys = ['CurrentRank', 'RankRating', 'Leaderboard']
        try:
            if response.ok:
                r = response.json()
                if r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID] or r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["NumberOfWinsWithPlacements"] != 0:
                    numberOfWins = r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["NumberOfWinsWithPlacements"]
                    numberOfGames = r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["NumberOfGames"]
                    winPercent = round(int(numberOfWins) /
                                       int(numberOfGames), 3) * 100
                else:
                    winPercent = 0
                rankTIER = r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["CompetitiveTier"]
                if int(rankTIER) >= 21:
                    rank = [rankTIER,
                            r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["RankedRating"],
                            r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["LeaderboardRank"],
                            ]
                elif int(rankTIER) not in (0, 1, 2, 3):
                    rank = [rankTIER,
                            r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["RankedRating"],
                            'N/A',
                            ]
                else:
                    rank = [0, 0, 'N/A']
            else:
                print("Failed retrieving rank.")
                rank = [0, 0, 'N/A']
                winPercent = 0
        except TypeError:
            rank = [0, 0, 'N/A']
            winPercent = 0
        except KeyError:
            rank = [0, 0, 'N/A']
            winPercent = 0

        # Convert tier to rank name.
        rank[0] = number_to_ranks[rank[0]]
        return dict(zip(keys, rank)), winPercent
