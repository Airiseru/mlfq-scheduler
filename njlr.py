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
from __future__ import annotations
from typing import Protocol
from os import path
from io import TextIOWrapper
from sys import argv, maxsize
from pathlib import Path
from dataclasses import dataclass, field
from functools import reduce

# constants
Q1_QUANTUM: int = 4

@dataclass
class Process:
    """Class for each process"""
    name: str
    arrival_time: int
    cpu_burst: list[int]
    io_burst: list[int]
    q1_run_counter: int = field(default=0)
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

    @classmethod
    def create_new_process(cls, inp: str) -> Process:
        """Create an instance of Process using user input"""
        splitted_inp = inp.split(";")
        return Process(
            name =          splitted_inp[0],
            arrival_time =  int(splitted_inp[1]),
            cpu_burst =     [int(splitted_inp[i]) for i in range(2, len(splitted_inp)) if i%2==0], # even indices
            io_burst =      [int(splitted_inp[i]) for i in range(2, len(splitted_inp)) if i%2!=0] # odd indices
        )

class SchedulerAlgorithm(Protocol):
    _priority_queue:list[Process]

    def sort(self) -> None:
        ...

    def add_process(self, proc:Process) -> None:
        self._priority_queue.append(proc)
        self.sort()

    def remove_process(self, index:int=0) -> Process:
        return self._priority_queue.pop(index)

    @property
    def priority_queue(self) -> list[Process]:
        return self._priority_queue
    
    @property
    def get_queue(self) -> list[Process]:
        return self._priority_queue

class RoundRobinAlgorithm(SchedulerAlgorithm):
    def __init__(self):
        self._priority_queue = list()
    
    @property
    def get_queue(self) -> list[Process]:
        return self._priority_queue

    def sort(self) -> None:
        pass

class FCFSAlgorithm(SchedulerAlgorithm):
    def __init__(self):
        self._priority_queue = list()
    
    @property
    def get_queue(self) -> list[Process]:
        return self._priority_queue

    def sort(self) -> None:
        pass

class SJFAlgorithm(SchedulerAlgorithm):
    def __init__(self):
        self._priority_queue = list()
    
    @property
    def get_queue(self) -> list[Process]:
        return self._priority_queue

    def sort(self):
        sorted(self._priority_queue, key = lambda p: p.burst_remaining)

@dataclass
class MFLQScheduler:
    cpu: Process
    priority_queues: list[SchedulerAlgorithm]
    switch_time_pass: int = field(default=0) # tracks time elapsed for context switch
    process_list: list[Process] = field(default_factory=list)
    arriving_list: list[Process] = field(default_factory=list)
    io_list: list[Process] = field(default_factory=list)
    returning_from_cpu: list[Process] = field(default_factory=list) # list for processes returning from CPU
    done_processes: list[Process] = field(default_factory=list)
    allotments: list[int] = field(default_factory=list)
    time: int = field(default=0)
    
    context_switch_duaration: int = field(default=0)
    context_switch: bool = field(default=False)
    
    num_procs: int = field(default=0)
    finished_execution: list[Process] = field(default_factory=list)

    def _get_scheduler_details(self) -> None:
        """Get scheduler details from user details"""
        # Case : input.txt file was provided
        if (len(argv) > 1):
            file_path = Path(argv[1])
            if not path.exists(file_path) or ".txt" not in argv[1]:
                raise FileNotFoundError("Input: not a valid input file")
            try:
                with open(file_path, "r") as input:
                    # no input validation is done
                    self.num_procs = int(input.readline().strip("\n "))
                    self.allotments.append(int(input.readline().strip("\n ")))
                    self.allotments.append(int(input.readline().strip("\n ")))
                    self.context_switch_duration = int(input.readline().strip("\n "))
                    self._get_process_details(self.num_procs, input)
            except:
                raise FileNotFoundError("Input: unable to open provided input text file")

        # Case : no input.txt file was provided
        print("# Enter Scheduler Details #")
        self.num_procs = self._input_int_loop(0, 12)
        self.allotments.append(self._input_int_loop(4, float('inf'))) # q1 time allotment
        self.allotments.append(self._input_int_loop(0, float('inf'))) # q2 time allotment
        self.context_switch_duration = self._input_int_loop(-1, 6)
        self._get_process_details(self.num_procs)
    
    def _input_int_loop(self, min_inp: int, max_inp: float) -> int:
        """ Keep asking user for input until valid

        Arguments:
        min_inp -- minimum, exclusive
        max_inp -- maximum, exclusive

        """
        user_input = -5
        while (user_input < min_inp) or (user_input > max_inp):
            try:
                user_input = int(input(""))
            except ValueError:
                continue

        return user_input

    def _get_process_details(self, num_procs:int, input_file: TextIOWrapper | None = None) -> None:
        """Get all process details from user input and put into a list"""
        # Case : input.txt file was provided
        if input_file != None:
            for _ in range(self.num_procs):
                self.process_list.append(Process.create_new_process(input_file.readline().strip("\n ")))
            return

        # Case : no input.txt file was provided
        print(f"# Enter {self.num_procs} Process Details #")
        for _ in range(self.num_procs):
            self.process_list.append(Process.create_new_process(input()))
    
    """Function to get time"""
    @property
    def get_time(self) -> int:
        return self.time
    
    """Function to get Queues"""
    @property
    def get_queues(self) -> list[SchedulerAlgorithm]:
        return self.priority_queues
    
    """Function to get CPU"""
    @property
    def get_cpu(self) -> Process:
        return self.cpu
    
    """Function to get the list of processes in the I/O, sorted alphabetically"""
    @property
    def get_io(self) -> list[Process]:
        return sorted(self.io_list, key = lambda x: x.name)
    
    @property
    def get_arriving(self) -> list[Process]:
        return self.arriving_list
    
    @property
    def get_context_switch(self) -> bool:
        return self.context_switch
    
    @property 
    def get_done_processes(self) -> list[Process]:
        return self.done_processes
    
    @property
    def get_process_list(self) -> list[Process]:
        return self.process_list
    
    def update_time(self) -> None:
        self.time = self.time + 1
    
    """Function to get Arriving processes"""
    def update_arriving(self) -> None:
        for process in self.process_list:
            if process.arrival_time == self.time:
                self.arriving_list.append(process)
        self.arriving_list = sorted(self.arriving_list, key = lambda p: p.name)

    """Function to add Arriving processes to the Queue"""
    def arriving_to_queue(self) -> None:
        while self.arriving_list:
            self.priority_queues[0].add_process(self.arriving_list.pop(0))

        while self.returning_from_cpu:
            self.priority_queues[0].add_process(self.returning_from_cpu.pop(0))

    """Function to move Queued process to CPU"""
    def queue_to_cpu(self) -> None:
        # If Context Switching / CPU is not empty -> Do nothing
        if self.context_switch == True or self.cpu.name != "":
            return
                
        if self.priority_queues[0].priority_queue:
            self.cpu = self.priority_queues[0].remove_process()

        elif self.priority_queues[1].priority_queue:
            self.cpu = self.priority_queues[1].remove_process()

        elif self.priority_queues[2].priority_queue:
            self.cpu = self.priority_queues[2].remove_process()
            
    def run_cpu(self) -> None:
        # If Context Switching / CPU is not empty -> Do nothing
        if self.context_switch == True or self.cpu.name == "":
            self.switch_time_pass += 1
            return
        
        self.cpu.quantum_passed += 1
        self.cpu.update_burst()
        
    def run_cpu2(self) -> None:
        if self.cpu.burst_remaining == 0 and self.cpu.name != "":
            if self.cpu.idx >= len(self.cpu.io_burst):
                self.done_processes.append(self.cpu)
                self.finished_execution.append(self.cpu)
                self.cpu.completion_time = self.time + 1
            else: 
                self.move_to_io()
            
            self.empty_cpu()
        
        elif self.cpu.queue_number != 3 and self.cpu.quantum_passed == self.allotments[self.cpu.queue_number - 1]:
            process_demoted = self.cpu
            self.move_process_down_queue()
                
            self.empty_cpu()
            
        elif self.cpu.quantum_passed == Q1_QUANTUM and self.cpu.queue_number == 1 and self.cpu.q1_run_counter == 0:
            self.cpu.q1_run_counter += 1
            self.returning_from_cpu.append(self.cpu)
            
            self.empty_cpu()
                
    """Function to empty the cpu"""
    def empty_cpu(self) -> None:
        if self.context_switch_duration > 0:
            self.context_switch = True
        self.switch_time_pass = 0
        self.cpu = Process("", -1, [-1], [-1], -1)
  
    def clear_context_switch(self) -> None:
        if self.switch_time_pass >= self.context_switch_duration:
            self.context_switch = False
        
    def run_io(self) -> None:
        for proc in self.io_list:
            proc.quantum_passed += 1
            proc.update_io()
            
            if proc.io_remaining == 0:
                proc.idx += 1
                proc.quantum_passed = 0
                
                if proc.idx != len(proc.cpu_burst):
                    self.add_to_queue(proc.queue_number, proc)
                else:
                    self.done_processes.append(proc)
                    self.finished_execution.append(proc)
                    proc.completion_time = self.time + 1
                
                self.remove_from_io(proc)
            
    def sort_priority_queues(self) -> None:
        for pq in self.priority_queues:
            pq.sort()

    """Function to add to proper queue"""
    def add_to_queue(self, queue_num: int, proc: Process) -> None:
        self.priority_queues[queue_num-1].add_process(proc)


    """Function to move a process down a queue"""
    def move_process_down_queue(self) -> None:
        if self.cpu.queue_number <= 3:
            queue_no = self.cpu.queue_number
            self.cpu.q1_run_counter = 0
            self.add_to_queue(queue_no+1, self.cpu)
            self.cpu.queue_number += 1 # update queue number
        else:
            self.priority_queues[2].add_process(self.cpu)

    """Function to move a process to the io"""
    def move_to_io(self) -> None:
        self.cpu.quantum_passed = 0 # reset so it can be used for io count
        self.cpu.q1_run_counter = 0
        self.io_list.append(self.cpu)

    """Function to remove a process from the I/O"""
    def remove_from_io(self, proc:Process) -> None:
        self.io_list.remove(proc)
        
    def check_preemption(self) -> None:
        min_queue_num = min(
            [idx+1 if queue else 4 for idx, queue in
            enumerate([pq.priority_queue for pq in self.priority_queues])]
        )

        if min_queue_num < self.cpu.queue_number:
            self.add_to_queue(self.cpu.queue_number, self.cpu)
            self.empty_cpu()
            self.queue_to_cpu()

        # Move Queued Process to CPU if CPU is Empty
        if self.cpu.name == "":
            self.queue_to_cpu()
            
class View:
    def print_scheduler_log(self) -> None:
        """Prints the events from timestamp t=0 until all processes finish running"""
        print("# Scheduling Results #")

    def print_time(self, time: int) -> None:
        print(f"At Time = {time}")
        
    def print_all_queues(self, queues: list[SchedulerAlgorithm]) -> None:
        print(f"Queues : [{self._proc_list_to_str(queues[0].get_queue)}];[{self._proc_list_to_str(queues[1].get_queue)}];[{self._proc_list_to_str(queues[2].get_queue)}]")
        
    def print_cpu(self, context_switch: bool, cpu: Process) -> None:
        if context_switch == True: #context switch
            print(f"CPU : ")
        else:
            print(F"CPU : {cpu.name}")
            
    def print_io(self, io: list[Process]) -> None:
        print(f"I/O : [{self._proc_list_to_str(io)}]")

    def print_arriving(self, arriving: list[Process]) -> None:
        """ Prints the details of process, with an optional prefix """
        if arriving != []:
            print(f"Arriving : [{self._proc_list_to_str(arriving)}]")

    def print_scheduler_metrics(self, process_list: list[Process]) -> None:
        """Prints the turnaround time per process, average turnaround time, waiting time"""
        ...
        sub_total = 0
        for proc in sorted(process_list, key=lambda x: x.name):
            sub_total += proc.get_turnaround_time()
            print(f"Turn-around time for Process {proc.name} : {proc.print_turnaround_time()}")

        print(f"Average Turn-around time = {round(sub_total/len(process_list),2)} ms")

        for proc in sorted(process_list, key=lambda x: x.name):
            print(f"Waiting time for Process {proc.name} : {proc.print_waiting_time()}")

    def _proc_list_to_str(self, lst: list[Process]) -> str:
        return ', '.join([proc.name for proc in lst])

    def print_done_processes(self, done_processes:list[Process]) -> None:
        while(done_processes):
            print(f"{done_processes[0].name} DONE")
            done_processes.pop(0)
            

    def print_demotion(self, process_name: str) -> None:
        if process_name != "":
            print(f"{process_name} DEMOTED")

    def print_simulation_done(self) -> None:
        print("SIMULATION DONE\n")
    
class Controller:
    def __init__(self, view: View, model: MFLQScheduler) -> None:
        self.view = view
        self.model = model
      
    def run(self):
        self.view.print_scheduler_log()
        # Get scheduler details from input
        self.model._get_scheduler_details()
        
        ret_next = False
        while True: 
            # Print Time
            self.view.print_time(self.model.get_time)
            # Update Arriving
            self.model.update_arriving()
            self.view.print_arriving(self.model.get_arriving)
            self.view.print_done_processes(self.model.get_done_processes)
            # Move Arriving to Queue            
            self.model.arriving_to_queue()
            self.model.queue_to_cpu()
            
            self.model.check_preemption()
            self.view.print_all_queues(self.model.get_queues)
            self.view.print_cpu(self.model.get_context_switch, self.model.get_cpu)
            
            self.model.run_cpu()
            self.model.clear_context_switch()
            
            self.view.print_io(self.model.get_io)
            self.model.run_io()
            self.model.run_cpu2()
            print()
            
            # Increment Time
            self.model.update_time()
            
            #Really ugly ik but works for now
            if ret_next == True or self.model.time > 90:
                break
            if len(self.model.finished_execution) >= self.model.num_procs:
                ret_next = True
                
        view.print_simulation_done()
        view.print_scheduler_metrics(self.model.get_process_list)
        
if __name__ == "__main__":
    view: View = View()
    model: MFLQScheduler = MFLQScheduler(priority_queues=[RoundRobinAlgorithm(), FCFSAlgorithm(), SJFAlgorithm()] ,cpu=Process("", -1, [-1], [-1], -1))
    controller: Controller = Controller(view, model)

    controller.run()