import threading
import multiprocessing

class SuperVisor:
    def __init__(self, param1, param2, use_processes, number_equipment):
        self.param1 = param1
        self.param2 = param2
        self.use_processes = use_processes
        self.number_eq = number_equipment
        #self.process_init(self)

    def process_init(self):
        if self.use_processes == True:
            processes = []
            arglist = ["process1", "process2"]
            for i in range(self.number_eq):
                process = multiprocessing.Process(target=self.equipment_process, args=(arglist[i],))
                print(process)
                processes.append(process)
                process.start()
            for process in range(len(processes)):
                process.join()
        else:
            print("arg not propogating")
    def equipment_process(self, arg1):
        print(arg1)

