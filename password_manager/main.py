import zenipy
import os
import sys
import logging
import json
import datetime
import re
from pprint import pprint


def help_message():
    sys.exit("""

Call as: sudo %s [-h|-s<settings file>|-d|-v|-q]

Arguments:
    -h: Display this message and exit
    -s: Custom location of the settings file
    -d: Dryrun, do not change anything
    -v: Verbose, display more information
    -q: Don't save settings
    
Author: AGW 

    """)


def main(settings):
    dry_run = settings['session_settings']['dry_run']
    def_width = settings['sys_config']['def_width']
    def_height = settings['sys_config']['def_height']
       
    password = zenipy.password(title='Indtast dit nye password')
    logging.debug('password was %s' % password)
    if not password:
        logging.info('Did not get a new password,'
                     ' exitting as there is no reason to change anything')
    cifs_for_root = settings['usr_config']['cifs_file_for_root']

    if cifs_for_root and not zenipy.question(
        width=def_width, height=def_height, text=
        'I got %s as a file in my system, is this correct?' % cifs_for_root):
            cifs_for_root = None
    if not cifs_for_root:
        cifs_for_root = zenipy.entry(
            title='Where is the location of the cif file?',
            height=def_height, width=def_width)
    logging.debug('path to cif is %s' %cifs_for_root)
    next_update = zenipy.calendar(day=1, month=,
        text='How many months till next reminder?', width=def_width,
        height=def_height) or settings['usr_config']['default_months_between']
    logging.debug('Got {date}/{month} for when to do next update'
                  .format(date=next_update.day, month=next_update.month + 1))
    if not dry_run:
        settings['sys_config'] = write_to_cifs(
            settings['sys_config'], cifs_for_root, password)
    settings['usr_config'], edited = update_settings(
        settings['usr_config'], cifs_for_root)
    logging.debug('Updated settings successfully ')
    if edited:
        logging.debug('Some changes occured')
        settings['sys_config']['last_settings_edit'] = \
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    if not dry_run:
        schedule_next(
            ' 10 8 {date} {month} * '.format(
                date=next_update.day,
                month=next_update.month + 1,
            ))
    return settings


def schedule_next(new_scheduled_event):
    path_to_self = 'python3' + os.path.abspath(__file__)
    os.popen('crontab -l > tmp_crontab.txt')
    tmp_crontab = 'tmp_crontab.txt'
    aut_postfix = '# AUTOGEN: DO NOT TOUCH!'
    with open(tmp_crontab, 'r') as fin:
        current_crontab = fin.read().split('\n')
    
    if any(x for x in current_crontab if aut_postfix in x):
        with open(tmp_crontab, 'w') as fout:
            for cr in current_crontab:
                if aut_postfix in cr:
                    current_crontab[current_crontab.index(cr)] = \
                        new_scheduled_event + path_to_self + aut_postfix
                fout.write(cr + '\n')
    else:
        with open(tmp_crontab, 'a') as fout:
            fout.write(new_scheduled_event + path_to_self + aut_postfix)
    logging.debug('Updated crontab')
    os.popen('crontab ' + tmp_crontab)
    os.popen('rm ' + tmp_crontab)
    logging.debug('Removed tmp crontab')


def write_to_cifs(sys_config, path_to_cifs, new_password):
    logging.debug('Writing to path_to_cifs %s' %path_to_cifs)
    
    with open(path_to_cifs, 'rt') as fin:
        current_cifs = fin.read().split('\n')

    if any(x for x in current_cifs if 'password=' in x):
        with open(path_to_cifs, 'wt') as fout:
            for line in current_cifs:
                logging.debug(line + '=>' + re.sub(r'^password=.*', 
                                  'password=' + new_password, line))
                fout.write(re.sub(r'^password=.*', 
                                  'password=' + new_password, line))
                logging.debug()
    else:
        logging.debug('.cifs had no password, so creating it '
                      'at the end of the file')
        with open(path_to_cifs, 'a') as fout:
            fout.write('password='+new_password)
    
    logging.debug('Completed writing to file')
    sys_config['last_run'] = \
        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return sys_config

def update_settings(usr_config, cifs_file_for_root):
    edited = False
    if usr_config['cifs_file_for_root'] != cifs_file_for_root:
        edited = True
        usr_config['cifs_file_for_root'] = cifs_file_for_root
        
    return usr_config, edited
    
    
def default_config(settings_location):
    DEFAULT_CONFIG={
        'usr_config': {
            'cifs_file_for_root': '',  # Where the .cifs file is located
        },
        'sys_config': {
            'def_width': 500,
            'def_height': 300,
            'settings_path': settings_location,
            'last_settings_edit': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'default_months_between': '3',
            'last_run': '',
        },
        'session_settings':{
            'dry_run': False,
        },
    }
    with open(settings_location, 'w') as f:
          json.dump(DEFAULT_CONFIG, f)      


def save_config(settings):
    settings = reset_session_settings(settings)
    with open(settings['sys_config']['settings_path'], 'w') as f:
        json.dump(settings, f)
    
    
def reset_session_settings(settings):
    settings['session_settings']['dry_run'] = False
    return settings
  
  
if __name__ == '__main__':
    
    settings_location = ''
    if '-h' in sys.argv:
        help_message()
    if not os.geteuid() == 0:
        sys.exit("\nOnly root can run this script\n")
    if '-v' in sys.argv:
        logging.basicConfig(format="%(levelname)s: %(message)s", 
                            level=logging.DEBUG)
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s")
    
    if '-s' in sys.argv:
        tmp_settings_location = sys.argv[sys.argv.index('-s') + 1]
        if tmp_settings_location.startswith('-'): 
            logging.error('You didn\'t specify a path for the settings file')
            exit(1)
        elif not os.path.exists(settings_location):
            logging.error('Settings file does not exsist')
            exit(1)
        else:
            settings_location = tmp_settings_location
    if '-q' in sys.argv:
        SAVESETTINGS = False
    if not settings_location.endswith('.set'):
        settings_location += 'settings.set'
    if not os.path.exists(settings_location):
        default_config(settings_location)
    
    with open(settings_location) as f:
        settings = json.load(f)
    if '-d' in sys.argv:
        settings['session_settings']['dry_run'] = True
    pprint(settings)
    settings = main(settings)
    if '-q' not in sys.argv:
        save_config(settings)
