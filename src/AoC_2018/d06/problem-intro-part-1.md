# Advent of Code 2018 - Day 6: Chronal Coordinates (Part 1)

## Problem Introduction

Your wrist device beeps urgently: "Situation critical. Destination indeterminate. Chronal interference detected." It produces a list of coordinates and suggests you check manual page 729. Unfortunately, the Elves didn't give you a manual!

The device has given you a list of coordinates in the format `x, y`. Your task is to work out which coordinate has the largest **finite area** around it. But what does that mean?

## Understanding the Problem

Using **Manhattan distance** (also called taxicab distance), you need to determine which locations on an infinite 2D grid are closest to each coordinate. The Manhattan distance between two points is calculated as:

```
distance = |x1 - x2| + |y1 - y2|
```

For each integer location `(x, y)` on the grid, you determine which coordinate it's closest to. If a location is equally close to two or more coordinates, it doesn't count as belonging to any of them.

The "area" of a coordinate is the count of all grid locations that are closest to it.

### Example Input Data

```text
1, 1
1, 6
8, 3
3, 4
5, 5
8, 9
```

If we label these coordinates A through F and visualise the grid (with `0,0` at the top left), we can see which locations are closest to each coordinate. Locations marked with lowercase letters belong to that coordinate:

```text
aaaaa.cccc
aAaaa.cccc
aaaddecccc
aadddeccCc
..dDdeeccc
bb.deEeecc
bBb.eeee..
bbb.eeefff
bbb.eeffff
bbb.ffffFf
```

Locations shown as `.` are equally far from two or more coordinates.

### Infinite vs Finite Areas

Some coordinates have **infinite areas** because their closest locations extend forever beyond the visible grid. In the example above, coordinates A, B, C, and F all have infinite areas because they're on or near the edges.

However, coordinates D and E have **finite areas**:
- Coordinate D is closest to 9 locations
- Coordinate E is closest to 17 locations (including the coordinate itself)

## Part 1 Goal

**What is the size of the largest area that isn't infinite?**

You need to:
1. Read the list of coordinates from your input
2. Determine which coordinates have finite areas (those that don't extend to infinity)
3. Calculate the area (count of closest locations) for each finite coordinate
4. Return the size of the largest finite area

In the example above, the answer would be **17** (coordinate E's area).
