import threading
import json
from queue import Queue

class Database:
    def __init__(self, path):
        self.path = path
        self.running = False
        self.queue = Queue(maxsize=20)
        try:
            open(self.path, 'x').close()
            f = open(self.path, 'w')
            f.write('{}')
            f.close()
        except:
            pass

    def read_json(self):
        f = open(self.path, 'r')
        data = json.load(f)
        f.close()
        return data

    def write_json(self, data):
        f = open(self.path, 'w')
        json.dump(data, f)
        f.close()

    def perform_actions(self):
        while True:
            action = self.queue.get()
            command, arg, result = action
            if command == 'quit':
                return
            data = self.read_json()
            match command:
                case 0: # dump
                    result.put(data)
                case 1: # read
                    keys = arg
                    for key in keys:
                        data = data[key]
                    result.put(data)
                case 2: # initialize
                    self.write_json(arg)
                    result.put(None)
                case 3: # write
                    value, keys = arg[0], arg[1]
                    exec_str = 'data'
                    for key in keys:
                        exec_str += "['{}']".format(key)
                    exec_str += '=value'
                    exec(exec_str)
                    self.write_json(data)
                    result.put(None)
                case 4: # clear
                    self.write_json({})
                    result.put(None)
                case 5: # remove
                    keys = arg
                    exec_str = 'data'
                    for key in keys[0:-1]:
                        exec_str += "['{}']".format(key)
                    exec_str += '.pop(keys[-1])'
                    exec(exec_str)
                    self.write_json(data)
                    result.put(None)

    def perform_action(self, command, arg):
        if self.running:
            action = [command, arg, Queue(maxsize=1)]
            self.queue.put(action)
            return action[2].get()
        else:
            raise ValueError()

    def start(self):
        threading.Thread(target=self.perform_actions).start()
        self.running = True

    def stop(self):
        self.running = False
        self.queue.put(['quit', None, None])

    def dump(self):
        return self.perform_action(0, None)

    def read(self, *keys):
        return self.perform_action(1, keys)
    
    def initialize(self, value):
        return self.perform_action(2, value)

    def write(self, value, *keys):
        return self.perform_action(3, (value, keys))

    def clear(self):
        return self.perform_action(4, None)

    def remove(self, *keys):
        return self.perform_action(5, keys)