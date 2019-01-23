from base import Plugin
from zenipy import question, entry

import os


class LockingTool(Plugin):
    def overwrite_base(self):
        self.require_setup = True
        self.delay = self.to_seconds(minutes=10)

    def setup(self):
        self.logger.info('Initializing setup')
        saved = {
            'is_command': False,
            'path_exec': '',
            'last_ran': self.datetime,
        }
        is_command = question('Are you using a command or a file?',
                              text='In order for this plugin to '
                                   'execute locked '
                                   'screen, it needs to know how you '
                                   'do this. '
                                   'Are you using a command, '
                                   'press yes')
        saved['is_command'] = is_command
        saved['path_exec'] = entry(
            text='What is the {} you are using?'.format(
                'command' if is_command else 'lock script location'),
            title='Please insert the {} you are using'.format(
                'command' if is_command else 'lock script location'))
        if not is_command and not os.path.isfile(saved['path_exec']):
            self.logger.error('You did not specify a valid file to execute')
            return
        self.logger.debug('Finished setting up LockingTool')
        self.save(self, saved)

    def action(self):
        self.logger.debug('Initiating the action')
        saved = self.load(self)
        if self.check_if_can_run(self, saved['last_ran']):
            self.logger.debug('Activated lockscreen')
            saved['last_ran'] = self.datetime
            if saved['is_command']:
                os.popen(saved['path_exec'])
            else:
                os.popen("sh " + saved['path_exec'])
            return saved