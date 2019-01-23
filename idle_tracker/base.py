import datetime
from xprintidle import idle_time
import zenipy
import pickle
import os
import logging
from utils import setup_logger


class Plugin(object):
    def __init__(self, *args, **kwargs):
        self.min_idle = self.to_seconds(minutes=1)
        self.max_idle = self.to_seconds(minutes=9)
        self.verbosity = True
        self.delay = 0
        self.idle_time = idle_time()
        self.datetime = datetime.datetime.now()
        self.require_setup = False
        self.save_file_location = os.path.join('savefiles',
                                               '%s.pickle' % self.__name__)
        setup_logger(self.__name__, self.__name__, logging.DEBUG)
        self.logger = logging.getLogger(self.__name__)

    def action(self,):
        pass

    def overwrite_base(self):
        pass

    @staticmethod
    def to_seconds(seconds=0, minutes=0, hours=0, days=0):
        return datetime.timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds
        ).total_seconds()

    def notify(self, title, message, expire_time=None,
               urgent=0):
        title = str(self.__name__) + ': ' + title
        if not urgent:
            zenipy.message(title=title, text=message, timeout=expire_time or 0)
        elif urgent == 1:
            zenipy.warning(title=title, text=message, timeout=expire_time or 0)
        else:
            zenipy.error(title=title, text=message, timeout=expire_time or 0)

    def check_run(self):
        return self.max_idle <= self.idle_time >= self.min_idle

    def check_if_can_run(self, last):
        return last > self.datetime + datetime.timedelta(seconds=self.delay)

    def load(self):
        saved = None
        if os.path.isfile(self.save_file_location):
            with open(self.save_file_location, 'rb') as f:
                saved = pickle.load(f)
        return saved

    def save(self, saved):
        with open(self.save_file_location, 'wb') as f:
            pickle.dump(saved, f)

    def setup(self):
        pass

    def __str__(self):
        return self.__name__
