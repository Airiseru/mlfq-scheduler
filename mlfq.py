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
- print events that occur every time stamp (arriving process, processing finishing its total burst time, state of the ready queue, process currently running in the CPU, processes currently runnign their IO, process demotion)
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

@dataclass
class Scheduler:
    cpu: Process
    process_list: list[Process]
    arriving_list: list[Process]
    queue_one: list[Process]
    queue_two: list[Process]
    queue_three: list[Process]
    time: int
        
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
        if self.queue_one and self.cpu.name == "":
            self.cpu = self.queue_one.pop(0)

        elif self.queue_two and self.cpu.name == "":
            self.cpu = self.queue_two.pop(0)
            
        elif self.queue_three and self.cpu.name == "":
            self.cpu = self.queue_three.pop(0)

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

if __name__ == "__main__":
    # "Global" Variables (temp)
    scheduler: Scheduler = Scheduler(Process("", -1, [-1], [-1], -1), [], [], [], [], [], 0)

    # Get scheduler details from input
    print("# Enter Scheduler Details #")
    num_procs: int = input_int_loop(0, 12)
    q1_allot: int = input_int_loop(4, float('inf'))
    q2_allot: int = input_int_loop(0, float('inf'))
    context_switch: int = input_int_loop(-1, 6)

    # Get process details from input and put into a list
    print(f"# Enter {num_procs} Process Details #")
    for _ in range(num_procs):
        scheduler.process_list.append(create_new_process(input()))

    print("# Scheduling Results #")

    while (scheduler.time < 10): #Temporary condition of time < 10.
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
        # Move Arriving Processes to Queue One
        scheduler.arriving_to_queue()
        #Check if CPU should be cleared (process is done/ran out of quantum)

        # Move Queued Process to CPU if CPU is Empty
        scheduler.queue_to_CPU()
        # Handle I/O

        # Print Arriving
        if scheduler.arriving_list != []:
            print(f"Arriving : {[proc.name for proc in scheduler.arriving_list]}") #Di ko knows how to print the array without the ''. #future worry

        # Print Queues
        print(f"Queues : {[proc.name for proc in scheduler.queue_one]} ; {[proc.name for proc in scheduler.queue_two]} ; {[proc.name for proc in scheduler.queue_three]}")

        # CPU
        print(f"CPU : {scheduler.cpu.name}")
        
        # Print I/0

        print()
        scheduler.time = scheduler.time + 1

    print("SIMULATION DONE")