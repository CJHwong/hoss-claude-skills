# Structured Concurrency: Go Statement Considered Harmful

**Source:** https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/
**Tags:** concurrency
**Saved:** 2024-03-31

## Core Thesis

Traditional concurrency primitives (go statements, thread spawning, callbacks, futures) are the modern equivalent of `goto`. They break control flow abstraction by allowing functions to spawn background tasks with unbounded lifetimes, making it impossible to reason locally about program behavior.

## Key Arguments

### The goto analogy
Just as `goto` allowed uncontrolled jumps across function boundaries, go statements let functions spawn background work that outlives the caller. You cannot know if a function truly completes without reading its entire source tree.

### Three failures of go statements

1. **Broken abstraction** - Functions become unpredictable. Calling `f()` might spawn 10 background tasks you never know about.
2. **Resource cleanup failure** - Context managers and with-blocks break when tasks continue after the block exits. The file closes while background operations still need it.
3. **Error propagation failure** - Most frameworks silently discard unhandled errors in background tasks rather than propagating them.

## The Solution: Nurseries

Nurseries enforce the "black box rule" - control enters through one path and exits through another, with all child tasks guaranteed to complete before the block ends.

```python
async with trio.open_nursery() as nursery:
    nursery.start_soon(myfunc)
    nursery.start_soon(anotherfunc)
# Both tasks guaranteed complete here
```

**Why this matters:**
- Functions become truly composable - returning means completely finished
- Resource cleanup works reliably
- Exceptions propagate upward through the task tree
- Dynamic task spawning still works (pass nursery objects as arguments)
- Demonstrated 15x shorter implementations compared to unstructured equivalents

## Practical Takeaway

Structured concurrency is to threading what structured programming was to goto. The adjustment requires learning new patterns, but the payoff is code that is dramatically more readable and correct by default.
