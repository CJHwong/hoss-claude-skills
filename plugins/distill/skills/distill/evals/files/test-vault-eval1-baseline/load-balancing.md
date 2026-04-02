# Load Balancing

**Source:** https://samwho.dev/load-balancing/
**Tags:** distributed-systems
**Saved:** 2024-03-31

## Algorithms Compared

### Round Robin
Distributes requests sequentially. Still nginx's default. Has the best median latency but poor tail latency (95th, 99th percentiles) because it sends requests to overloaded servers indiscriminately.

### Weighted Round Robin
Assigns manual weights based on known server capacity. Impractical at scale because "boiling server performance down to a single number is hard."

### Dynamic Weighted Round Robin
Automatically adjusts weights using latency as a proxy metric. Adapts to performance changes over time without manual configuration.

### Least Connections
Tracks active connections per server, routes new requests to the least-busy one. "Great balance between simplicity and performance." Ensures available resources stay utilized.

### PEWMA (Peak Exponentially Weighted Moving Average)
Most sophisticated - combines latency tracking with connection awareness. Recent request latencies receive greater weight. Eventually avoids slower servers entirely.

## Trade-offs

| Algorithm | Simplicity | Median Latency | Tail Latency | Overload Handling |
|-----------|-----------|----------------|--------------|-------------------|
| Round Robin | Best | Best | Poor | Poor |
| Least Connections | Good | Good | Good | Good |
| PEWMA | Low | Good | Best | Drops more requests |

## Practical Takeaway

Higher percentiles (95th, 99th) matter more than medians for user experience. Least connections is the sweet spot for most workloads. PEWMA optimizes tail latency but drops more requests under extreme load. Benchmark your own workloads rather than relying on generic advice.
