---
category: Algorithms & Data Structures
name: Dynamic Programming
contributors:
    - ["Akashdeep Goel", "http://github.com/akashdeepgoel"]
    - ["Miltiadis Stouras", "https://github.com/mstou"]
---

Dynamic Programming is a technique for solving problems by breaking them into
overlapping subproblems and caching results to avoid redundant computation.

"Those who can't remember the past are condemned to repeat it."

## Core Idea

If a problem has **optimal substructure** (optimal solution built from optimal
sub-solutions) and **overlapping subproblems** (same sub-problems solved
repeatedly), DP applies.

### Two Approaches

**Top-Down (Memoization)** — Recurse naturally; cache results as you go.
Easy to reason about. Uses the call stack.

**Bottom-Up (Tabulation)** — Solve trivial sub-problems first, build up to
the target. No recursion. Usually faster in practice.

## Example: Fibonacci

### Naive (exponential time — recomputes everything)

```python
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
```

### Top-Down Memoization (O(n) time, O(n) space)

```python
memo = {}

def fib(n):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fib(n - 1) + fib(n - 2)
    return memo[n]
```

### Bottom-Up Tabulation (O(n) time, O(1) space)

```python
def fib(n):
    if n <= 1:
        return n
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr
```

## Example: Longest Increasing Subsequence (LIS)

Given sequence S, find the longest strictly increasing subsequence.

```python
def lis(seq):
    n = len(seq)
    dp = [1] * n          # dp[i] = LIS length ending at index i

    for i in range(1, n):
        for j in range(i):
            if seq[j] < seq[i]:
                dp[i] = max(dp[i], dp[j] + 1)

    return max(dp)

# Example
lis([3, 1, 8, 2, 5])  # => 3  (subsequence: 1, 2, 5)
```

## Example: 0/1 Knapsack

Given items with weights and values, maximize value within weight capacity W.

```python
def knapsack(weights, values, W):
    n = len(weights)
    # dp[i][w] = max value using first i items with capacity w
    dp = [[0] * (W + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(W + 1):
            # Don't take item i
            dp[i][w] = dp[i-1][w]
            # Take item i (if it fits)
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i][w],
                               dp[i-1][w - weights[i-1]] + values[i-1])

    return dp[n][W]

# Example
weights = [2, 3, 4, 5]
values  = [3, 4, 5, 6]
knapsack(weights, values, W=5)  # => 7  (items with weight 2 and 3)
```

## When to Recognize a DP Problem

1. "Find the minimum/maximum ..." → likely optimization DP
2. "Count the number of ways ..." → likely counting DP
3. "Is it possible to ..." → likely boolean DP
4. The problem has a natural recursive breakdown with repeated subproblems

## Complexity

| Approach | Time | Space |
|----------|------|-------|
| Naive recursion | Exponential | O(n) stack |
| Memoization | O(subproblems) | O(subproblems) |
| Tabulation | O(subproblems) | O(table size) — often reducible |

## Further Reading

* MIT 6.006 Lectures 19–22: Dynamic Programming
* [TopCoder: DP from Novice to Advanced](https://www.topcoder.com/community/competitive-programming/tutorials/dynamic-programming-from-novice-to-advanced/)
* [GeeksForGeeks: DP](https://www.geeksforgeeks.org/dynamic-programming/)

<!-- Source: https://github.com/adambard/learnxinyminutes-docs/blob/master/dynamic-programming.md (adapted for reference) -->
