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
        self.config["user"] = {}
        self.config["mission"] = {}

        self.base_url = "https://data.nsldata.com/webAPI.php"
        self.url = ""

    def _prompt_set_email_and_api_key(self):
        sys.exit(
            "\nPlease configure your email and API key using the following commands:\n\n\t./bark.py config --email <your_email@example.com>\n\t./bark.py config --api-key <your_api_key>\n"
        )

    def _prompt_set_mission_id(self):
        sys.exit(
            "\nPlease configure your mission ID using the following commands:\n\n\t./bark.py comfig --mission-id <your_mission_id>\n"
        )

    def _load_config(self):
        "Load config.toml, if one exists. Otherwise, create one"
        try:
            with open("config.toml", "r") as file:
                self.config = toml.loads(file.read())
        except FileNotFoundError:
            with open("config.toml", "w") as file:
                file.write(toml.dumps(self.config))
        except Exception:
            traceback.print_exc()

    @property
    def email(self):
        # Load config
        self._load_config()

        # Attempt to return email. Otherwise, prompt user to configure email
        try:
            return self.config["user"]["email"]
        except KeyError:
            self._prompt_set_email_and_api_key()

    @email.setter
    def email(self, email):
        # Load config, as to ensure other configurations persist after overwriting config file
        self._load_config()

        # Set email
        self.config["user"]["email"] = email

        # Overwrite existing config file
        with open("config.toml", "w") as file:
            file.write(toml.dumps(self.config))

    @property
    def api_key(self):
        # Load config
        self._load_config()

        # Attempt to return API key. Otherwise, prompt user to configure key
        try:
            return self.config["user"]["api-key"]
        except KeyError:
            self._prompt_set_email_and_api_key()

    @api_key.setter
    def api_key(self, api_key):
        # Load config, as to ensure other configurations persist after overwriting config file
        self._load_config()

        # Set API key
        self.config["user"]["api-key"] = api_key

        # Overwrite existing config file
        with open("config.toml", "w") as file:
            file.write(toml.dumps(self.config))

    @property
    def mission_id(self):
        # Load config
        self._load_config()

        # Attempt to return mission id. Otherwise, prompt user to configure key
        try:
            return self.config["mission"]["id"]
        except KeyError:
            self._prompt_set_mission_id()

    @mission_id.setter
    def mission_id(self, mission_id):
        # Load config, as to ensure other configurations persist after overwriting config file
        self._load_config()

        # Set mission id
        self.config["mission"]["id"] = mission_id

        # Overwrite existing config file
        with open("config.toml", "w") as file:
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
        return r.json()

    def console_api(self, method, params={}):
        self.url = self._get_request_url(method, params)
        result = self._load_url_and_parse_json(self.url)
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

    # Setup subparser for subcommands
    subparsers = parser.add_subparsers(dest="command")

    # Create parser with args for configuring email, API key, and/or mission id
    parser_config = subparsers.add_parser(
        "config", help="Configure email, API key, and/or mission ID"
    )
    parser_config.add_argument("--email", type=str, required=True, help="Set email")
    parser_config.add_argument("--api-key", type=str, required=True, help="Set API key")
    parser_config.add_argument("--mission-id", type=str, help="Set Mission ID")

    # Create parser with args for requesting mission info
    parser_info = subparsers.add_parser("info", help="Request mission info")
    parser_info.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbosity (prints full API call)",
    )

    # Create parser with args for requesting packets info
    parser_packets = subparsers.add_parser("ls", help="Request list of packets")
    parser_packets.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbosity (prints full API call)",
    )

    # Create parser with args for sending uplink command
    parser_uplink = subparsers.add_parser("uplink", help="Send an uplink command")
    parser_uplink.add_argument("--radio-view-id", type=str, help="Set radio view ID")
    parser_uplink.add_argument("--format-id", type=str, help="Set format ID")
    parser_uplink.add_argument("--fields", type=str, help="Set fields")
    parser_uplink.add_argument(
        "--note",
        type=str,
        help="Add an optional note as string",
    )
    parser_uplink.add_argument(
        "--dry-run",
        action="store_true",
        help="Enable dry run",
    )

    # Print help text if no arguments passed
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Parse arguments
    args = parser.parse_args()

    # Setup bark instance
    bark = Bark()

    # Configure/update config.toml, if passed as arguments
    if args.command == "config":
        if args.email:
            bark.email = args.email
        if args.api_key:
            bark.api_key = args.api_key
        if args.mission_id:
            bark.mission_id = args.mission_id

    # Request mission info
    if args.command == "info":
        mission_id_to_fetch = bark.mission_id
        mission_details = bark.console_api(
            "getMissionDetails", {"missionID": mission_id_to_fetch}
        )
        result_as_formatted_string = json.dumps(mission_details, indent=2)

        # Prepend output with full url of API call, if --verbose flag is also passed
        if args.verbose:
            print(bark.url)

        print(result_as_formatted_string)

    # Request list of packets
    if args.command == "ls":
        mission_id_to_fetch = bark.mission_id
        mission_details = bark.console_api(
            "getMissionDetails", {"missionID": mission_id_to_fetch}
        )
        recent_packets = bark.console_api(
            "getConsoleMissionPackets", {"missionID": mission_id_to_fetch}
        )

        # Prepend output with full url of API call, if --verbose flag is also passed
        if args.verbose:
            print(bark.url)

        print("Most Recent Packets, Any Radio/Format")
        most_recent_packets_any_radio_or_format = recent_packets["lastAnyRadioOrFormat"]
        for packet in most_recent_packets_any_radio_or_format:
            radio_view_id = packet["radioViewID"]
            radio_view_name = mission_details["radioViews"][str(radio_view_id)][
                "radioViewName"
            ]
            format_id = packet["formatID"]
            format_name = mission_details["downlinkFormats"][str(format_id)][
                "formatName"
            ]
            print("  ", radio_view_name, format_name)
            print("     ", packet["gatewayTS"], "UTC")
            print("     ", packet["numBytes"], "bytes")
            print("     ", packet["packetFields"])
