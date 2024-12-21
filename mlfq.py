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
- always prioritize top queue
"""
from __future__ import annotations
from typing import Protocol
from os import path
from io import TextIOWrapper
from sys import argv
from pathlib import Path
from dataclasses import dataclass, field

### CONSTANTS ###
Q1_QUANTUM: int = 4

@dataclass
class Process:
    """Class for each Process"""
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
        return self.get_turnaround_time() - sum(self.cpu_burst) - sum (self.io_burst)

    """Function to get the waiting time in a string format for printing"""
    def print_waiting_time(self) -> str:
        return f"{self.get_waiting_time()} ms"

    """Function to update the time left for current burst"""
    def update_burst(self):
        self.burst_remaining -= 1

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

    @classmethod
    def default(cls) -> Process:
        return Process("",-1,[-1],[-1])


class SchedulerAlgorithm(Protocol):
    """Protocol for Scheduler"""
    _priority_queue: list[Process]

    def sort(self) -> None:
        ...

    def add_process(self, proc: Process) -> None:
        self._priority_queue.append(proc)
        self.sort()

    def add_process_start(self, proc: Process) -> None:
        self._priority_queue = [proc] + self._priority_queue

    def dequeue_process(self, index:int=0) -> Process:
        return self._priority_queue.pop(index)

    @property
    def priority_queue(self) -> list[Process]:
        return self._priority_queue

class RoundRobinAlgorithm(SchedulerAlgorithm):
    """Round Robin Scheduler Class"""
    def __init__(self, quantum: int):
        self._priority_queue = list()
        self._quantum = quantum

    def sort(self) -> None:
        pass

class FCFSAlgorithm(SchedulerAlgorithm):
    """First Come First Served Scheduler Class"""
    def __init__(self):
        self._priority_queue = list()

    def sort(self) -> None:
        pass

class SJFAlgorithm(SchedulerAlgorithm):
    """Shortest Job First Scheduler Class"""
    def __init__(self):
        self._priority_queue = list()

    def sort(self) -> None:
        self._priority_queue = sorted(self._priority_queue, key = lambda p: (p.burst_remaining, p.name))


@dataclass
class MLFQScheduler:
    cpu: Process
    switch_time_pass: int = field(default=0) # tracks time elapsed for context switch
    process_list: list[Process] = field(default_factory=list)
    arriving_list: list[Process] = field(default_factory=list)
    io_list: list[Process] = field(default_factory=list)
    finished_processes: list[Process] = field(default_factory=list) # tracks processes that are done with their burst
    priority_queues: list[SchedulerAlgorithm] = field(default_factory=list)
    time: int = field(default=0)
    is_idle: bool = field(default=True)

    """Function to add time"""
    @property
    def add_time(self) -> None:
        self.time += 1

    """Function to check if scheduler is done"""
    @property
    def is_finished(self) -> bool:
        return (len(self.finished_processes) == len(self.process_list))

    """Function to get arriving processes"""
    def get_arriving_processes(self) -> None:
        for process in self.process_list:
            if process.arrival_time == self.time:
                self.arriving_list.append(process)

        self.arriving_list = sorted(self.arriving_list, key = lambda p: p.name)

    """Function to add recently arrived processes to the queue"""
    def add_arriving_to_queue(self) -> None:
        while self.arriving_list:
            self.priority_queues[0].add_process(self.arriving_list.pop(0))

    """Function to move a Queued Process to CPU"""
    def queue_to_CPU(self) -> None:
        old_process = self.current_process

        if self.priority_queues[0].priority_queue and self.cpu.name == "":
            self.cpu = self.priority_queues[0].dequeue_process()

        elif self.priority_queues[1].priority_queue and self.cpu.name == "":
            self.cpu = self.priority_queues[1].dequeue_process()

        elif self.priority_queues[2].priority_queue and self.cpu.name == "":
            self.cpu = self.priority_queues[2].dequeue_process()

        if old_process != self.current_process:
            self.switch_time_pass = 0 # Reset context switch counter

    """Function to add a process to proper queue"""
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
        self.current_process.quantum_passed = 0
        self.add_to_queue(queue_no+1, self.cpu)
        self.current_process.queue_number += 1 # update queue number
        self.empty_cpu() # empty cpu

    """Function to move a process to the io"""
    def move_to_io(self, demoted: bool) -> None:
        if (demoted):
            self.current_process.queue_number += 1
        self.cpu.quantum_passed = 0 # reset so it can be used for io count
        self.cpu.q1_run_counter = 0
        self.cpu.update_io()
        self.io_list.append(self.cpu)
        self.empty_cpu() # empty cpu

    """Function to remove a process from the I/O"""
    def remove_from_io(self, proc:Process) -> None:
        self.io_list.remove(proc)

    """Function to get the current process"""
    @property
    def current_process(self) -> Process:
        return self.cpu

    """Function to get the list of processes in the I/O, sorted alphabetically"""
    @property
    def in_io(self) -> list[Process]:
        return sorted(self.io_list, key = lambda x: x.name)

class View:
    def __init__(self, scheduler: MLFQScheduler) -> None:
        self._scheduler = scheduler

    """Function to get the details about the scheduler"""
    def get_scheduler_details(self) -> tuple[list[int], int]:
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

        sub_total = 0
        for proc in sorted(self._scheduler.process_list, key=lambda x: x.name):
            sub_total += proc.get_turnaround_time()
            print(f"Turn-around time for Process {proc.name} : {proc.print_turnaround_time()}")

        print(f"Average Turn-around time = {round(sub_total/len(self._scheduler.process_list),2)} ms")

        for proc in sorted(self._scheduler.process_list, key=lambda x: x.name):
            print(f"Waiting time for Process {proc.name} : {proc.print_waiting_time()}")

    def print_timestamp(self) -> None:
        print(f"At Time = {self._scheduler.time}")

    def print_arriving_processes(self) -> None:
        """ Prints the details of process, with an optional prefix """
        if self._scheduler.arriving_list != []:
            print(f"Arriving : [{self._proc_list_to_str(self._scheduler.arriving_list)}]")

    def _proc_list_to_str(self, lst: list[Process]) -> str:
        return ', '.join([proc.name for proc in lst])

    def print_done_processes(self, done_processes:list[Process]) -> None:
        while(done_processes):
            print(f"{done_processes[0].name} DONE")
            done_processes.pop(0)

    def print_all_queues(self) -> None:
        print("Queues : ", end="")
        for idx, elem in enumerate(self._scheduler.priority_queues):
            if idx == (len(self._scheduler.priority_queues) - 1):
                print(f"[{self._proc_list_to_str(elem.priority_queue)}]")
            else:
                print(f"[{self._proc_list_to_str(elem.priority_queue)}]",end=";")

    def print_cpu(self, proc_name: str = "") -> None:
        print(f"CPU : {proc_name}")

    def print_io(self) -> None:
        print(f"I/O : [{self._proc_list_to_str(self._scheduler.in_io)}]")

    def print_demotion(self, process_name: str) -> None:
        if process_name != "":
            print(f"{process_name} DEMOTED")

    def print_simulation_done(self) -> None:
        print("SIMULATION DONE\n")

    def print_newline(self) -> None:
        print()

class Controller:
    def __init__(self, view: View, scheduler: MLFQScheduler) -> None:
        self.view = view
        self.scheduler = scheduler
        self.done_processes: list[Process] = list()
        self.finished_quantum: list[Process] = list()
        self.finished_io: list[Process] = list()
        self.min_quantum_iters: int = 0

    """Function for 'preemption'"""
    def get_topmost_process(self) -> None:
        # Find minimum queue number
        min_queue_num = min(
            [idx+1 if queue else 4 for idx, queue in
            enumerate([pq.priority_queue for pq in self.scheduler.priority_queues])]
        )

        # If there's a process in a higher queue, load that process
        if min_queue_num < self.scheduler.cpu.queue_number:
            self.scheduler.add_to_queue(self.scheduler.cpu.queue_number, self.scheduler.cpu)
            self.scheduler.empty_cpu()
            self.scheduler.queue_to_CPU()

        # For the case when there's more than one process in queue 3
        if min_queue_num == 3 and self.scheduler.cpu.queue_number == 3:
            try:
                next_in_line = scheduler.priority_queues[min_queue_num-1].priority_queue[0]
            except:
                next_in_line = None

            # If there is more than one process in queue 3
            if next_in_line != None:

                # Check if the first process in the queue has a lesser burst time or is alphabetically "less" than the current
                if (next_in_line.burst_remaining < scheduler.cpu.burst_remaining) or (next_in_line.burst_remaining == scheduler.cpu.burst_remaining and next_in_line.name < scheduler.cpu.name):
                    self.scheduler.add_to_queue(self.scheduler.cpu.queue_number, self.scheduler.cpu)
                    self.scheduler.empty_cpu()
                    self.scheduler.queue_to_CPU()

        # If CPU is still empty, load a process from queue
        if self.scheduler.cpu.name == "":
            self.scheduler.queue_to_CPU()

    """Function to run the CPU for one timestamp"""
    def run_one_cpu_quantum(self) -> None:
        self.scheduler.cpu.quantum_passed += 1
        self.scheduler.cpu.update_burst()

    """Function to check if process finished quantum"""
    def check_process_quantum(self) -> None:
        current_proc = self.scheduler.cpu

        if (current_proc.quantum_passed%Q1_QUANTUM) == 0 and current_proc.queue_number == 1 and current_proc.q1_run_counter < self.min_quantum_iters and current_proc.quantum_passed != current_proc.cpu_burst[current_proc.idx]:
            current_proc.q1_run_counter += 1
            self.finished_quantum.append(current_proc)
            self.scheduler.empty_cpu()

    """Function to run the IO for one timestamp"""
    def run_one_io_quantum(self) -> None:
        for proc in self.scheduler.io_list:
            proc.quantum_passed += 1
            proc.update_io()

    """Function to check which processes are done with IO and get them (sorted alphabetically)"""
    def check_proc_in_io(self) -> list[Process]:
        final_lst:list[Process] = []
        idx_to_remove:list[int] = []

        for idx, proc in enumerate(self.scheduler.io_list):
            if proc.io_remaining == 0:
                proc.idx += 1
                proc.quantum_passed = 0

                # Check if there's still remaining CPU burst time for the process
                if proc.idx != len(proc.cpu_burst):
                    self.set_burst_remaining(proc, proc.idx)
                    final_lst.append(proc)
                else:
                    # No more bursts indicates that the process is done
                    self.done_processes.append(proc)
                    self.scheduler.finished_processes.append(proc)
                    proc.completion_time = self.scheduler.time

                idx_to_remove.append(idx)

        # Remove the finished IO's from the list
        self.scheduler.io_list = [proc for idx, proc in enumerate(self.scheduler.io_list) if idx not in idx_to_remove]

        return sorted(final_lst, key = lambda p: p.name)

    """Function to update the process' current remaining burst"""
    def set_burst_remaining(self, proc: Process, idx: int) -> None:
        proc.burst_remaining = proc.cpu_burst[idx]

    def run(self) -> None:
        # Other variables
        demoted_process: str = ""
        process_ran_name: str = ""
        view = self.view
        scheduler = self.scheduler
        sched_done = False
        demoted = False

        # Get scheduler details from input
        allotments, context_switch = view.get_scheduler_details()

        # Define the minimum number of times a process can run in queue 1 based on allotment and quantum
        if allotments[0] % Q1_QUANTUM != 0:
            self.min_quantum_iters = allotments[0] // Q1_QUANTUM
        else:
            self.min_quantum_iters = (allotments[0] - 1) // Q1_QUANTUM

        # Set initial burst remaining
        for proc in self.scheduler.process_list:
            self.set_burst_remaining(proc, proc.idx)

        view.print_scheduler_log()

        while (not sched_done):
            cpu_ran: bool = False

            # Checker mainly for the final print of scheduler
            if scheduler.is_finished:
                sched_done = True

            # Print timestamp
            view.print_timestamp()

            # Get the arriving processes
            scheduler.get_arriving_processes()

            # Print processes that have arrived
            view.print_arriving_processes()

            # Add arrived processes to queue
            scheduler.add_arriving_to_queue()

            # Print the processes that have finished
            view.print_done_processes(self.done_processes)

            # Increment time
            scheduler.add_time

            # Add to the queue the processes that used up the quantum (returning from cpu)
            prev_process = None
            for proc in self.finished_quantum:
                scheduler.add_to_queue(proc.queue_number, proc)
                prev_process = self.finished_quantum.pop(0)

            # Add to queue those that finished the io
            for proc in self.finished_io:
                scheduler.add_to_queue(proc.queue_number, proc)

            self.finished_quantum = []
            self.finished_io = []

            # Get the process at topmost queue
            self.get_topmost_process()

            # Check if there's NO need to context switch
            # -- idle
            # -- previous process is same as next process
            # -- demoted process is same as next process
            if scheduler.is_idle or \
               (prev_process == scheduler.cpu) or \
               (demoted_process == scheduler.cpu.name):
                scheduler.switch_time_pass = context_switch

            # Print queues
            view.print_all_queues()

            # Check for context switch
            old_cs = scheduler.switch_time_pass

            if scheduler.switch_time_pass == context_switch and scheduler.cpu.name != "":
                # Run the CPU for one quantum
                self.run_one_cpu_quantum()
                cpu_ran = True
                process_ran_name = scheduler.cpu.name

                # Check if quantum was used up; add to top queue
                self.check_process_quantum()
            elif scheduler.switch_time_pass != context_switch:
                scheduler.switch_time_pass += 1
                scheduler.is_idle = False

            # Check if the CPU ran
            if cpu_ran:
                view.print_cpu(process_ran_name)
                scheduler.is_idle = False
            # Context switch occured (so no process was updated) or scheduler is done running
            elif old_cs != scheduler.switch_time_pass or demoted or sched_done:
                if demoted and old_cs == scheduler.switch_time_pass:
                    scheduler.is_idle = True
                view.print_cpu()
            # For idle case
            else:
                view.print_cpu()
                scheduler.is_idle = True

            # Print the processes in io
            if scheduler.io_list:
                view.print_io()

            # Run the io
            self.run_one_io_quantum()

            # Check if any process has finished their io; Adjust queue (sort alphabetically)
            self.finished_io = self.check_proc_in_io()

            # Print process that moved down a queue
            view.print_demotion(demoted_process)
            demoted_process = ""

            # Adjust queue
            current_proc = scheduler.cpu
            # Check if process is done with current CPU burst
            if current_proc.burst_remaining == 0 and current_proc.name != "":
                # Process has finished all bursts
                if current_proc.idx >= len(current_proc.io_burst):
                    current_proc.completion_time = scheduler.time
                    self.done_processes.append(current_proc)
                    scheduler.finished_processes.append(current_proc)
                # Process still not done; move to IO
                else:
                    demoted = False
                    if current_proc.queue_number != 3 and current_proc.quantum_passed == allotments[current_proc.queue_number -1]:
                        demoted_process = current_proc.name
                        demoted = True
                    scheduler.move_to_io(demoted)

                scheduler.empty_cpu()

            # Check if process ran out of allotment (No I/O)
            elif current_proc.queue_number != 3:
                if current_proc.quantum_passed == allotments[current_proc.queue_number -1]:
                    demoted_process = current_proc.name

                    # Case 1: Process is not in the last queue
                    if current_proc.queue_number != 3:
                        scheduler.move_process_down_queue()

                    # Case 2: Process is in the last queue
                    else:
                        scheduler.priority_queues[2].add_process(scheduler.cpu)

                    scheduler.empty_cpu()

            view.print_newline()

        view.print_simulation_done()
        view.print_scheduler_metrics()

if __name__ == "__main__":
    queues: list[SchedulerAlgorithm] = [RoundRobinAlgorithm(Q1_QUANTUM), FCFSAlgorithm(), SJFAlgorithm()]

    scheduler: MLFQScheduler = MLFQScheduler(cpu=Process("", -1, [-1], [-1]),priority_queues=queues)
    view: View = View(scheduler)
    controller: Controller = Controller(view, scheduler)

    controller.run()
