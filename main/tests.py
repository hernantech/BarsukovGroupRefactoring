from supervisor_V1 import SuperVisor
import multiprocessing


def main():
    multiprocessing.freeze_support()
    object = SuperVisor("hello", "hell999", True, 2)
    print(object.process_init())


main()