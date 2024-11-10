from GanttPanel import GanttPanel
from Process import Process
from ReadOnlyDict import ReadOnlyDict
from RoundRobin_Scheduler import RoundRobin_Scheduler

class MLFQ_Scheduler:
    def __init__(self):
        self.rr_queue1 = RoundRobin_Scheduler(2)
        self.rr_queue2 = RoundRobin_Scheduler(4)
        self.fcfs_queue = []
        self.final_stats = ReadOnlyDict()
        self.fcfs_final_stats = {}
        self.clock = 0
        self.received_quantum_rr1 = []
        self.received_quantum_rr2 = []

    def add_process(self, process):
        self.rr_queue1.add_process(process)
        for process in self.rr_queue1.waiting_queue:
            process.currentQueue = 1

    def move_processes_queue1(self):
        ##Ordering First RR queue
        if len(self.received_quantum_rr1) > 0:
            for process in self.received_quantum_rr1:
                if process is not None  and process.remaining_time > 0:
                    self.demote_process(process, 2, 1)

    def move_processes_queue2(self):
        ##Ordering Second RR Queue
        if len(self.received_quantum_rr2) > 0:
            for process in self.received_quantum_rr2:
                if process is not None  and process.remaining_time > 0:
                    self.demote_process(process, 3, 2)


    def move_processes_fcfs_queue(self):
        for process in self.fcfs_queue:
                if process.is_input_output == True:
                    self.promote_process(process, 1, 3)

    def promote_process(self, promoted_process, new_queue_index, old_queue_index):
        if new_queue_index == 1:
            promoted_process.currentQueue = new_queue_index
            self.rr_queue1.ready_queue.append(promoted_process)
        if old_queue_index == 3:
            for process in self.fcfs_queue:
                if  (process.process_id == promoted_process.process_id):
                     self.fcfs_queue.remove(process)


    def demote_process(self, demoted_process,  new_queue_index, old_queue_index):
        if new_queue_index == 2:
            demoted_process.currentQueue = new_queue_index
            self.rr_queue2.ready_queue.append(demoted_process)
            if old_queue_index == 1:
                for process in self.rr_queue1.ready_queue:
                    if  (process.process_id == demoted_process.process_id):
                        self.rr_queue1.ready_queue.remove(process)

        if new_queue_index == 3:
            demoted_process.currentQueue = new_queue_index
            self.fcfs_queue.append(demoted_process)
            if old_queue_index == 2:
                for process in self.rr_queue2.ready_queue:
                    if  (process.process_id == demoted_process.process_id):
                        self.rr_queue2.ready_queue.remove(process)


    def execute_next_process(self):
        self.move_processes_queue1()
        self.move_processes_queue2()
        self.move_processes_fcfs_queue()
        
        if  (self.clock == 0  or len(self.rr_queue1.ready_queue) > 0):
            process_to_exec = self.rr_queue1.execute_next_process()
            self.received_quantum_rr1.append(process_to_exec)
            self.clock = self.rr_queue1.clock
            if process_to_exec != None:
                return process_to_exec 
        
        elif(len(self.rr_queue1.ready_queue) == 0) and (len(self.rr_queue1.waiting_queue) > 0):
            process_to_exec = self.rr_queue1.execute_next_process()
            self.received_quantum_rr1.append(process_to_exec)
            self.clock = self.rr_queue1.clock
            if process_to_exec != None:
                return process_to_exec
          
        elif(len(self.rr_queue1.ready_queue) == 0 and len(self.rr_queue1.waiting_queue) == 0) and (len(self.rr_queue2.ready_queue) > 0):
            self.rr_queue2.clock = self.clock  
            self.rr_queue2.current_process = self.rr_queue2.ready_queue.pop(0)
            process_to_exec = self.rr_queue2.execute_next_process()
            self.received_quantum_rr2.append(process_to_exec)
            self.clock = self.rr_queue2.clock
            if process_to_exec != None:  
                return process_to_exec
            if process_to_exec == None:

                if(len(self.fcfs_queue) > 0):
                    process_to_exec = self.fcfs_queue[0]


                    if self.clock < process_to_exec.arrival_time:
                        process_to_exec.begin_exec_time = self.clock
                        process_to_exec.execute(0)
                        self.clock += 1
                        return process_to_exec
                    

                    if  self.clock >= process_to_exec.arrival_time:
                        process_to_exec.begin_exec_time = self.clock
                        self.clock += process_to_exec.remaining_time
                        process_id = f"P{process_to_exec.process_id}"
                        process_information = {
                            "arrival_time" :  process_to_exec.arrival_time,
                            "execution_time" : process_to_exec.execution_time,
                            "completion_time" : self.clock
                        }

                        self.fcfs_final_stats[process_id] = process_information
                        process_to_exec.execute(process_to_exec.remaining_time)
                        self.fcfs_queue.pop(0)

                        self.final_stats.update(self.rr_queue1.final_stats)
                        self.final_stats.update(self.rr_queue2.final_stats)
                        self.final_stats.update(self.fcfs_final_stats)

                        if process_to_exec != None:  
                            return process_to_exec
                else:
                    return None
          
    def create_gantt_chart_panel(self, parent):
        return GanttPanel(parent, self)