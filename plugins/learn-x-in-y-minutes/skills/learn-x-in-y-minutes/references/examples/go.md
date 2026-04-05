---
name: Go
filename: learngo.go
contributors:
    - ["Sonia Keys", "https://github.com/soniakeys"]
    - ["John Arundel", "https://github.com/bitfield"]
---

Go was created out of the need to get work done. It's not the latest trend
in programming language theory, but it is a way to solve real-world problems.

It draws concepts from imperative languages with static typing. It's fast to
compile and fast to execute, it adds easy-to-understand concurrency because
multi-core CPUs are now common, and it's used successfully in large codebases.

```go
// Single line comment
/* Multi-
   line comment */

// A package clause starts every source file.
// main is a special name declaring an executable rather than a library.
package main

// Import declaration declares library packages referenced in this file.
import (
    "fmt"      // A package in the Go standard library.
    "math"     // Math library.
    "net/http" // Yes, a web server!
    "strconv"  // String conversions.
)

// A function definition. Main is special. It is the entry point for the
// executable program.
func main() {
    // Println outputs a line to stdout.
    fmt.Println("Hello world!")

    beyondHello()
}

// Functions have parameters in parentheses.
// If there are no parameters, empty parentheses are still required.
func beyondHello() {
    var x int // Variable declaration. Variables must be declared before use.
    x = 3
    // "Short" declarations use := to infer the type, declare, and assign.
    y := 4
    sum, prod := learnMultiple(x, y)
    fmt.Println("sum:", sum, "prod:", prod)
    learnTypes()
}

// Functions can have parameters and (multiple!) return values.
func learnMultiple(x, y int) (sum, prod int) {
    return x + y, x * y // Return two values.
}

func learnTypes() {
    str := "Learn Go!"      // string type.
    f   := 3.14159          // float64.
    c   := 3 + 4i           // complex128.

    var a4 [4]int            // An array of 4 ints, initialized to all 0.
    s3 := []int{4, 5, 9}    // A slice — dynamic size, unlike arrays.
    s4 := make([]int, 4)    // Allocates slice of 4 ints, initialized to 0.

    // Maps are a dynamically growable associative array type.
    m := map[string]int{"three": 3, "four": 4}
    m["one"] = 1

    // Unused variables are an error in Go.
    _, _, _, _, _, _, _, _, _ = str, f, c, a4, s3, s4, m, math.Pi, strconv.Itoa

    fmt.Println(str, f, c, a4, s3, s4, m)

    learnFlowControl()
}

func learnFlowControl() {
    // If statements require brace brackets, and don't need parentheses.
    if true {
        fmt.Println("told ya")
    }

    // Formatting is standardized by the "go fmt" command.
    for x := 0; x < 3; x++ {
        fmt.Println("iteration", x)
    }

    // You can use range to iterate over an array, a slice, a string, a map,
    // or a channel. range returns one (channel) or two values (array, slice,
    // string and map).
    for key, value := range map[string]int{"one": 1, "two": 2, "three": 3} {
        fmt.Printf("key=%s, value=%d\n", key, value)
    }

    // Like for, := in an if statement means to declare and assign y first,
    // then test y > x.
    if y := expensiveComputation(); y > 0 {
        fmt.Println("y is greater than 0")
    }
}

func expensiveComputation() float64 {
    return math.Sqrt(3.0)
}

// Go is fully capable of HTTP servers.
func learnWebProgramming() {
    // The first parameter of ListenAndServe is the TCP address to listen to,
    // and the second is a handler.
    if err := http.ListenAndServe(":8080", pair{}); err != nil {
        panic(err)
    }
}

// Make pair implement the http.Handler interface by implementing its only method,
// ServeHTTP.
type pair struct {
    x, y int
}

func (p pair) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    // Serve data with a method of http.ResponseWriter.
    fmt.Fprintf(w, "You learned Go in Y minutes!")
}
```

<!-- Source: https://github.com/adambard/learnxinyminutes-docs/blob/master/go.md (truncated for reference) -->
