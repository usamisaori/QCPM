from time import *


class Timer:
    """
        call:
        1.  with Timer(description):
                todo...
        2.  timer = Timer()
            timer.start(description)
            todo...
            timer.end()
    """

    # Increase after enter()
    # Decrease when exit()
    indent = 0

    def __init__(self, description=''):
        self.description = description
        self.duration = 0
        self.silence = False
    
    def start(self, description=''):
        if description != '':
            self.description = description

        self.silence or print('-' * (self.__class__.indent * 4) + \
            'Start Timer: [{}]'.format(self.description))
        
        self.start_time = time()
        self.__class__.indent += 1

    def end(self):
        self.__class__.indent -= 1

        self.duration = time() - self.start_time
        self.silence or print('-' * (self.__class__.indent * 4) + \
            f'End Timer [{self.description}]:  {self.duration}\n')

    # context management protocol
    ## __enter__ and __exit__ 
    def __enter__(self):
        self.start()
    
    def __exit__(self, exec_type, exec_value, traceback):
        self.end()