#!/usr/bin/env python3

import argparse
import requests
import sys
from datetime import timedelta
from typing import Any, Callable, Optional

import bs4


def admin_cgi(
    args: argparse.Namespace,
    extra_params: Optional[dict[str, Any]] = {},
    request: Callable[..., requests.Response] = requests.get,
) -> requests.Response:
    """Wrapper for calls to /admin/cgi-bin/admin.cgi.

    This is the main API call interface. All calls require the function name
    argument 'f'. Common additional arguments are:
      n: next page, i.e. the page returned by the call
      a: action
      i: index

    Some calls might require a HTTP POST.

    Args:
      args (argparse.Namespace): Command line arguments object.
      extra_params (dict or None): Additional API call parameters.
      request (function): HTTP request type.
    """
    if extra_params is None:
        params = {}
    else:
        params = {"f": args.command}
        params.update(extra_params)
    return request(
        url=f"http://{args.hostname}/admin/cgi-bin/admin.cgi",
        params=params,
        auth=(args.username, args.password),
        timeout=10,
    )


def debug_cgi(
    args: argparse.Namespace,
    extra_params: Optional[dict[str, Any]] = {},
) -> requests.Response:
    """Wrapper for calls to /admin/cgi-bin/debug.cgi."""
    if extra_params is None:
        params = {}
    else:
        params = {"f": args.command}
        params.update(extra_params)
    return requests.get(
        url=f"http://{args.hostname}/admin/cgi-bin/debug.cgi",
        params=params,
        auth=(args.username, args.password),
        timeout=10,
    )


def ipc_send(args: argparse.Namespace) -> requests.Response:
    """Wrapper for calls to /admin/cgi-bin/ipc_send.

    ipc_send expects arguments separated by ampersands (i.e. not key,value pairs
    separated by '=').

    Args:
      args (argparse.Namespace): Command line arguments object.
    """
    return requests.get(
        url=f"http://{args.hostname}/admin/cgi-bin/ipc_send?"
        + "&".join([k for k in [args.command] + args.args]),
        auth=(args.username, args.password),
        timeout=10,
    )


def state_cgi(args: argparse.Namespace) -> requests.Response:
    """Wrapper for calls to /admin/cgi-bin/state.cgi.

    Args:
      args (argparse.Namespace): Command line arguments object.
    """
    return requests.get(
        url=f"http://{args.hostname}/admin/cgi-bin/state.cgi",
        params={"fav": 0},
        auth=(args.username, args.password),
        timeout=10,
    )


command_map: dict[str, Callable[[argparse.Namespace], requests.Response]] = {
    ## ipc_send
    "menu_collapse": ipc_send,
    "play": ipc_send,
    "power_down": ipc_send,
    "power_up": ipc_send,
    "show_list": ipc_send,
    "show_msg_box": ipc_send,
    ## admin_cgi
    "favorites": lambda args: admin_cgi(
        args,
        extra_params=(
            {
                "n": "../favorites.html",
                "a": "p",
                "i": args.args[0],
            }
            if len(args.args)
            else {"n": "../favorites.html"}
        ),
    ),
    "info": lambda args: admin_cgi(
        args,
        extra_params={
            "n": "../info.html",
        },
    ),
    "next_song": admin_cgi,
    "now_playing": lambda args: admin_cgi(
        args,
        extra_params={
            "f": "now_playing_frame",
            "n": "../now_playing_frame.html",
        },
    ),
    "play_pause": admin_cgi,
    "show_clock": lambda args: admin_cgi(
        args,
        request=requests.post,
    ),
    "uptime": lambda args: admin_cgi(
        args,
        extra_params={
            "n": "../empty.html",
        },
        request=requests.post,
    ),
    "volume_dec": admin_cgi,
    "volume_inc": admin_cgi,
    "volume_set": lambda args: admin_cgi(
        args,
        extra_params={
            "n": "../now_playing_frame.html",
            "v": args.args[0] if len(args.args) else -1,
        },
    ),
    ## debug_cgi
    "log": lambda args: debug_cgi(
        args,
        extra_params=None,
    ),
    "reboot": debug_cgi,
    "restart": debug_cgi,
    "start_telnet_server": lambda args: debug_cgi(
        args,
        extra_params={
            "v": "true",
        },
    ),
    ## state_sgi
    "state": state_cgi,
}
"""dict: Mapping of API command strings to appropriate API calls.
"""


class PrintCommandsExit(argparse.Action):
    """Prints list of available API commands and exits the program."""

    def __init__(
        self, option_strings: str, dest: str, nargs: int = 0, **kwargs: Any
    ):
        super().__init__(option_strings, dest, nargs, **kwargs)

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: Optional[str] = None,
    ) -> None:
        print("Available commands:")
        for k in command_map:
            print(f"  {k}")
        sys.exit(0)


def main() -> None:
    try:
        parser = argparse.ArgumentParser(
            conflict_handler="resolve",
            description="Command line client for the Freecom MusicPal.",
        )
        parser.add_argument(
            "-h",
            "--hostname",
            default="musicpal",
            help="IP or hostname of the MusicPal device (default: %(default)s)",
        )
        parser.add_argument(
            "-u",
            "--username",
            default="admin",
            help="username for HTTP authorization (default: %(default)s)",
        )
        parser.add_argument(
            "-p",
            "--password",
            default="admin",
            help="password for HTTP authorization (default: %(default)s)",
        )
        parser.add_argument(
            "-d",
            "--debug",
            action="store_true",
            help="print additional output for debugging",
        )
        parser.add_argument(
            "-l",
            "--list",
            action=PrintCommandsExit,
            help="print list available API commands and exit",
        )
        parser.add_argument(
            "command",
            default="state",
            nargs="?",
            help="command for sending to the MusicPal device (default: %(default)s)",
        )
        parser.add_argument(
            "args", nargs="*", help="(optional) arguments for given command"
        )
        args = parser.parse_args()

        # select appropriate API call for command
        command_trf = command_map.get(args.command)
        if not command_trf:
            print(f'Unknown command "{args.command}"')
            sys.exit(1)
        r = command_trf(args)
        if args.debug:
            print(f"{r.url = }, {r.status_code = }")

        # parse API call output (and possibly print it)
        soup = bs4.BeautifulSoup(r.content, "lxml")
        if args.command == "state" and soup.state:
            for state_tag in soup.state.children:
                if isinstance(state_tag, bs4.Tag) and state_tag.name:
                    print(f"{state_tag.name:18}: {state_tag.string}")
        elif args.command == "favorites":
            if not len(args.args):
                for i, fav_tag in enumerate(soup.find_all(class_="table_alt1")):
                    if not isinstance(fav_tag, bs4.Tag):
                        continue
                    name = fav_tag.find(attrs={"name": f"name_{i}"})
                    if name and isinstance(name, bs4.Tag):
                        print(f'{i}: {name["value"]}')
            else:
                i = args.args[0]
                name = soup.find(attrs={"name": f"name_{i}"})
                if name and isinstance(name, bs4.Tag):
                    print(f'Playing favorite {i}: {name["value"]}')
                else:
                    print(f"Favorite {i} does not exist")
        elif args.command == "info":
            content = soup.find(class_="content_content")
            if content:
                for info_tag in content:
                    if isinstance(info_tag, bs4.element.Comment) or (
                        isinstance(info_tag, bs4.Tag)
                        and (info_tag.name in ["div"] or not info_tag.string)
                    ):
                        continue
                    string = (
                        info_tag.string if info_tag.string else ""
                    ).strip()
                    if not len(string):
                        continue
                    if info_tag.name == "span":
                        print(f" {string}", end="")
                    elif info_tag.name in ["b"]:
                        print(f"\n{string}")
                    else:
                        if (
                            isinstance(info_tag.previous_sibling, bs4.Tag)
                            and info_tag.previous_sibling.name == "span"
                        ):
                            print(f" {string}")
                        else:
                            print(f"{string}")
        elif args.command == "log":
            if soup.textarea:
                print(
                    (
                        soup.textarea.string if soup.textarea.string else ""
                    ).strip()
                )
        elif args.command == "now_playing":
            content = soup.find(class_="content_content")
            if content:
                for s in content.stripped_strings:
                    print(s)
        elif args.command == "uptime":
            _, seconds = (soup.string if soup.string else "").strip().split()
            delta = timedelta(seconds=float(seconds))
            print(f"Uptime: {delta}")
        elif args.command == "volume_set":
            volume = len(soup.find_all("img", src="/images/volume_on.gif")) - 1
            print(f"Volume: {volume}")
        else:
            if args.debug:
                print(r.text)

        # just raise error if status_code != 200
        r.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        raise SystemExit(e)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
