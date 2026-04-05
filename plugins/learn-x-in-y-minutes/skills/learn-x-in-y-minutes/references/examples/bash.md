---
name: Bash
contributors:
    - ["Max Yankov", "https://github.com/golergka"]
    - ["Darren Lin", "https://github.com/CogBear"]
filename: LearnBash.sh
---

Bash is a name of the unix shell, which was also distributed as the shell
for the GNU operating system and as the default shell on most Linux distros.
Nearly all examples below can be a part of a shell script
or executed directly in the shell.

```bash
#!/usr/bin/env bash
# First line of the script is the shebang which tells the system how to execute
# the script: https://en.wikipedia.org/wiki/Shebang_(Unix)
# As you already figured, comments start with #. Shebang is also a comment.

# Simple hello world example:
echo "Hello world!" # => Hello world!

# Each command starts on a new line, or after a semicolon:
echo "This is the first command"; echo "This is the second command"
# => This is the first command
# => This is the second command

# Declaring a variable looks like this:
variable="Some string"

# But not like this:
variable = "Some string" # => returns error "variable: command not found"

# Using the variable:
echo "$variable" # => Some string
echo '$variable' # => $variable
# Note that ' (single quote) won't expand variables!

# Parameter expansion ${...}:
echo "${variable}" # => Some string

# String substitution in variables:
echo "${variable/Some/A}" # => A string

# Declare an array with 6 elements:
array=(one two three four five six)
# Print the first element:
echo "${array[0]}" # => "one"
# Print all elements:
echo "${array[@]}" # => "one two three four five six"
# Print the number of elements:
echo "${#array[@]}" # => "6"

# Built-in variables:
echo "Last program's return value: $?"
echo "Script's PID: $$"
echo "Number of arguments passed to script: $#"
echo "All arguments passed to script: $@"

# Reading a value from input:
echo "What's your name?"
read name
# Note that we didn't need to declare a new variable.
echo "Hello, $name!"

# We have the usual if structure:
# use 'man test' for more info about conditionals
if [ "$name" != $USER ]
then
    echo "Your name isn't your username"
else
    echo "Your name is your username"
fi
# Note: if $name is empty, bash sees the above condition as:
# if [ "" != $USER ]
# which is true, so the output is: "Your name isn't your username"

# There is also conditional execution
echo "Always executed" || echo "Only executed if first command fails"
echo "Always executed" && echo "Only executed if first command succeeds"

# A single ampersand & after a command runs it in the background. A background command's
# output is printed to the terminal, but it cannot read from the input.
sleep 30 &
# List background jobs
jobs # => [1]+  Running                 sleep 30 &
```

<!-- Source: https://github.com/adambard/learnxinyminutes-docs/blob/master/bash.md (truncated for reference) -->
