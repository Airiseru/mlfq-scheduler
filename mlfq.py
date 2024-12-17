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

"""Function to keep looping input until valid"""
def input_int_loop(min_inp: int, max_inp: float) -> int:
    user_input = -5
    while (user_input < min_inp) or (user_input > max_inp):
        try:
            user_input = int(input(""))
        except ValueError:
            continue

    return user_input

if __name__ == "__main__":
    print("# Enter Scheduler Details #")
    num_procs: int = input_int_loop(0, 12)
    q1_allot: int = input_int_loop(4, float('inf'))
    q2_allot: int = input_int_loop(0, float('inf'))
    context_switch: int = input_int_loop(-1, 6)