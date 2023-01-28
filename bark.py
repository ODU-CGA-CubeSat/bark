#!/usr/bin/env python3

import argparse
import json
import sys
import requests
import toml
import traceback


class Bark:
    """class used for interfacing with the NSL API"""

    def __init__(self):
        self.config = {}

        self.base_url = "https://data.nsldata.com/webAPI.php"

    def _prompt_set_email_and_api_key(self):
        sys.exit(
            "\nPlease configure your email and API key using the following commands:\n\n\t./bark.py --set-email <your_email@example.com>\n\t./bark.py --set-api-key <your_api_key>\n"
        )

    def _load_config(self):
        "Load barkconfig.toml, if one exists. Otherwise, create one"
        try:
            with open("barkconfig.toml", "r") as file:
                self.config = toml.loads(file.read())
        except FileNotFoundError:
            with open("barkconfig.toml", "w") as file:
                file.write(toml.dumps(self.config))
        except Exception:
            traceback.print_exc()

    @property
    def email(self):
        # Load config
        self._load_config()

        # Attempt to return email. Otherwise, prompt user to configure email
        try:
            return self.config["email"]
        except KeyError:
            self._prompt_set_email_and_api_key()

    @email.setter
    def email(self, email):
        # Load config, as to ensure other configurations persist after overwriting config file
        self._load_config()

        # Set email
        self.config["email"] = email

        # Overwrite existing config file
        with open("barkconfig.toml", "w") as file:
            file.write(toml.dumps(self.config))

    @property
    def api_key(self):
        # Load config
        self._load_config()

        # Attempt to return API key. Otherwise, prompt user to configure key
        try:
            return self.config["api-key"]
        except KeyError:
            self._prompt_set_email_and_api_key()

    @api_key.setter
    def api_key(self, api_key):
        # Load config, as to ensure other configurations persist after overwriting config file
        self._load_config()

        # Set API key
        self.config["api-key"] = api_key

        # Overwrite existing config file
        with open("barkconfig.toml", "w") as file:
            file.write(toml.dumps(self.config))

    def _get_request_url(self, method, params={}):
        return "".join(
            [
                self.base_url,
                "?email=",
                self.email,
                "&apiKey=",
                self.api_key,
                "&method=",
                method,
                "&params=",
                json.dumps(params),
            ]
        )

    def _load_url_and_parse_json(self, url):
        r = requests.get(url)
        try:
            return r.json()
        except Exception as e:
            print("Error parsing returned JSON:", e)
            exit(0)

    def console_api(self, method, params={}):
        url = self._get_request_url(method, params)
        result = self._load_url_and_parse_json(url)
        if not result["success"]:
            print("Error from api call", method)
            print("  result.errorCode:", result["errorCode"])
            print("  result.description:", result["description"])
            print("  result.return:", result["return"])
            exit(0)
        else:
            return result["return"]


if __name__ == "__main__":
    # Setup parser
    parser = argparse.ArgumentParser(
        description="CLI client for communicating with satellites on the Iridium Satellite Network using the NearSpace Launch API"
    )
    parser.add_argument(
        "--set-email", type=str, nargs=1, help="Set NearSpace Launch user email"
    )
    parser.add_argument(
        "--set-api-key", type=str, nargs=1, help="Set NearSpace Launch API key"
    )
    parser.add_argument(
        "--get-email", action="store_true", help="Get NearSpace Launch user email"
    )
    parser.add_argument(
        "--get-api-key", action="store_true", help="Get NearSpace Launch API key"
    )
    parser.add_argument(
        "--info", action="store_true", help="Display info on first mission"
    )
    parser.add_argument(
        "-l", "--list", action="store_true", help="List all packets on first mission"
    )

    # Print help text if no arguments passed
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Parse arguments
    args = parser.parse_args()

    # Setup bark instance
    bark = Bark()

    # Get/set barkconfig.toml, if passed as argument
    if args.set_email:
        bark.email = args.set_email[0]
    if args.set_api_key:
        bark.api_key = args.set_api_key[0]
    if args.get_email:
        print(bark.email)
    if args.get_api_key:
        print(bark.api_key)

    # Handle consoleAPI commands
    missions = bark.console_api("getMissions")
    missionIDToFetch = missions[0]["missionID"]
    missionDetails = bark.console_api(
        "getMissionDetails", {"missionID": missionIDToFetch}
    )
    if args.info:
        result_as_formatted_string = json.dumps(missionDetails, indent=2)
        print(result_as_formatted_string)
    if args.list:
        recentPackets = bark.console_api(
            "getConsoleMissionPackets", {"missionID": missionIDToFetch}
        )
        print("Most Recent Packets, Any Radio/Format")
        numPackets = len(recentPackets["lastAnyRadioOrFormat"])
        for i in range(numPackets):
            packet = recentPackets["lastAnyRadioOrFormat"][-numPackets]
            radioViewID = packet["radioViewID"]
            radioViewName = missionDetails["radioViews"][str(radioViewID)][
                "radioViewName"
            ]
            formatID = packet["formatID"]
            formatName = missionDetails["downlinkFormats"][str(formatID)]["formatName"]
            print("  ", radioViewName, formatName)
            print("     ", packet["gatewayTS"], "UTC")
            print("     ", packet["numBytes"], "bytes")
            print("     ", packet["packetFields"])
