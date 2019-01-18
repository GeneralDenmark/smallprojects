from xprintidle import idle_time
from pike.manager import PikeManager
from datetime import datetime
import os


def main():
    pass


with PikeManager(['plugins']) as mgr:
    classes = mgr.get_classes()

for cls in classes:
    try:
        cls.idle_time = idle_time
        cls.__time = datetime.now()
        cls.action(cls)
    except Exception as e:
        print ('error in %s\n%s' %(cls, e))
if __name__ == '__main__':
    pass


