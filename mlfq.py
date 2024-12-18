"""
PROJECT 1: MLFQ Scheduler in Python
CS140 THR/FQR

## Submitted By: ##
Denise Mae B. Dee
Nicholas John L. Reyes
Jopeth Bryan B. Seda
Kevin D. Trinidad

## Project Specifications ##
- Q1 (Top Priority Queue): RR with 4ms quantum
- Q2: FCFS
- Q3: SJF
- no priority boosting

Input:
- number of processes (0 > x >= 11)
- time allotment for Q1 (x >= 5)
- time allotment for Q2 (x > 0)
- time for context switch (0 >= x >= 5)
- process name; arrival time; CPU Burst 1; I/O Burst 1; CPU Burst 2; etc.

Output:
- print events that occur every time stamp (arriving process, processing finishing its total burst time, state of the ready queue, process currently running in the CPU, processes currently running their IO, process demotion)
- after all processes finish, print
    - turn-around time for each process (arranged alphabetically)
    - average turn-around time
    - waiting time for each process (arranged alphabetically)
"""
from dataclasses import dataclass, field

@dataclass
class Process:
    """Class for each process"""
    name: str
    arrival_time: int
    cpu_burst: list[int]
    io_burst: list[int]
    idx: int = field(default=0) # to know at which point of the burst the process is in
    quantum_passed: int = field(default=0) # for cpu and io (to know how much time the process used)
    burst_remaining: int = field(default=0)
    queue_number: int = field(default=1)
    completion_time: int = field(default=0)

    """Function to calculate the turnaround time of the process"""
    def get_turnaround_time(self) -> int:
        return self.completion_time - self.arrival_time
    
    """Function to get the turnaround time in a string format for printing"""
    def print_turnaround_time(self) -> str:
        return f"{self.completion_time} - {self.arrival_time} = {self.get_turnaround_time()} ms"
    
    """Function to calculate the waiting time"""
    def get_waiting_time(self) -> int:
        return self.get_turnaround_time() - sum(self.cpu_burst)
    
    """Function to get the waiting time in a string format for printing"""
    def print_waiting_time(self) -> str:
        return f"{self.get_waiting_time()} ms"

    """Function to update the time left for current burst"""
    def update_burst(self):
        self.burst_remaining = self.cpu_burst[self.idx] - self.quantum_passed

@dataclass
class Scheduler:
    cpu: Process
    # is_switch: bool = field(default=True)
    switch_time_pass: int = field(default=0)
    process_list: list[Process] = field(default_factory=list)
    arriving_list: list[Process] = field(default_factory=list)
    io_list: list[Process] = field(default_factory=list)
    queue_one: list[Process] = field(default_factory=list)
    queue_two: list[Process] = field(default_factory=list)
    queue_three: list[Process] = field(default_factory=list)
    time: int = field(default=0)
        
    """Function to get Arriving processes"""
    def get_arriving_processes(self):
        for process in self.process_list:
            if process.arrival_time == self.time:
                self.arriving_list.append(process) 
        self.arriving_list = sorted(self.arriving_list, key = lambda p: p.name)

    """Function to add Arriving processes to the Queue"""
    def arriving_to_queue(self):
        while self.arriving_list:
            self.queue_one.append(self.arriving_list.pop(0))

    """Function to move Queued process to CPU"""
    def queue_to_CPU(self):
        # self.is_switch = True
        self.switch_time_pass = 0
        if self.queue_one and self.cpu.name == "":
            self.cpu = self.queue_one.pop(0)

        elif self.queue_two and self.cpu.name == "":
            self.cpu = self.queue_two.pop(0)
            
        elif self.queue_three and self.cpu.name == "":
            self.cpu = self.queue_three.pop(0)

    """Function to sort the third queue"""
    def sort_queue_three(self):
        # sort the queue based on the shortest job first on current burst time
        self.queue_three = sorted(self.queue_three, key = lambda p: p.burst_remaining)

    """Function to add to proper queue"""
    def add_to_queue(self, queue_num: int, proc: Process):
        if queue_num == 1:
            self.queue_one.append(proc)
        
        elif queue_num == 2:
            self.queue_two.append(proc)
        
        else:
            self.queue_three.append(proc)
            self.sort_queue_three()

    """Function to empty the cpu"""
    def empty_cpu(self):
        self.switch_time_pass = 0
        self.cpu = Process("", -1, [-1], [-1], -1)
    
    """Function to move a process down a queue"""
    def move_process_down_queue(self):
        queue_no = self.current_process.queue_number
        self.add_to_queue(queue_no+1, self.cpu)
        self.current_process.queue_number += 1 # update queue number
        self.empty_cpu() # empty cpu

    """Function to move a process to the io"""
    def move_to_io(self):
        self.cpu.quantum_passed = 0 # reset so it can be used for io count
        self.io_list.append(self.cpu)
        self.empty_cpu # empty cpu
    
    """Function to get the current process"""
    @property
    def current_process(self) -> Process:
        return self.cpu

    """Function to get the list of processes in the I/O, sorted alphabetically"""
    @property
    def in_io(self):
        return sorted(self.io_list, key = lambda x: x.name)

"""Function to keep looping input until valid"""
def input_int_loop(min_inp: int, max_inp: float) -> int:
    user_input = -5
    while (user_input < min_inp) or (user_input > max_inp):
        try:
            user_input = int(input(""))
        except ValueError:
            continue

    return user_input

"""Function to process the input about process"""
def create_new_process(inp: str) -> Process:
    splitted_inp = inp.split(";")
    return Process(splitted_inp[0], int(splitted_inp[1]),
                   [int(splitted_inp[i]) for i in range(2, len(splitted_inp)) if i%2==0], # even indices
                   [int(splitted_inp[i]) for i in range(2, len(splitted_inp)) if i%2!=0]) # odd indices

def proc_list_to_str(lst: list[Process]):
    return ', '.join([proc.name for proc in lst])

if __name__ == "__main__":
    # "Global" Variables (temp)
    scheduler: Scheduler = Scheduler(Process("", -1, [-1], [-1], -1))
    Q1_QUANTUM = 4
    allotments = []

    # Get scheduler details from input
    print("# Enter Scheduler Details #")
    num_procs: int = input_int_loop(0, 12)
    # q1_allot: int = input_int_loop(4, float('inf'))
    # q2_allot: int = input_int_loop(0, float('inf'))
    allotments.append(input_int_loop(4, float('inf'))) # q1 time allotment
    allotments.append(input_int_loop(0, float('inf'))) # q2 time allotment
    context_switch: int = input_int_loop(-1, 6)

    # Get process details from input and put into a list
    print(f"# Enter {num_procs} Process Details #")
    for _ in range(num_procs):
        scheduler.process_list.append(create_new_process(input()))

    print("# Scheduling Results #")

    while (scheduler.time < 20): #Temporary condition of time < 10.
        print(f"At Time = {scheduler.time}")
        """
        1) Check for arriving processes
        2) Move arriving processes to Queue One
        3) Check if CPU should be cleared (process is done/ran out of quantum)
        4) Move queued process to CPU if CPU is empty
        5) Check for I/O
        """
        # Check for Arriving Processes
        scheduler.get_arriving_processes()

        # Print Arriving
        if scheduler.arriving_list:
            print(f"Arriving : [{proc_list_to_str(scheduler.arriving_list)}]") #Di ko knows how to print the array without the ''. #future worry
        
        # Move Arriving Processes to Queue One
        scheduler.arriving_to_queue()

        # Check if CPU should be cleared (process is done/ran out of quantum)
        current_proc: Process = scheduler.current_process
        process_demoted = ""

        # case 1: process is done
        if current_proc.idx > len(current_proc.cpu_burst) and current_proc.idx > len(current_proc.io_burst):
            # index > len(cpu_burst) essentially means that the process doesn't have to use the cpu anymore
            print(f"{scheduler.cpu.name} DONE") # print that process is done

            current_proc.completion_time = scheduler.time
            scheduler.empty_cpu()

        # case 2: process ran out of allotment
        elif current_proc.quantum_passed == allotments[current_proc.queue_number -1]:
            process_demoted = scheduler.cpu.name
            # case 2.1: process is not the last queue
            if current_proc.queue_number != 3:
                scheduler.move_process_down_queue()
            
            # case 2.2 process is in the last queue
            else:
                scheduler.queue_three.append(scheduler.cpu)
                scheduler.sort_queue_three()

            scheduler.empty_cpu()

        # case 3: process ran out of quantum (q1)
        elif current_proc.quantum_passed == Q1_QUANTUM and current_proc.queue_number == 1:
            scheduler.queue_one.append(current_proc)
            scheduler.empty_cpu()

        # case 4: process finished current cpu burst time
        elif current_proc.burst_remaining == 0 and current_proc.name != "":
            scheduler.move_to_io()
            scheduler.empty_cpu()

        # Move Queued Process to CPU if CPU is Empty
        if scheduler.cpu.name == "":
            scheduler.queue_to_CPU()

        # Handle I/O
        # 1. check if the io is done (add 1 to idx and move back to proper queue)
        # 2. if not done, add 1 to the quantum_passed

        # Update quantum
        # only update after context switch
        if scheduler.switch_time_pass == context_switch:
            scheduler.current_process.quantum_passed += 1
        # if cpu is in idle mode, no context switch
        elif scheduler.cpu.name == '':
            scheduler.switch_time_pass = context_switch
        else:
            scheduler.switch_time_pass += 1

        # Print Queues
        print(f"Queues : [{proc_list_to_str(scheduler.queue_one)}];[{proc_list_to_str(scheduler.queue_two)}];[{proc_list_to_str(scheduler.queue_three)}]")

        # CPU
        print(f"CPU : {scheduler.cpu.name}")
        
        # Print I/0
        if scheduler.io_list:
            print(f"I/O : [{proc_list_to_str(scheduler.in_io)}]")

        if process_demoted:
            print(f"{process_demoted} DEMOTED")

        print()
        scheduler.time = scheduler.time + 1
        scheduler.cpu.update_burst()

    print("SIMULATION DONE")