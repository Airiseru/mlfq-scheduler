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
    io_remaining: int = field(default=0)
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

    """Function to update the time left for current I/O"""
    def update_io(self):
        self.io_remaining = self.io_burst[self.idx] - self.quantum_passed

@dataclass
class Scheduler:
    cpu: Process
    # is_switch: bool = field(default=True)
    switch_time_pass: int = field(default=0) # tracks time elapsed for context switch
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
        self.current_process.quantum_passed = 0 # reset so it can be used for io count
        self.current_process.update_io()
        self.io_list.append(self.current_process)
        self.empty_cpu # empty cpu
    
    """Function to remove a process from the I/O"""
    def remove_from_io(self, proc:Process):
        self.io_list.remove(proc)

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
    return Process(
        name =          splitted_inp[0],
        arrival_time =  int(splitted_inp[1]),
        cpu_burst =     [int(splitted_inp[i]) for i in range(2, len(splitted_inp)) if i%2==0], # even indices
        io_burst =      [int(splitted_inp[i]) for i in range(2, len(splitted_inp)) if i%2!=0] # odd indices
    ) 

def proc_list_to_str(lst: list[Process]):
    return ', '.join([proc.name for proc in lst])

if __name__ == "__main__":
    # "Global" Variables (temp)
    scheduler: Scheduler = Scheduler(Process("", -1, [-1], [-1], -1))
    Q1_QUANTUM = 4
    allotments = []
    done_processes = []

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

    while (
        scheduler.time <= 200 and (         # REMOVE THIS
        scheduler.time == 0 or (
        scheduler.queue_one != [] or
        scheduler.queue_two != [] or
        scheduler.queue_three != [] or
        scheduler.io_list != [] or
        scheduler.current_process.name != ""
        ))
    ):
        print(f"At Time = {scheduler.time}")
        while(done_processes):
            print(f"{done_processes[0].name} DONE")
            done_processes.pop(0)
        
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
            print(f"Arriving : [{proc_list_to_str(scheduler.arriving_list)}]")
        
        # Move Arriving Processes to Queue One
        scheduler.arriving_to_queue()

        current_proc: Process = scheduler.current_process
        process_demoted = ""

        # Check for Preemption
        # -- Q1 should be top priority, followed by Q2 then Q3
        min_queue_num = min(
            [idx+1 if queue else 4 for idx, queue in 
            enumerate([scheduler.queue_one, scheduler.queue_two, scheduler.queue_three])]
        )

        if min_queue_num < current_proc.queue_number:
            scheduler.add_to_queue(current_proc.queue_number, current_proc)
            scheduler.empty_cpu()
            scheduler.queue_to_CPU()

        # Check if CPU should be cleared (process is done/ran out of quantum)
        # -- Case 1: process finished current cpu burst time
        if current_proc.burst_remaining == 0 and current_proc.name != "":
            if  current_proc.idx >= len(current_proc.io_burst): # process ends after consuming its last burst
                done_processes.append(scheduler.cpu) # put process to DONE queue
                current_proc.completion_time = scheduler.time
                scheduler.empty_cpu()
            else: # process not done yet; move to i/o
                scheduler.move_to_io()
                scheduler.empty_cpu()
        
        # -- Case 2: process ran out of allotment
        # ----- The process should be demoted, except if
        # ----- it's in the bottommost queue already 
        elif current_proc.quantum_passed == allotments[current_proc.queue_number -1]:
            process_demoted = scheduler.cpu.name
            # Case 2.1: process is not the last queue
            if current_proc.queue_number != 3:
                scheduler.move_process_down_queue()
            
            # Case 2.2: process is in the last queue
            else:
                scheduler.queue_three.append(scheduler.cpu)
                scheduler.sort_queue_three()

            scheduler.empty_cpu()

        # -- Case 3: process ran out of quantum (Q1)
        # ----- Reset quantum and put process at the end of Q1's RQ
        elif current_proc.quantum_passed == Q1_QUANTUM and current_proc.queue_number == 1:
            scheduler.queue_one.append(current_proc)
            scheduler.empty_cpu()

        # Move Queued Process to CPU if CPU is Empty
        if scheduler.cpu.name == "":
            scheduler.queue_to_CPU()

        # Handle I/O
        # -- 1. Add 1 to quantum_passed
        # -- 2. Check if the I/O is done 
        for proc in scheduler.io_list:
            proc.quantum_passed += 1
            proc.update_io()

            # Check if the I/O is done
            if proc.io_remaining == 0:
                proc.idx += 1
                proc.quantum_passed = 0

                # Check if there's still remaining CPU burst time for the process
                if proc.idx != len(proc.cpu_burst): 
                    scheduler.add_to_queue(proc.queue_number, proc)
                else: # no more bursts => DONE
                    done_processes.append(proc)
                    proc.completion_time = scheduler.time
                scheduler.remove_from_io(proc)
                
        # Update Quantum for Process in CPU
        # -- only update after context switch
        if scheduler.switch_time_pass == context_switch:
            # context switch done
            scheduler.current_process.quantum_passed += 1
        elif scheduler.cpu.name == '':
            # cpu is in idle mode, no context switch
            # -- to immediately satisfy previous condition
            scheduler.switch_time_pass = context_switch
        else:
            scheduler.switch_time_pass += 1

        # Print Queues
        print(f"Queues : \
                [{proc_list_to_str(scheduler.queue_one)}];\
                [{proc_list_to_str(scheduler.queue_two)}];\
                [{proc_list_to_str(scheduler.queue_three)}]"
            )

        # CPU
        print(f"CPU : {scheduler.cpu.name}")
        
        # Print I/0
        if scheduler.io_list:
            print(f"I/O : [{proc_list_to_str(scheduler.in_io)}]")

        # Print Demoted Process
        if process_demoted:
            print(f"{process_demoted} DEMOTED")

        print()
        scheduler.time = scheduler.time + 1
        scheduler.cpu.update_burst()

    print("SIMULATION DONE\n")

    # Print Parameters
    sub_total = 0
    for proc in sorted(scheduler.process_list, key=lambda x: x.name):
        sub_total += proc.get_turnaround_time()
        print(f"Turn-around time for Process {proc.name} : {proc.print_turnaround_time()}")
    
    print(f"Average Turn-around time = {round(sub_total/len(scheduler.process_list),2)} ms")
    
    for proc in sorted(scheduler.process_list, key=lambda x: x.name):
        print(f"Waiting time for Process {proc.name} : {proc.print_waiting_time()}")
