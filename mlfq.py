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
from sys import argv
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

class RoundRobinAlgorithm(SchedulerAlgorithm):
    def __init__(self):
        self._priority_queue = list()

    def sort(self) -> None:
        pass

class FCFSAlgorithm(SchedulerAlgorithm):
    def __init__(self):
        self._priority_queue = list()

    def sort(self) -> None:
        pass

class SJFAlgorithm(SchedulerAlgorithm):
    def __init__(self):
        self._priority_queue = list()

    def sort(self):
        sorted(self._priority_queue, key = lambda p: p.burst_remaining)

@dataclass
class MFLQScheduler:
    cpu: Process
    switch_time_pass: int = field(default=0) # tracks time elapsed for context switch
    process_list: list[Process] = field(default_factory=list)
    arriving_list: list[Process] = field(default_factory=list)
    io_list: list[Process] = field(default_factory=list)
    finished_list: list[Process] = field(default_factory=list) # list for processes returning from CPU
    priority_queues: list[SchedulerAlgorithm] = field(default_factory=list)
    time: int = field(default=0)
    idle: bool = False

    """Function to get Arriving processes"""
    def get_arriving_processes(self) -> None:
        for process in self.process_list:
            if process.arrival_time == self.time:
                self.arriving_list.append(process)
        self.arriving_list = sorted(self.arriving_list, key = lambda p: p.name)

    """Function to add Arriving processes to the Queue"""
    def arriving_to_queue(self) -> None:
        while self.arriving_list:
            self.priority_queues[0].add_process(self.arriving_list.pop(0))

        for proc in self.finished_list:
            self.priority_queues[0].add_process(proc)
        self.finished_list = []

    """Function to move Queued process to CPU"""
    def queue_to_CPU(self) -> None:
        self.switch_time_pass = 0
        if self.priority_queues[0].priority_queue and self.cpu.name == "":
            self.cpu = self.priority_queues[0].remove_process()

        elif self.priority_queues[1].priority_queue and self.cpu.name == "":
            self.cpu = self.priority_queues[1].remove_process()

        elif self.priority_queues[2].priority_queue and self.cpu.name == "":
            self.cpu = self.priority_queues[2].remove_process()

    def sort_priority_queues(self) -> None:
        for pq in self.priority_queues:
            pq.sort()

    """Function to add to proper queue"""
    def add_to_queue(self, queue_num: int, proc: Process) -> None:
        self.priority_queues[queue_num-1].add_process(proc)

    """Function to empty the cpu"""
    def empty_cpu(self) -> None:
        self.switch_time_pass = 0
        self.cpu = Process("", -1, [-1], [-1], -1)

    """Function to move a process down a queue"""
    def move_process_down_queue(self) -> None:
        queue_no = self.current_process.queue_number
        self.current_process.q1_run_counter = 0
        self.add_to_queue(queue_no+1, self.cpu)
        self.current_process.queue_number += 1 # update queue number
        self.empty_cpu() # empty cpu

    """Function to move a process to the io"""
    def move_to_io(self) -> None:
        self.current_process.quantum_passed = 0 # reset so it can be used for io count
        self.current_process.q1_run_counter = 0
        self.current_process.update_io()
        self.io_list.append(self.current_process)
        self.empty_cpu # empty cpu

    """Function to remove a process from the I/O"""
    def remove_from_io(self, proc:Process) -> None:
        self.io_list.remove(proc)

    def try_idle(self) -> bool:
        if (self.io_list != [] or scheduler.current_process.name != ""):
            self.idle = False
            return False

        for pq in self.priority_queues:
            if pq.priority_queue != []:
                self.idle = False
                return False

        self.idle = True
        return True


    """Function to get the current process"""
    @property
    def current_process(self) -> Process:
        return self.cpu

    """Function to get the list of processes in the I/O, sorted alphabetically"""
    @property
    def in_io(self) -> list[Process]:
        return sorted(self.io_list, key = lambda x: x.name)


class View:
    def __init__(self, scheduler:MFLQScheduler) -> None:
        self._scheduler = scheduler

    def get_scheduler_details(self) -> tuple[list[int], float]:
        """Get scheduler details from user details"""
        allotments:list[int] = list()
        num_procs:int = 0
        context_switch_duration = 0

        # Case : input.txt file was provided
        if (len(argv) > 1):
            file_path = Path(argv[1])
            if not path.exists(file_path) or ".txt" not in argv[1]:
                raise FileNotFoundError("Input: not a valid input file")
            try:
                with open(file_path, "r") as input:
                    # no input validation is done
                    num_procs = int(input.readline().strip("\n "))
                    allotments.append(int(input.readline().strip("\n ")))
                    allotments.append(int(input.readline().strip("\n ")))
                    context_switch_duration = int(input.readline().strip("\n "))
                    self._get_process_details(num_procs, input)
                    return allotments, context_switch_duration
            except:
                raise FileNotFoundError("Input: unable to open provided input text file")

        # Case : no input.txt file was provided
        print("# Enter Scheduler Details #")
        num_procs = self._input_int_loop(0, 12)
        allotments.append(self._input_int_loop(4, float('inf'))) # q1 time allotment
        allotments.append(self._input_int_loop(0, float('inf'))) # q2 time allotment
        context_switch_duration = self._input_int_loop(-1, 6)
        self._get_process_details(num_procs)
        return allotments, context_switch_duration

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
            for _ in range(num_procs):
                self._scheduler.process_list.append(Process.create_new_process(input_file.readline().strip("\n ")))
            return

        # Case : no input.txt file was provided
        print(f"# Enter {num_procs} Process Details #")
        for _ in range(num_procs):
            self._scheduler.process_list.append(Process.create_new_process(input()))

    def print_scheduler_log(self) -> None:
        """Prints the events from timestamp t=0 until all processes finish running"""
        print("# Scheduling Results #")

    def print_scheduler_metrics(self) -> None:
        """Prints the turnaround time per process, average turnaround time, waiting time"""
        ...
        sub_total = 0
        for proc in sorted(self._scheduler.process_list, key=lambda x: x.name):
            sub_total += proc.get_turnaround_time()
            print(f"Turn-around time for Process {proc.name} : {proc.print_turnaround_time()}")

        print(f"Average Turn-around time = {round(sub_total/len(self._scheduler.process_list),2)} ms")

        for proc in sorted(self._scheduler.process_list, key=lambda x: x.name):
            print(f"Waiting time for Process {proc.name} : {proc.print_waiting_time()}")

    def print_arriving_processes(self) -> None:
        """ Prints the details of process, with an optional prefix """
        if self._scheduler.arriving_list != []:
            print(f"Arriving : [{self._proc_list_to_str(self._scheduler.arriving_list)}]")

    def _proc_list_to_str(self, lst: list[Process]) -> str:
        return ', '.join([proc.name for proc in lst])

    def print_done_processes(self, done_processes:list[Process]) -> None:
        print(f"At Time = {self._scheduler.time}")
        while(done_processes):
            print(f"{done_processes[0].name} DONE")
            done_processes.pop(0)

    def print_all_queues(self) -> None:
        print("Queues : ", end="")
        for _, elem in enumerate(self._scheduler.priority_queues):
            print(f"[{self._proc_list_to_str(elem.priority_queue)}]",end=";")
        print()

    def print_io(self) -> None:
        print(f"I/O : [{self._proc_list_to_str(self._scheduler.in_io)}]")

    def print_demotion(self, process_name: str) -> None:
        if process_name != "":
            print(f"{process_name} DEMOTED")

    def print_simulation_done(self) -> None:
        print("SIMULATION DONE\n")


class Controller:
    def __init__(self, view:View, scheduler:MFLQScheduler) -> None:
        self.view = view
        self.scheduler = scheduler

    def check_preemption(self, current_proc:Process, done_processes: list[Process], allotments: list[int], context_switch:int) -> None:
        # -- Q1 should be top priority, followed by Q2 then Q3
        process_demoted = ""
        min_queue_num = min(
            [idx+1 if queue else 4 for idx, queue in
            enumerate([pq.priority_queue for pq in self.scheduler.priority_queues])]
        )

        if min_queue_num < current_proc.queue_number:
            self.scheduler.add_to_queue(current_proc.queue_number, current_proc)
            self.scheduler.empty_cpu()
            self.scheduler.queue_to_CPU()

        # Move Queued Process to CPU if CPU is Empty
        if self.scheduler.cpu.name == "":
            self.scheduler.queue_to_CPU()
            current_proc = self.scheduler.current_process

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
                self.scheduler.remove_from_io(proc)

        # Remove context switch for start
        if self.scheduler.time == 0:
            self.scheduler.switch_time_pass = context_switch

        # Update Quantum for Process in CPU
        # -- only update after context switch
        prev_switch: int = scheduler.switch_time_pass

        if scheduler.switch_time_pass == context_switch:
            # context switch done
            scheduler.switch_time_pass = context_switch
            scheduler.current_process.quantum_passed += 1
        # elif scheduler.cpu.name == '':
        #     print("Case 2")
        #     # cpu is in idle mode, no context switch
        #     # -- to immediately satisfy previous condition
        #     scheduler.switch_time_pass = context_switch
        else:
            scheduler.switch_time_pass += 1

        scheduler.cpu.update_burst()
        scheduler.time = scheduler.time + 1

        # Print Queues
        view.print_all_queues()

        # CPU
        # -- if a context switch occured, no process is "in" the CPU
        if(prev_switch != scheduler.switch_time_pass):
            print("CPU : ")
        else:
            print(f"CPU : {scheduler.cpu.name}")

        # Print I/0
        if scheduler.io_list:
            view.print_io()

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
                scheduler.priority_queues[2].add_process(scheduler.cpu)

            scheduler.empty_cpu()

        # -- Case 3: process ran out of quantum (Q1)
        # ----- Reset quantum and put process at the end of Q1's RQ
        elif current_proc.quantum_passed == Q1_QUANTUM and current_proc.queue_number == 1 and current_proc.q1_run_counter == 0:
            current_proc.q1_run_counter += 1
            scheduler.finished_list.append(current_proc)
            # scheduler.queue_one.append(current_proc)
            scheduler.empty_cpu()

        # Print Demoted Process
        view.print_demotion(process_demoted)

        print()

    def run(self):
        self.view.print_scheduler_log()
        # Get scheduler details from input
        allotments:list[int] = []
        done_processes:list[Process] = []
        allotments, context_switch = view.get_scheduler_details()
        while scheduler.idle != True:
            """
            1) Check for arriving processes
            2) Move arriving processes to Queue One
            3) Check if CPU should be cleared (process is done/ran out of quantum)
            4) Move queued process to CPU if CPU is empty
            5) Check for I/O
            """
            self.view.print_done_processes(done_processes)
            self.scheduler.get_arriving_processes()
            self.view.print_arriving_processes()
            self.scheduler.arriving_to_queue()
            self.check_preemption(self.scheduler.current_process, done_processes, allotments, int(context_switch))
            self.scheduler.try_idle()
        view.print_simulation_done()
        view.print_scheduler_metrics()


if __name__ == "__main__":
    scheduler: MFLQScheduler = MFLQScheduler(priority_queues=[RoundRobinAlgorithm(), FCFSAlgorithm(), SJFAlgorithm()],cpu=Process("", -1, [-1], [-1], -1))
    view: View = View(scheduler)
    controller: Controller = Controller(view, scheduler)

    controller.run()


