class Process:
    def __init__(self, process_id, arrival_time, execution_time, color):
        self.process_id = process_id
        self.arrival_time = arrival_time
        self.begin_exec_time = 0
        self.preempted_time = arrival_time
        self.execution_time = execution_time
        self.remaining_time = execution_time
        self.overstayed = False
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        self.alloted_time = 0
        self.color = color
        self.is_input_output = False
        self.currentQueue = "_"

    def execute(self, time_quantum=None):
        if time_quantum is None:
            self.remaining_time = 0
        else:
            self.remaining_time -= time_quantum
            self.alloted_time = time_quantum
            if self.remaining_time < 0:
                self.remaining_time = 0
        self.waiting_time += 1