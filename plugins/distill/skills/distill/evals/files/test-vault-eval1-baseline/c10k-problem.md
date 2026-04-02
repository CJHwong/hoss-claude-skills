# The C10K Problem

**Source:** http://www.kegel.com/c10k.html
**Tags:** system/network
**Saved:** 2024-03-31

## The Problem

How can a web server handle 10,000 simultaneous client connections? Hardware has sufficient CPU, memory, and bandwidth. The bottleneck is OS and software architecture design.

## Five I/O Strategies

### 1. Level-Triggered Readiness Notification (select/poll)

The kernel tells you whether a file descriptor is ready, regardless of whether you acted on previous notifications.

- `select()` - limited by hardcoded `FD_SETSIZE`
- `poll()` - no hardcoded limit but degrades past a few thousand FDs since most are idle at any time
- `/dev/poll` (Solaris) - maintains state across calls for better efficiency

**Problem:** Disk I/O blocks the entire process. Setting nonblocking mode on disk file handles has no effect.

### 2. Edge-Triggered Readiness Notification (epoll/kqueue)

Signals only when a file descriptor transitions from not-ready to ready. The kernel assumes you know it's ready and won't re-notify until the state changes again.

- **epoll** (Linux 2.6+) - recommended for Linux
- **kqueue** (FreeBSD/NetBSD) - supports both edge and level triggering
- **Realtime signals** (Linux 2.4) - uses `F_SETSIG` and `sigwaitinfo()`

More efficient but less forgiving - miss one event and that connection gets stuck forever.

### 3. Asynchronous I/O (Completion Notification)

Uses `aio_write()` with signal or completion port notification. Works for both network and disk I/O, avoiding disk blocking. But Linux kernel AIO didn't support sockets as of 2.6. Windows has better support via IOCP.

### 4. One Thread Per Client

Classic threading with blocking I/O. The math kills it: 2MB stack per thread means you hit virtual memory limits at 512 threads on 32-bit systems with 1GB user-accessible VM.

Industry consensus shifted to 1:1 threading models (NPTL) over M:N models - M:N has higher theoretical performance but is too complex to get right.

### 5. In-Kernel Server

Embedding server logic in the kernel (khttpd, TUX). Consensus: don't move servers into the kernel; instead add minimal kernel hooks to improve server performance.

## Recommendations by Platform

| Platform | Recommended Approach |
|----------|---------------------|
| Linux 2.6+ | epoll (edge-triggered) |
| FreeBSD/NetBSD | kqueue |
| Solaris | /dev/poll |

## Key Insight

The workaround for disk I/O blocking in event-driven servers: use memory-mapped files, check with `mincore()` if I/O is needed, delegate to a worker thread, and continue handling network traffic.
