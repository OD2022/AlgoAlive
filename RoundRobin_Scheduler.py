from ReadOnlyDict import ReadOnlyDict
from Process import Process
from GanttPanel import GanttPanel



class RoundRobin_Scheduler:
    def __init__(self, time_quantum):
        self.ready_queue = []
        self.waiting_queue = []
        self.time_quantum = time_quantum
        self.clock = 0
        self.current_process = None
        self.final_stats = ReadOnlyDict()


    def add_process(self, process):
        self.waiting_queue.append(process)
        self.waiting_queue.sort(key=lambda x: x.arrival_time)

    def execute_next_process(self):        
        self.waiting_queue.sort(key=lambda p: p.arrival_time)
        index = 0
        while index < len(self.waiting_queue):
            if self.waiting_queue[index].arrival_time <= self.clock:  
                self.ready_queue.append(self.waiting_queue.pop(index))
            else:
                index += 1
        
        for process in self.ready_queue:  
            if process.remaining_time < 1:
                self.ready_queue.remove(process)

        if(self.current_process == None):
            if len(self.ready_queue) == 0:
                self.clock += 1
                self.current_process = Process(0, 0, 0, 'White')
                return self.current_process
            if len(self.ready_queue) > 0:
                self.current_process = self.ready_queue.pop(0)
                self.clock = self.current_process.arrival_time
                self.current_process.begin_exec_time = self.clock
                self.clock += (min(self.current_process.remaining_time, self.time_quantum))
                self.current_process.execute(min(self.current_process.remaining_time, self.time_quantum))
                return self.current_process

        elif(self.current_process.process_id == 0 and len(self.ready_queue) == 0):
            self.clock +=1
            return self.current_process
        
        elif(self.current_process.process_id == 0 and len(self.ready_queue) > 0):
            self.current_process = self.ready_queue.pop(0)
            self.current_process.begin_exec_time = self.clock
            self.clock += (min(self.current_process.remaining_time, self.time_quantum))
            self.current_process.execute(min(self.current_process.remaining_time, self.time_quantum))
            return self.current_process
        
        if (self.current_process.remaining_time > 0):
                if len(self.ready_queue) > 0:
                   ##Removing from ready queue
                   self.current_process.preempted_time = self.clock
                   self.ready_queue.append(self.current_process)

                   ##Setting a new current process
                   self.current_process = self.ready_queue.pop(0)
                   self.current_process.begin_exec_time = self.clock
                   
                   self.clock = self.clock + (min(self.time_quantum, self.current_process.remaining_time))
                   self.current_process.execute(min(self.time_quantum, self.current_process.remaining_time))
                   return self.current_process

                elif(len(self.ready_queue) == 0 and len(self.waiting_queue) > 0):
                    self.current_process.begin_exec_time = self.clock
                    self.current_process.execute(1)
                    self.clock +=1
                    return self.current_process

                elif(len(self.ready_queue) == 0 and len(self.waiting_queue) == 0):
                    self.current_process.begin_exec_time = self.clock
                    self.clock += self.current_process.remaining_time
                    self.current_process.execute(self.current_process.remaining_time)
                    return self.current_process


        if (self.current_process.remaining_time == 0):
                ##Updating final statistics once the process is done
                process_id = f"P{self.current_process.process_id}"
                process_information = {
                    "arrival_time" :  self.current_process.arrival_time,
                    "execution_time" : self.current_process.execution_time,
                    "completion_time" : self.clock
                }
                self.final_stats[process_id] = process_information

                if len(self.ready_queue) > 0:
                   self.current_process.preempted_time = self.clock
                   self.ready_queue.append(self.current_process)
                   ##Setting a new current process
                   self.current_process = self.ready_queue.pop(0)
                   self.current_process.begin_exec_time = self.clock
                   self.clock += (min(self.time_quantum, self.current_process.remaining_time))
                   self.current_process.execute(min(self.time_quantum, self.current_process.remaining_time))
                   return self.current_process
                    
                elif(len(self.ready_queue) == 0 and len(self.waiting_queue) > 0):
                    self.current_process.begin_exec_time = self.clock
                    self.current_process.execute(0)
                    self.clock +=1
                    return self.current_process

                elif(len(self.ready_queue)==0 and len(self.waiting_queue)==0):
                    return None


    def calculate_statistics(self):
        total_waiting_time = sum(process.waiting_time for process in self.final_stats)
        average_waiting_time = total_waiting_time / len(self.final_stats) if len(self.final_stats) > 0 else 0
        return total_waiting_time, average_waiting_time

    def create_gantt_chart_panel(self, parent):
        return GanttPanel(parent, self)
    
    def print_final_stats(self):
        return self.final_stats