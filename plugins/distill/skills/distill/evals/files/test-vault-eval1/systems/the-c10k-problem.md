---
url: "http://www.kegel.com/c10k.html"
title: "The C10K problem"
source: "pocket-export"
date_processed: 2026-04-02
confidence: high
insight_summary: "Foundational reference on handling 10K concurrent connections, cataloging I/O strategies (select, poll, epoll, kqueue, async I/O) with tradeoffs that still shape server architecture today."
concepts:
  - "systems-programming"
  - "concurrency"
---

# The C10K problem

> [Original](http://www.kegel.com/c10k.html)

## Key Insight

Foundational reference on handling 10K concurrent connections, cataloging I/O strategies (select, poll, epoll, kqueue, async I/O) with tradeoffs that still shape server architecture today.

## Takeaways

- The bottleneck for handling 10K+ concurrent connections is not hardware but the I/O model chosen by the server: select() doesn't scale, poll() is better, epoll/kqueue are the real solution.
- Threads-per-connection models hit memory walls around 1K connections due to stack allocation overhead.
- The event-driven approach (single thread, non-blocking I/O, readiness notifications) became the foundation for nginx, Node.js, and every modern high-performance server.
- This problem, articulated in 1999, correctly predicted that server-side concurrency would be the defining systems challenge of the internet era.

## Context

Written when 10,000 simultaneous connections seemed ambitious, this page became the canonical reference for server architecture decisions. The I/O strategy taxonomy it established (select vs. poll vs. epoll vs. async I/O) remains the framework engineers use today when building high-concurrency systems.

---

The C10K problem
The C10K problem
[
Help save the best Linux news source on the web -- subscribe to Linux Weekly News!
]
It's time for web servers to handle ten thousand clients simultaneously,
don't you think?  After all, the web is a big place now.
And computers are big, too.  You can buy a 1000MHz machine
with 2 gigabytes of RAM and an 1000Mbit/sec Ethernet card for $1200 or so.  
Let's see - at 20000 clients, that's
50KHz, 100Kbytes, and 50Kbits/sec per client.  

It shouldn't take any more horsepower than that to take four kilobytes 
from the disk and send them to the network once a second for each
of twenty thousand clients.
(That works out to $0.08 per client, by the way.  Those
$100/client licensing fees some operating systems charge are starting to 
look a little heavy!)  So hardware is no longer the bottleneck.
In 1999 one of the busiest ftp sites, cdrom.com, 
actually handled 10000 clients simultaneously
through a Gigabit Ethernet pipe.
As of 2001, that same speed is now
being offered by several ISPs
,
who expect it to become increasingly popular with large business customers.
And the thin client model of computing appears to be coming back in
style -- this time with the server out on the Internet, serving
thousands of clients.
With that in mind, here are a few notes on how to configure operating 
systems and write code to support thousands of clients.  The discussion
centers around Unix-like operating systems, as that's my personal area
of interest, but Windows is also covered a bit.
Contents
The C10K problem
Related Sites
Book to Read First
I/O frameworks
I/O Strategies
Serve many clients with each thread, and use nonblocking I/O and
level-triggered
readiness notification
The traditional select()
The traditional poll()
/dev/poll
(Solaris 2.7+)
kqueue
(FreeBSD, NetBSD)
Serve many clients with each thread, and use nonblocking I/O and readiness
change
notification
epoll
(Linux 2.6+)
Polyakov's kevent
(Linux 2.6+)
Drepper's New Network Interface
(proposal for Linux 2.6+)
Realtime Signals
(Linux 2.4+)
Signal-per-fd
kqueue
(FreeBSD, NetBSD)
Serve many clients with each thread, and use asynchronous I/O and completion notification
Serve one client with each server thread
LinuxThreads
(Linux 2.0+)
NGPT
(Linux 2.4+)
NPTL
(Linux 2.6, Red Hat 9)
FreeBSD threading support
NetBSD threading support
Solaris threading support
Java threading support in JDK 1.3.x and earlier
Note: 1:1 threading vs. M:N threading
Build the server code into the kernel
Bring the TCP stack into userspace
Comments
Limits on open filehandles
Limits on threads
Java issues
[Updated 27 May 2001]
Other tips
Zero-Copy
The sendfile() system call can implement zero-copy networking.
Avoid small frames by using writev (or TCP_CORK)
Some programs can benefit from using non-Posix threads.
Caching your own data can sometimes be a win.
Other limits
Kernel Issues
Measuring Server Performance
Examples
Interesting select()-based servers
Interesting /dev/poll-based servers
Interesting epoll-based servers
Interesting kqueue()-based servers
Interesting realtime signal-based servers
Interesting thread-based servers
Interesting in-kernel servers
Other interesting links
Related Sites
See Nick Black's execellent
Fast UNIX Servers
page
for a circa-2009 look at the situation.
In October 2003, Felix von Leitner put together an excellent
web page
and
presentation
about network scalability,
complete with benchmarks comparing various networking system calls and operating systems.
One of his observations is that the 2.6 Linux kernel really does beat the 2.4 kernel,
but there are many, many good graphs that will give the OS developers food for thought for some time.
(See also the
Slashdot
comments; it'll be interesting to see whether anyone does followup benchmarks improving on Felix's results.)
Book to Read First
If you haven't read it already, go out and get a copy of
Unix Network Programming : Networking Apis: Sockets and Xti (Volume 1)
by the late W. Richard Stevens.  It describes many of the I/O
strategies and pitfalls related to writing high-performance servers.
It even talks about the
'thundering herd'
problem.
And while you're at it, go read
Jeff Darcy's notes on high-performance server design
.
(Another book which might be more helpful for those
who are *using* rather than *writing* a web server is
Building Scalable Web Sites
by Cal Henderson.)
I/O frameworks
Prepackaged libraries are available that abstract some of the techniques presented below, 
insulating your code from the operating system and making it more portable.
ACE
, a heavyweight C++ I/O framework,
contains object-oriented implementations of some of these I/O strategies
and many other useful things.
In particular, his Reactor is an OO way of doing nonblocking I/O, and
Proactor is an OO way of doing asynchronous I/O.
ASIO
is an C++ I/O framework
which is becoming part of the Boost library.  It's like ACE updated for 
the STL era.
libevent
is a lightweight C
I/O framework by Niels Provos.  It supports kqueue and select,
and soon will support poll and epoll.  It's level-triggered only, I think,
which has both good and bad sides.  Niels has
a nice graph of time to handle one event
as a function of the number of connections.  It shows kqueue and sys_epoll
as clear winners.
My own attempts at lightweight frameworks (sadly, not kept up to date):
Poller
is a lightweight C++ 
I/O framework that implements a level-triggered readiness API using whatever underlying 
readiness API you want (poll, select, /dev/poll, kqueue, or sigio).
It's useful for
benchmarks that compare
the performance of the various APIs.
This document links to 
Poller subclasses below to illustrate how each of the readiness APIs
can be used.
rn
is a lightweight C I/O framework that was my second try
after Poller.  It's lgpl (so it's easier to use in commercial apps) and
C (so it's easier to use in non-C++ apps).  It was used in some commercial
products.
Matt Welsh wrote
a paper
in April 2000 about how to balance the use of worker thread and
event-driven techniques when building scalable servers.  
The paper describes part of his Sandstorm I/O framework.
Cory Nelson's Scale! library
- an async socket, file, and pipe I/O library for Windows
I/O Strategies
Designers of networking software have many options.  Here are a few:
Whether and how to issue multiple I/O calls from a single thread
Don't; use blocking/synchronous calls throughout, and possibly use multiple threads or processes to achieve concurrency
Use nonblocking calls (e.g. write() on a socket set to O_NONBLOCK) to start I/O,
	and readiness notification (e.g. poll() or /dev/poll) to know when it's OK to start the next I/O on that channel.
	Generally only usable with network I/O, not disk I/O.
Use asynchronous calls (e.g. aio_write()) to start I/O, and completion notification (e.g. signals or completion ports)
	to know when the I/O finishes.  Good for both network and disk I/O.
How to control the code servicing each client
one process for each client (classic Unix approach, used since 1980 or so)
one OS-level thread handles many clients; each client is controlled by:
a user-level thread (e.g. GNU state threads, classic Java with green threads)
a state machine (a bit esoteric, but popular in some circles; my favorite)
a continuation (a bit esoteric, but popular in some circles)
one OS-level thread for each client (e.g. classic Java with native threads)
one OS-level thread for each active client (e.g. Tomcat with apache front end; NT completion ports; thread pools)
Whether to use standard O/S services, or put some code into the 
kernel (e.g. in a custom driver, kernel module, or VxD)
The following five combinations seem to be popular:
Serve many clients with each thread, and use nonblocking I/O and
level-triggered
readiness notification
Serve many clients with each thread, and use nonblocking I/O and readiness
change
notification
Serve many clients with each server thread, and use asynchronous I/O
serve one client with each server thread, and use blocking I/O
Build the server code into the kernel
1. Serve many clients with each thread, and use nonblocking I/O and
level-triggered
readiness notification
... set nonblocking mode on all network handles, and use
select() or poll() to tell which network handle has data waiting.
This is the traditional favorite.
With this scheme, the kernel tells you whether a file descriptor is ready,
whether or not you've done anything with that file descriptor since the last time
the kernel told you about it.  (The name 'level triggered' comes from computer hardware
design; it's the opposite of
'edge triggered'
.
Jonathon Lemon introduced the terms in his
BSDCON 2000 paper on kqueue()
.)
Note: it's particularly important to remember that readiness notification from the
kernel is only a hint; the file descriptor might not be ready anymore when you try
to read from it.  That's why it's important to use nonblocking mode when using
readiness notification.
An important bottleneck in this method is that read() or sendfile() 
from disk blocks if the page is not in core at the moment;
setting nonblocking mode on a disk file handle has no effect.
Same thing goes for memory-mapped disk files.
The first time a server needs disk I/O, its process blocks,
all clients must wait, and that raw nonthreaded performance goes to waste.
This is what asynchronous I/O is for, but on systems that lack AIO,
worker threads or processes that do the disk I/O can also get around this
bottleneck.  One approach is to use memory-mapped files,
and if mincore() indicates I/O is needed, ask a worker to do the I/O,
and continue handling network traffic.  Jef Poskanzer mentions that
Pai, Druschel, and Zwaenepoel's 1999
Flash
web server uses this trick; they gave a talk at
Usenix '99
on it.
It looks like mincore() is available in BSD-derived Unixes 
like
FreeBSD
and Solaris, but is not part
of the
Single Unix Specification
.
It's available as part of Linux as of kernel 2.3.51,
thanks to Chuck Lever
.
But
in November 2003 on the freebsd-hackers list, Vivek Pei et al reported
very good results using system-wide profiling of their Flash web server
to attack bottlenecks.  One bottleneck they found was
mincore (guess that wasn't such a good idea after all)
Another was the fact that sendfile blocks on disk access;
they improved performance by introducing a modified sendfile() 
that return something like EWOULDBLOCK
when the disk page it's fetching is not yet in core.
(Not sure how you tell the user the page is now resident...
seems to me what's really needed here is aio_sendfile().)
The end result of their optimizations is a SpecWeb99 score of about 800
on a 1GHZ/1GB FreeBSD box, which is better than anything on
file at spec.org.
There are several ways for a single thread to tell which of a set of nonblocking sockets are ready for I/O:
The traditional select()
Unfortunately, select() is limited to FD_SETSIZE handles.  
This limit is compiled in to the standard library and user programs.
(Some versions of the C library let you raise this limit at user app compile time.)
See
Poller_select
(
cc
,
h
)
for an example of how to use select() interchangeably with other readiness notification schemes.
The traditional poll()
There is no hardcoded limit to the number of file descriptors poll() can handle,
but it does get slow about a few thousand, since most of the file descriptors
are idle at any one time, and scanning through thousands of file descriptors
takes time.
Some OS's (e.g. Solaris 8) speed up poll() et al by use of techniques like poll hinting,
which was
implemented and benchmarked by Niels Provos
for Linux in 1999.
See
Poller_poll
(
cc
,
h
,
benchmarks
)
for an example of how to use poll() interchangeably with other readiness notification schemes.
/dev/poll
This is the recommended poll replacement for Solaris.
The idea behind /dev/poll is to take advantage of the fact that often
poll() is called many times with the same arguments.
With /dev/poll, you get an open handle to /dev/poll, and
tell the OS just once what files you're interested in by writing to that handle;
from then on, you just read the set of currently ready file descriptors from that handle.
It appeared quietly in Solaris 7
(
see patchid 106541
)
but its first public appearance was in
Solaris 8
;
according to Sun
,
at 750 clients, this has 10% of the overhead of poll().
Various implementations of /dev/poll were tried on Linux, but 
none of them perform as well as epoll, and were never really completed.
/dev/poll use on Linux is not recommended.
See
Poller_devpoll
(
cc
,
h
benchmarks
)
for an example of how to use /dev/poll interchangeably with many other readiness notification 
schemes.  (Caution - the example is for Linux /dev/poll, might not work right on Solaris.)
kqueue()
This is the recommended poll replacement for FreeBSD (and, soon, NetBSD).
See below.
kqueue() can specify either edge triggering or level triggering.
2. Serve many clients with each thread, and use nonblocking I/O and readiness
change
notification
Readiness change notification (or edge-triggered readiness notification)
means you give the kernel a file descriptor, and later, when that descriptor transitions from
not ready
to
ready
, the kernel notifies you somehow.  It then assumes you
know the file descriptor is ready, and will not send any more readiness
notifications of that type for that file descriptor until you do something
that causes the file descriptor to no longer be ready (e.g. until you receive the
EWOULDBLOCK error on a send, recv, or accept call, or a send or recv transfers
less than the requested number of bytes).
When you use readiness change notification, you must be prepared for spurious
events, since one common implementation is to signal readiness whenever any
packets are received, regardless of whether the file descriptor was already ready.
This is the opposite of "
level-triggered
" readiness notification.
It's a bit less forgiving of programming mistakes, since
if you miss just one event, the connection that event was for gets stuck forever.
Nevertheless, I have found that edge-triggered readiness notification
made programming nonblocking clients with OpenSSL easier, so it's worth trying.
[Banga, Mogul, Drusha '99]
described this kind of scheme in 1999.
There are several APIs which let the application retrieve 'file descriptor became ready' notifications:
kqueue()
This is the recommended edge-triggered poll replacement for FreeBSD (and, soon, NetBSD).
FreeBSD 4.3 and later, and
NetBSD-current as of Oct 2002
, 
support a generalized alternative to poll() called
kqueue()/kevent()
; 
it supports both edge-triggering and level-triggering.
(See also
Jonathan Lemon's page
and his
BSDCon 2000 paper on kqueue()
.)
Like /dev/poll, you allocate a listening object, but rather than opening the file /dev/poll, you
call kqueue() to allocate one.  To change the events you are listening for, or to get the
list of current events, you call kevent() on the descr