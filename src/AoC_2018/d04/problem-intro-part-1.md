## Problem Intro

We've sneaked into a supply closet near the prototype suit manufacturing lab. We find a record of guard shifts and their sleeping habits. We need to analyze these records to find the best time to sneak into the lab.

The input consists of timestamped log entries, which look like this:

```text
[1518-11-01 00:00] Guard #10 begins shift
[1518-11-01 00:05] falls asleep
[1518-11-01 00:25] wakes up
[1518-11-01 00:30] falls asleep
[1518-11-01 00:55] wakes up
[1518-11-01 23:58] Guard #99 begins shift
[1518-11-02 00:40] falls asleep
[1518-11-02 00:50] wakes up
```

The records are not necessarily in chronological order, so we'll need to sort them first.
We need to track when each guard is on duty, when they fall asleep, and when they wake up.
