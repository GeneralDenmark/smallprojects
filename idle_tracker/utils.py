# will contain utilities for idle_tracker,
import datetime
import pickle
import os
import logging
import logging.handlers

ROOTDIR = os.path.abspath(os.path.dirname(__file__))


class PluginManagerManager:
    def __init__(self):
        setup_logger('plugin_manager_manager', 'plugin_manager_manager',
                     logging.DEBUG)
        self.logger = logging.getLogger('plugin_manager_manager')
        self.save_place = os.path.join(ROOTDIR, 'savefiles',
                                       '_SetupManager.pickle')
        self.saved = self.load()
        if not self.saved:
            self.saved = self.default_dict()

    @staticmethod
    def default_dict():
        return {
            'minutes_between': 30,
        }

    def load(self):
        saved = None
        if os.path.isfile(self.save_place):
            with open(self.save_place, 'rb') as f:
                saved = pickle.load(f)
            self.logger.debug('Loaded file correctly')
        return saved

    def save(self, saved):
        with open(self.save_place, 'wb') as f:
            pickle.dump(saved, f)
        self.logger.debug('Saved file correctly')

    def check_for_setup(self, cls):
        self.logger.debug('Starting setup sequence for (%s)' % cls.__name__)
        if (cls.require_setup and cls.__name__ not in self.saved
            or cls.__name__ in self.saved
            and self.saved[cls.__name__].get('last_modified', 0) <
            datetime.datetime.now() + datetime.timedelta(
                minutes=-self.saved.get('minutes_between', 30))):

            cls.setup(cls)
            self.saved[cls.__name__] = {
                'last_modified': datetime.datetime.now(),
                'failed':False
            }
            self.logger.debug('Setup completed for (%s)' % cls.__name__)
            self.save(self.saved)

    def run_plugin(self, cls):
        try:
            self.logger.debug('Trying to run function "action" in class (%s)'
                              % cls.__name__)
            possible_edit = None
            cls.__init__(cls)
            cls.overwrite_base(cls)
            self.check_for_setup(cls)
            if cls.check_run(cls):
                self.logger.debug('Running action on class (%s)'
                                  % cls.__name__)
                possible_edit = cls.action(cls)
        except Exception as e:
            import traceback
            self.logger.error('Error in class [%s] -> %s\n%s' % (
                cls.__name__, e, traceback.format_tb(e.__traceback__)))
            if cls.require_setup and cls.__name__ in self.saved:
                self.saved[cls.__name__]['failed'] = True
        else:
            if possible_edit:
                self.logger.debug('Saving changes made for (%s)'
                                  % cls.__name__)
                cls.save(cls, possible_edit)

    def __str__(self):
        return self.__name__


def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(ROOTDIR, 'log', '%s.log' % log_file),
        when='midnight', backupCount=5)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    l.propagate = False
    l.setLevel(level)
    l.addHandler(stream_handler)
    l.addHandler(file_handler)
