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
    process_list: list[Process] = []

    # Get scheduler details from input
    print("# Enter Scheduler Details #")
    num_procs: int = input_int_loop(0, 12)
    q1_allot: int = input_int_loop(4, float('inf'))
    q2_allot: int = input_int_loop(0, float('inf'))
    context_switch: int = input_int_loop(-1, 6)

    # Get process details from input and put into a list
    print(f"# Enter {num_procs} Process Details #")
    for _ in range(num_procs):
        process_list.append(create_new_process(input()))

    print("# Scheduling Results #")