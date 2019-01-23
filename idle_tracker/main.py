from pike.manager import PikeManager
from utils import PluginManagerManager


def main():
    man = PluginManagerManager()
    with PikeManager(['plugins']) as mgr:
        classes = mgr.get_classes()

    for cls in classes:
        if cls.__name__ == 'Plugin':
            continue
        man.run_plugin(cls)


if __name__ == '__main__':
    main()


