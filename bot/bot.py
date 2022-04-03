#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------
# bot
# created 22.03.2022
# Thomas Kaulke, kaulketh@gmail.com
# https://github.com/kaulketh
# -----------------------------------------------------------

import json
import multiprocessing
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
from json import JSONDecodeError
from time import sleep

from .command import SubProcessCmd, CURL_UPDATE, CURL_SEND


class SimpleBot:

    def __init__(self, token, chat_id, handle_function, poll=5.0):
        self.__admin = chat_id
        self.__token = token
        self.__handle = handle_function
        self.__update_poll = poll

        (filename, line_number, function_name, text) = \
            traceback.extract_stack()[-2]
        self.__name = text[:text.find('=')].strip()
        sys.stdout.write(
            f"## Initialize '{self.__name}' as instance "
            f"of {self.__class__.__name__}.\n")

        self.__result = None
        self.__msg_text = None
        self.__msg = None
        self.__from = None
        self.__from_id = None
        self.__msg_id = 0
        self.__msg_storage = 0
        self.__loop = multiprocessing.Process(target=self._loop_func)
        self.__run()

    def __get_update(self):

        def read(update, key):
            """
            get value of any key in Json object
            """
            try:

                def found(_d: dict, _key: str):
                    for _k, _v in _d.items():
                        if _k == _key:
                            yield _v
                        elif isinstance(_v, dict):
                            for _val in found(_v, _key):
                                yield _val

                for k in found(update, key):
                    return k
            except (TypeError, StopIteration) as ts:
                sys.stderr.write(f"!! While searching for '{key}' in {update} "
                                 f"an error occurred:\n{ts}\n")
                self.stop()

        # cUrl
        response = SubProcessCmd(CURL_UPDATE, self.__token).out

        # decode response and load as JSON document
        try:
            response = json.loads(response.decode('utf-8').replace("'", '"'))
        except JSONDecodeError as jde:
            sys.stderr.write(f"!! While decoding '{response}' "
                             f"JSONDecodeError occurred:\n{jde}\n")
            self.stop()

        # get last of the returned results
        self.__result = read(response, "result")[-1]
        # extract text from last result
        self.__msg_text = read(self.__result, "text")
        # extract content parts
        self.__msg = read(self.__result, "message")
        self.__msg_id = read(self.__result, "message_id")
        self.__from = read(self.__msg, "from")
        self.__from_id = read(self.__from, "id")
        # noinspection LongLine
        return self.__result, self.__msg_text, self.__msg, self.__from, self.__from_id, self.__msg_id

    def __run(self):
        try:
            self.__loop.start()
            sys.stdout.write(
                f"## Bot is running... "
                f"API polling every {self.__update_poll} second(s)\n")
            self.send(self.__admin, "Bot is running...")
        except KeyboardInterrupt:
            sys.stderr.write(f"!! Program interrupted\n")
            self.stop()
        except Exception as e:
            sys.stderr.write(f"!! An error occurred: {e}\n")
            self.stop()

    def _loop_func(self):
        while True:
            # update
            self.update = self.update
            # if initial
            if self.__msg_storage == 0:
                self.__msg_storage = self.__msg_id
            # check for new message
            if self.__msg_id == self.__msg_storage:
                continue
            else:
                # store last msg id
                self.__msg_storage = self.__msg_id
                if self.__msg_text is not None:
                    # TODO: type exception!?
                    sys.stdout.write(
                        f">> Got message|"
                        f"{self.__msg_storage}|"
                        f"{self.__msg_text}|"
                        f"{self.__from_id}\n")
                    self.__handle(self)
                else:
                    # type exception!?
                    # ignore other then text
                    sys.stderr.write("!! Wrong content type!\n")
                    self.send(self.user_id, "Wrong content type!")
                    continue
            sleep(self.__update_poll)

    def send(self, chat_id, text):
        SubProcessCmd(CURL_SEND, self.__token, chat_id, text)
        sys.stdout.write(f"<< Sent Message|"
                         f"{text}|"
                         f"{chat_id}\n")

    def stop(self):
        if self.__loop is not None:
            if self.__loop.is_alive():
                self.__loop.terminate()
        self.send(self.__admin, "Bot stopped.")
        del self
        sys.stdout.write("## Bot stopped.\n")

    @property
    def update(self):
        """
        Since Python >3.2, the stdlib- concurrent.futures module provides a
        higher-level API for threading, including passing return values or
        exceptions from a worker thread to the main thread:
        """
        with ThreadPoolExecutor() as executor:
            results = executor.submit(self.__get_update).result()
            return results

    @update.setter
    def update(self, results):
        # noinspection LongLine
        self.__result, self.__msg_text, self.__msg, self.__from, self.__from_id, self.__msg_id = results

    @property
    def result(self):
        return self.update[0]

    @property
    def text(self):
        return self.update[1]

    @property
    def message(self):
        return self.update[2]

    @property
    def user(self):
        return dict(self.update[3])

    @property
    def user_id(self):
        return self.update[4]

    @property
    def message_id(self):
        return self.update[5]


if __name__ == '__main__':
    pass
