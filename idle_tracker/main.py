from pike.manager import PikeManager
from utils import PluginManagerManager, ROOTDIR
import os


def main():
    man = PluginManagerManager()
    with PikeManager([os.path.join(ROOTDIR, 'plugins')]) as mgr:
        classes = mgr.get_classes()

    for cls in classes:
        if cls.__name__ == 'Plugin':
            continue
        man.run_plugin(cls)


if __name__ == '__main__':
    main()


