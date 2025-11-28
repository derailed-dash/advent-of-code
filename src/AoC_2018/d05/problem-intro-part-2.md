## Part 2

Time to optimize the polymer! The prototype suit's material is still a bit too large.

We need to figure out which unit type is preventing the polymer from collapsing as much as possible. The goal is to remove **all** units of exactly one type (both lowercase and uppercase) from the original polymer, and then fully react the remaining polymer.

For example, using the same polymer `dabAcCaCBAcCcaDA`:

- Removing all `a`/`A` units produces `dbcCCBcCcD`. Fully reacting this yields `dbCBcD`, which has length 6.
- Removing all `b`/`B` units produces `daAcCaCAcCcaDA`. Fully reacting this yields `daCAcaDA`, which has length 8.
- Removing all `c`/`C` units produces `dabAaBAaDA`. Fully reacting this yields `daDA`, which has length 4.
- Removing all `d`/`D` units produces `abAcCaCBAcCcaA`. Fully reacting this yields `abCBAc`, which has length 6.

In this example, removing all `c`/`C` units produces the best result, a length of **4**.

**What is the length of the shortest polymer you can produce by removing all units of exactly one type and fully reacting the result?**
