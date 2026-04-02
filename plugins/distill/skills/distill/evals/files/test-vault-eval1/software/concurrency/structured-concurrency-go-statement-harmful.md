---
url: "https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/"
title: "Notes on structured concurrency, or: Go statement considered harmful"
source: "pocket-export"
date_processed: 2026-04-02
confidence: high
insight_summary: "Argues that unrestricted concurrency spawning (go, spawn, create_task) is the modern equivalent of goto, and proposes structured concurrency as the fix with nursery/task-group patterns."
concepts:
  - "concurrency"
  - "programming-paradigms"
---

# Notes on structured concurrency, or: Go statement considered harmful

> [Original](https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/)

## Key Insight

Argues that unrestricted concurrency spawning (go, spawn, create_task) is the modern equivalent of goto, and proposes structured concurrency as the fix with nursery/task-group patterns.

## Takeaways

- The `go` statement (and equivalents like `spawn`, `create_task`, `pthread_create`) is the concurrency equivalent of `goto`: it creates unstructured control flow that's impossible to reason about locally.
- Structured concurrency constrains concurrent operations to a lexical scope (nursery/task group), guaranteeing that when a block exits, all its child tasks have completed or been cancelled.
- This eliminates entire classes of bugs: orphaned tasks, unhandled exceptions in background work, and resource leaks from fire-and-forget patterns.
- The pattern maps directly to how humans think about concurrent work: "do these three things, wait for all of them, then continue."

## Context

Nathaniel Smith's 2018 essay introduced structured concurrency as a paradigm shift in how we think about concurrent programming. The concept, inspired by Dijkstra's structured programming argument against goto, has since been adopted in Python's trio library, Kotlin's coroutines, and Java's Project Loom (JEP 453). It reframes concurrency bugs as a language design problem, not a programmer discipline problem.

---

Notes on structured concurrency, or: Go statement considered harmful — njs blog
fake link
Every concurrency API needs a way to run code concurrently. Here's
some examples of what that looks like using different APIs:
go myfunc();                                // Golang

pthread_create(&thread_id, NULL, &myfunc);  /* C with POSIX threads */

spawn(modulename, myfuncname, [])           % Erlang

threading.Thread(target=myfunc).start()     # Python with threads

asyncio.create_task(myfunc())               # Python with asyncio
There are lots of variations in the notation and terminology, but the
semantics are the same: these all arrange for
myfunc
to start
running concurrently to the rest of the program, and then return
immediately so that the parent can do other things.
Another option is to use callbacks:
QObject::connect(&emitter, SIGNAL(event()),        // C++ with Qt
                 &receiver, SLOT(myfunc()))

g_signal_connect(emitter, "event", myfunc, NULL)   /* C with GObject */

document.getElementById("myid").onclick = myfunc;  // Javascript

promise.then(myfunc, errorhandler)                 // Javascript with Promises

deferred.addCallback(myfunc)                       # Python with Twisted

future.add_done_callback(myfunc)                   # Python with asyncio
Again, the notation varies, but these all accomplish the same thing:
they arrange that from now on, if and when a certain event occurs,
then
myfunc
will run. Then once they've set that up, they
immediately return so the caller can do other things. (Sometimes
callbacks get dressed up with fancy helpers like
promise
combinators
,
or
Twisted-style protocols/transports
,
but the core idea is the same.)
And... that's it. Take any real-world, general-purpose concurrency
API, and you'll probably find that it falls into one or the other of
those buckets (or sometimes both, like asyncio).
But my new library
Trio
is weird. It
doesn't use either approach. Instead, if we want to run
myfunc
and
anotherfunc
concurrently, we write something like:
async
with
trio
.
open_nursery
()
as
nursery
:
nursery
.
start_soon
(
myfunc
)
nursery
.
start_soon
(
anotherfunc
)
When people first encounter this "nursery" construct, they tend to
find it confusing. Why is there an indented block? What's this
nursery
object, and why do I need one before I can spawn a task?
Then they realize that it prevents them from using patterns they've
gotten used to in other frameworks, and they get really annoyed. It
feels quirky and idiosyncratic and too high-level to be a basic
primitive. These are understandable reactions! But bear with me.
In this post, I want to convince you that nurseries aren't quirky or
idiosyncratic at all, but rather a new control flow primitive that's
just as fundamental as for loops or function calls. And furthermore,
the other approaches we saw above – thread spawning and callback
registration – should be removed entirely and replaced with
nurseries.
Sound unlikely? Something similar has actually happened before: the
goto
statement was once the king of control flow. Now it's a
punchline
. A few languages still have
something they call
goto
, but it's different and far weaker than
the original
goto
. And most languages don't even have that. What
happened? This was so long ago that most people aren't familiar with
the story anymore, but it turns out to be surprisingly relevant. So
we'll start by reminding ourselves what a
goto
was, exactly, and
then see what it can teach us about concurrency APIs.
Contents:
What is a
goto
statement anyway?
What is a
go
statement anyway?
What happened to
goto
?
goto
: the destroyer of abstraction
A surprise benefit: removing
goto
statements enables new features
goto
statements: not even once
go
statement considered harmful
go
statements: not even once
Nurseries: a structured replacement for
go
statements
Nurseries preserve the function abstraction.
Nurseries support dynamic task spawning.
There is an escape.
You can define new types that quack like a nursery.
No, really, nurseries
always
wait for the tasks inside to exit.
Automatic resource cleanup works.
Automated error propagation works.
A surprise benefit: removing
go
statements enables new features
Nurseries in practice
Conclusion
Comments
Acknowledgments
Footnotes
What is a
goto
statement anyway?
Let's review some history: Early computers were programmed using
assembly language
, or other even
more primitive mechanisms. This kinda sucked. So in the 1950s, people
like
John Backus
at
IBM and
Grace Hopper
at Remington Rand started to develop languages like
FORTRAN
and
FLOW-MATIC
(better known for its
direct successor
COBOL
).
FLOW-MATIC was very ambitious for its time. You can think of it as
Python's great-great-great-...-grandparent: the first language that
was designed for humans first, and computers second. Here's some
FLOW-MATIC code to give you a taste of what it looked like:
You'll notice that unlike modern languages, there's no
if
blocks,
loop blocks, or function calls here – in fact there's no block
delimiters or indentation at all. It's just a flat list of statements.
That's not because this program happens to be too short to use fancier
control syntax – it's because block syntax wasn't invented yet!
Sequential flow represented as a vertical arrow pointing
down, and goto flow represented as an arrow that starts
pointing down and then leaps off to the side.
Instead, FLOW-MATIC had two options for flow control. Normally, it was
sequential, just like you'd expect: start at the top and move
downwards, one statement at a time. But if you execute a special
statement like
JUMP TO
, then it could directly transfer control
somewhere else. For example, statement (13) jumps back to statement
(2):
Just like for our concurrency primitives at the beginning, there was
some disagreement about what to call this "do a one-way jump"
operation. Here it's
JUMP TO
, but the name that stuck was
goto
(like "go to", get it?), so that's what I'll use here.
Here's the complete set of
goto
jumps in this little program:
If you think this looks confusing, you're not alone! This style of
jump-based programming is something that FLOW-MATIC inherited pretty
much directly from assembly language. It's powerful, and a good fit to
how computer hardware actually works, but it's super confusing to work
with directly. That tangle of arrows is why the term "spaghetti code"
was invented. Clearly, we needed something better.
But... what is it about
goto
that causes all these problems? Why
are some control structures OK, and some not? How do we pick the good
ones? At the time, this was really unclear, and it's hard to fix a
problem if you don't understand it.
What is a
go
statement anyway?
But let's hit pause on the history for a moment – everyone knows
goto
was bad. What does this have to do with concurrency? Well,
consider Golang's famous
go
statement, used to spawn a new
"goroutine" (lightweight thread):
// Golang
go
myfunc
();
Can we draw a diagram of its control flow? Well, it's a little
different from either of the ones we saw above, because control
actually splits. We might draw it like:
"Go" flow represented as two arrows: a green arrow pointing
down, and a lavender arrow that starts pointing down and then
leaps off to the side.
Here the colors are intended to indicate that
both
paths are taken.
From the perspective of the parent goroutine (green line), control
flows sequentially: it comes in the top, and then immediately comes
out the bottom. Meanwhile, from the perspective of the child (lavender
line), control comes in the top, and then jumps over to the body of
myfunc
. Unlike a regular function call, this jump is one-way: when
running
myfunc
we switch to a whole new stack, and the runtime
immediately forgets where we came from.
But this doesn't just apply to Golang. This is the flow control
diagram for
all
of the primitives we listed at the beginning of this
post:
Threading libraries usually provide some sort of handle object that
lets you
join
the thread later – but this is an independent
operation that the language doesn't know anything about. The actual
thread spawning primitive has the control flow shown above.
Registering a callback is semantically equivalent to starting a
background thread that (a) blocks until some event occurs, and
then (b) runs the callback. (Though obviously the implementation is
different.) So in terms of high-level control flow, registering a
callback is essentially a
go
statement.
Futures and promises are the same too: when you call a function and
it returns a promise, that means it's scheduled the work to happen
in the background, and then given you a handle object to join the
work later (if you want). In terms of control flow semantics, this
is just like spawning a thread. Then you register callbacks on the
promise, so see the previous bullet point.
This same exact pattern shows up in many, many forms: the key
similarity is that in all these cases, control flow splits, with one
side doing a one-way jump and the other side returning to the caller.
Once you know what to look for, you'll start seeing it all over the
place – it's a fun game!
[1]
Annoyingly, though, there is no standard name for this category of
control flow constructs. So just like "
goto
statement" became the
umbrella term for all the different
goto
-like constructs, I'm
going to use "
go
statement" as a umbrella term for these. Why
go
? One reason is that Golang gives us a particularly pure example
of the form. And the other is... well, you've probably guessed where
I'm going with all this. Look at these two diagrams. Notice any
similarities?
Repeat of earlier diagrams: goto flow represented as an arrow
that starts pointing down and then leaps off to the side, and
"go" flow represented as two arrows: a green arrow pointing
down, and a lavender arrow that starts pointing down and then
leaps off to the side.
That's right:
go statements are a form of goto statement.
Concurrent programs are notoriously difficult to write and reason
about. So are
goto
-based programs. Is it possible that this might
be for some of the same reasons? In modern languages, the problems
caused by
goto
are largely solved. If we study how they fixed
goto
, will it teach us how to make more usable concurrency APIs?
Let's find out.
What happened to
goto
?
So what is it about
goto
that makes it cause so many problems? In
the late 1960s,
Edsger W. Dijkstra
wrote a pair of
now-famous papers that helped make this much clearer:
Go to statement
considered harmful
,
and
Notes on structured programming
(PDF).
goto
: the destroyer of abstraction
In these papers, Dijkstra was worried about the problem of how you
write non-trivial software and get it correct. I can't give them due
justice here; there's all kinds of fascinating insights. For example,
you may have heard this quote:
Yep, that's from
Notes on structured programming
. But his major
concern was
abstraction
. He wanted to write programs that are too
big to hold in your head all at once. To do this, you need to treat
parts of the program like a black box – like when you see a Python
program do:
print
(
"Hello world!"
)
then you don't need to know all the details of how
print
is
implemented (string formatting, buffering, cross-platform differences,
...). You just need to know that it will somehow print the text you
give it, and then you can spend your energy thinking about whether
that's what you want to have happen at this point in your code.
Dijkstra wanted languages to support this kind of abstraction.
By this point, block syntax had been invented, and languages like
ALGOL had accumulated ~5 distinct types of control structure: they
still had sequential flow and
goto
:
Same picture of sequential flow and goto flow as before.
And had also acquired variants on if/else, loops, and function calls:
Diagrams with arrows showing the flow control for if
statements, loops, and function calls.
You can implement these higher-level constructs using
goto
, and
early on, that's how people thought of them: as a convenient
shorthand. But what Dijkstra pointed out is that if you look at these
diagrams, there's a big difference between
goto
and the rest. For
everything except
goto
, flow control comes in the top → [stuff
happens] → flow control comes out the bottom. We might call this the
"black box rule": if a control structure has this shape, then in
contexts where you don't care about the details of what happens
internally, you can ignore the [stuff happens] part, and treat the
whole thing as regular sequential flow. And even better, this is also
true of any code that's
composed
out of those pieces. When I look at
this code:
print
(
"Hello world!"
)
I don't have to go read the definition of
print
and all its
transitive dependencies just to figure out how the control flow works.
Maybe inside
print
there's a loop, and inside the loop there's an
if/else, and inside the if/else there's another function call... or
maybe it's something else. It doesn't really matter: I know control
will flow into
print
, the function will do its thing, and then
eventually control will come back to the code I'm reading.
It may seem like this is obvious, but if you have a language with
goto
– a language where functions and everything else are built on
top of
goto
, and
goto
can jump anywhere, at any time – then
these control structures aren't black boxes at all! If you have a
function, and inside the function there's a loop, and inside the loop
there's an if/else, and inside the if/else there's a
goto
... then
that
goto
could send the control anywhere it wants. Maybe control
will suddenly return from another function entirely, one you haven't
even called yet. You don't know!
And this breaks abstraction: it means that
every function call is
potentially a
goto
statement in disguise, and the only way to
know is to keep the entire source code of your system in your head at
once.
As soon as
goto
is in your language, you stop being able do
local reasoning about flow control. That's
why
goto
leads to
spaghetti code.
And now that Dijkstra understood the problem, he was able to solve it.
Here's his revolutionary proposal: we should stop thinking of
if/loops/function calls as shorthands for
goto
, but rather as
fundamental primitives in their own rights – and we should remove
goto
entirely from our languages.
From here in 2018, this seems obvious enough. But have you seen how
programmers react when you try to take away their toys because they're
not smart enough to use them safely? Yeah, some things never change.
In 1969, this proposal was
incredibly controversial
.
Donald Knuth
defended
goto
. People who had become experts on writing code with
goto
quite reasonably resented having to basically learn how to program
again in order to express their ideas using the newer, more
constraining constructs. And of course it required building a whole
new set of languages.
Left: A traditional
goto
. Right: A domesticated
goto
, as
seen in C, C#, 