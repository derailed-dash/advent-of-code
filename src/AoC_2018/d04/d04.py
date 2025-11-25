"""
Author: Darren
Date: 25/11/2025

Solving https://adventofcode.com/2018/day/4

Part 1:

Part 2:

"""
import logging
import re
import sys
import textwrap
from collections import defaultdict

import dazbo_commons as dc  # For locations
from rich.logging import RichHandler

import aoc_common.aoc_commons as ac  # General AoC utils

YEAR = 2018
DAY = 4

locations = dc.get_locations(__file__)

# Configure Rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(message)s",
    datefmt='%H:%M:%S',
    handlers=[RichHandler(
        rich_tracebacks=True, 
        show_path=False,
        markup=True,
        show_time=False  # Disable Rich's time since we're using our own
    )]
)
logger = logging.getLogger(locations.script_name)
logger.setLevel(logging.DEBUG)

matcher = re.compile(r"Guard #(\d+)")

class Guard:
    def __init__(self, guard_id):
        self.guard_id = guard_id
        self.sleep_times = [0]*60

    def add_sleep_time(self, start, end):
        """ Add sleep time to the guard's sleep times """
        for i in range(start, end):
            self.sleep_times[i] += 1

    def get_total_sleep(self) -> int:
        """ Return total sleep time in minutes """
        return sum(self.sleep_times)

    def get_sleep_freq_for_minute(self, minute) -> int:
        """ Return the frequency of sleep for a given minute """
        return self.sleep_times[minute]
    
    def get_most_frequent_minute(self) -> int:
        """ Return the minute that the guard was most frequently asleep """
        return self.sleep_times.index(max(self.sleep_times))

    def __str__(self):
        return f"Guard {self.guard_id}: {self.get_total_sleep()} minutes, " \
               f"asleep {self.get_sleep_freq_for_minute(self.get_most_frequent_minute())} times at minute " \
               f"{self.get_most_frequent_minute()}"

def process_data(data):
    """ Data is a list of strings in the format:
    [1518-11-01 00:00] Guard #10 begins shift
    [1518-11-01 00:05] falls asleep
    [1518-11-01 00:25] wakes up

    The data is unsorted and must be sorted by date and time.
    """
    sorted_data = sorted(data)
    guards = {}

    for line in sorted_data:
        if "Guard" in line:
            asleep_start = None
            guard_id = int(matcher.search(line).group(1))
            if guard_id not in guards:
                guards[guard_id] = Guard(guard_id)
        else:
            if "asleep" in line:
                asleep_start = int(line[15:17])
            else:
                assert asleep_start is not None
                asleep_end = int(line[15:17])
                guards[guard_id].add_sleep_time(asleep_start, asleep_end)
    
    return guards
    
def part1(data):
    """ Return the product of the ID of the guard who has the most total sleep, 
    and the minute they are most frequently asleep """
    guards = process_data(data)
    for guard in guards.values():
        logger.debug(guard)
    
    sleepiest_guard = max(guards.values(), key=lambda x: x.get_total_sleep())
    logger.debug(f"Sleepiest guard: {sleepiest_guard}")
    return sleepiest_guard.guard_id * sleepiest_guard.get_most_frequent_minute()

def part2(data):
    """ Return the product of the ID of the guard who is most frequently asleep at the same minute, 
    and the minute they are most frequently asleep """
    guards = process_data(data)
    sleepiest_minute = max(guards.values(), 
                           key=lambda x: x.get_sleep_freq_for_minute(x.get_most_frequent_minute()))
    logger.debug(f"Sleepiest minute: {sleepiest_minute}")
    return sleepiest_minute.guard_id * sleepiest_minute.get_most_frequent_minute()

def main():
    try:
        ac.write_puzzle_input_file(YEAR, DAY, locations)
        with open(locations.input_file, encoding="utf-8") as f:
            input_data = f.read().splitlines()
            logger.debug(dc.top_and_tail(input_data))
    except (ValueError, FileNotFoundError) as e:
        logger.error("Could not read input file: %s", e)
        return 1

    sample_inputs = []
    sample_inputs.append(textwrap.dedent("""\
        [1518-11-01 00:05] falls asleep
        [1518-11-01 00:30] falls asleep
        [1518-11-01 00:25] wakes up
        [1518-11-03 00:05] Guard #10 begins shift
        [1518-11-01 00:00] Guard #10 begins shift
        [1518-11-01 23:58] Guard #99 begins shift
        [1518-11-01 00:55] wakes up
        [1518-11-04 00:02] Guard #99 begins shift
        [1518-11-03 00:29] wakes up
        [1518-11-02 00:50] wakes up
        [1518-11-03 00:24] falls asleep
        [1518-11-05 00:45] falls asleep
        [1518-11-02 00:40] falls asleep
        [1518-11-04 00:46] wakes up
        [1518-11-05 00:03] Guard #99 begins shift
        [1518-11-04 00:36] falls asleep
        [1518-11-05 00:55] wakes up"""))
    sample_answers = [240]
    test_solution(part1, sample_inputs, sample_answers)

    with ac.timer():
        logger.info(f"Part 1 soln={part1(input_data)}")
        
    sample_answers = [4455]
    test_solution(part2, sample_inputs, sample_answers)
     
    with ac.timer():
        logger.info(f"Part 2 soln={part2(input_data)}")

def test_solution(soln_func, sample_inputs: list, sample_answers: list):
    """
    Tests a solution function against multiple sample inputs and expected answers.

    Args:
        soln_func: The function to be tested (e.g., part1 or part2).
        sample_inputs: A list of sample input strings.
        sample_answers: A list of expected answers corresponding to the sample inputs.

    Raises:
        AssertionError: If any of the test cases fail validation.
    """
    for curr_input, curr_ans in zip(sample_inputs, sample_answers):
        try:
            ac.validate(soln_func(curr_input.splitlines()), curr_ans)
        except AssertionError as e:
            logger.error(f"{soln_func.__name__} test failed: {e}")
            sys.exit(1)
    logger.info(f"{soln_func.__name__} tests passed")
    
if __name__ == "__main__":
    main()
