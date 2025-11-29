# Advent of Code 2018 - Day 6: Chronal Coordinates (Part 2)

## Problem Introduction

On the other hand, **if the coordinates are safe**, maybe the best you can do is try to find a **region** near as many coordinates as possible.

## Part 2 Goal

Find the size of the region containing all locations which have a **total distance to all given coordinates of less than 10000**.

## Understanding the Problem

For each location on the grid, you need to:
1. Calculate the Manhattan distance to **ALL** given coordinates
2. Sum up all those distances
3. If the total sum is **less than 10000**, that location is within the desired region
4. Count how many locations meet this criteria

## Example

Using the same sample coordinates from Part 1, but with a threshold of **32** (instead of 10000):

```text
1, 1
1, 6
8, 3
3, 4
5, 5
8, 9
```

The resulting region looks like this (marked with `#`):

```text
..........
.A........
..........
...###..C.
..#D###...
..###E#...
.B.###....
..........
..........
........F.
```

### Example Calculation for Location (4,3)

For the highlighted location `4,3` at the top middle of the region:

- Distance to coordinate A (1,1): `abs(4-1) + abs(3-1) =  5`
- Distance to coordinate B (1,6): `abs(4-1) + abs(3-6) =  6`
- Distance to coordinate C (8,3): `abs(4-8) + abs(3-3) =  4`
- Distance to coordinate D (3,4): `abs(4-3) + abs(3-4) =  2`
- Distance to coordinate E (5,5): `abs(4-5) + abs(3-5) =  3`
- Distance to coordinate F (8,9): `abs(4-8) + abs(3-9) = 10`
- **Total distance**: `5 + 6 + 4 + 2 + 3 + 10 = 30`

Because the total distance (30) is **less than 32**, this location is within the region.

This region, which also includes coordinates D and E, has a total size of **16**.

## Your Task

Your actual region will need to be much larger than this example. You need to find all locations with a total distance of **less than 10000**.

**What is the size of the region containing all locations which have a total distance to all given coordinates of less than 10000?**

## Strategy Thoughts

- Use the same bounding box approach from Part 1
- For each point in the bounding box:
  - Calculate Manhattan distance to **every** danger coordinate
  - Sum all the distances
  - If sum < 10000, increment the region counter
- Return the total count of locations in the region
