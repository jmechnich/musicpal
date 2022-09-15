[![PyPI versio](https://img.shields.io/pypi/v/musicpal)](https://pypi.org/project/musicpal/)
[![PyPi format](https://img.shields.io/pypi/format/musicpal)](https://pypi.org/project/musicpal/)
[![PyPI license](https://img.shields.io/pypi/l/musicpal)](https://pypi.org/project/musicpal/)
[![PyPi weekly downloads](https://img.shields.io/pypi/dw/musicpal)](https://pypi.org/project/musicpal/)

## musicpal

Command line interface for remote controlling a Freecom MusicPal.

### Usage

```
usage: musicpal [--help] [-h HOSTNAME] [-u USERNAME] [-p PASSWORD] [-d] [-l]
                [command] [args ...]

Command line client for the Freecom MusicPal.

positional arguments:
  command               command for sending to the MusicPal device (default: state)
  args                  (optional) arguments for given command

optional arguments:
  --help                show this help message and exit
  -h HOSTNAME, --hostname HOSTNAME
                        IP or hostname of the MusicPal device (default: musicpal)
  -u USERNAME, --username USERNAME
                        username for HTTP authorization (default: admin)
  -p PASSWORD, --password PASSWORD
                        password for HTTP authorization (default: admin)
  -d, --debug           print additional output for debugging
  -l, --list            print list available API commands and exit
```

Available commands are:

  * `menu_collapse` - close menu on display
  * `play` - play media file from (http) url
  * `power_down` - suspend device
  * `power_up` - wake-up device
  * `show_list` - display a list, arguments are the list items
  * `show_msg_box` - display a message box
  * `favorites` -  list favorites if called without arguments, supply favorite index (starting from 0) to select
  * `info` - retrieve network information 
  * `next_song` - skip to next favorite / playlist item
  * `now_playing` - WIP
  * `play_pause` - toggle playback
  * `show_clock` - display clock
  * `volume_dec` - turn volume down
  * `volume_inc` - turn volume up
  * `volume_set` - print current volume if called without arguments, supply value between 0 and 20 to set
  * `state` - display various information about device state

### Links

  * https://musicpal.mcproductions.nl/ - various information about the device
