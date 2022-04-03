#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import subprocess
import sys

SUDO_REBOOT = "sudo reboot"
CURL_SEND = "sudo curl -s -o /dev/nul/ " \
            "-X  POST \"https://api.telegram.org/bot{}/" \
            "sendMessage?chat_id={}&text={}\""
'''string format required: (bot token, chat id, message text)'''

CURL_UPDATE = "sudo curl -s -X GET \"https://api.telegram.org/bot{}/getUpdates\"" #?offset=1000000000000\""

'''string format required: bot token'''


class _Cmd():
    def __init__(self, cmd: str, *args):
        self._out = None
        try:
            self._cmd = cmd.format(*args) if args is not None else cmd
        except Exception as e:
            self._exept(e,
                        "An error occurred while formatting command arguments:")
        self._execute()

    def _execute(self):
        pass

    def _exept(self, e, txt):
        sys.stderr.write(
            f"!! {txt} {e}\n")
        exit(0)

    @property
    def out(self):
        return self._out


class SubProcessCmd(_Cmd):
    def __init__(self, cmd: str, *args):
        super().__init__(cmd, *args)

    def _execute(self):
        #try:
        proc = subprocess.Popen(self._cmd, stdout=subprocess.PIPE, shell=True)
        self._out = proc.communicate()[0]
        #except Exception as e:
        #    self._exept(e, "An error occurred while starting a subprocess:")


class OsCmd(_Cmd):
    def __init__(self, cmd: str, *args):
        super().__init__(cmd, *args)

    def _execute(self):
        try:
            self._out = os.system(self._cmd)
        except Exception as e:
            self._exept(e, "An error occurred while executing OS command:")


if __name__ == '__main__':
    pass
