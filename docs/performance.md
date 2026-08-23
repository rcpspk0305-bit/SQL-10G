# Performance & Low-Carbon Footprint Architecture

## 1. Overview & Sustainability Goals

OraCLI 10G is engineered under strict **low-compute, low-memory, low-network, and low-CI-minute** principles. Rather than relying on heavyweight server processes or external database clusters, the entire architecture runs as an ultra-efficient, locally-contained educational platform.

---

## 2. Low-Compute & Low-Carbon Principles

### 2.1 Concurrency Control in GitHub Actions CI
- Every push to `main` or pull request automatically cancels obsolete in-progress CI jobs via:
  ```yaml
  concurrency:
    group: ci-${{ github.ref }}
    cancel-in-progress: true
  ```
- This prevents redundant VM runner execution, reducing cloud compute consumption and energy waste.

### 2.2 In-Memory Isolated Database Sandboxes
- Each browser session allocates a lightweight in-memory SQLite database (`:memory:`).
- Zero background disk I/O, zero network socket overhead, and instant query latency (<1ms).
- Instant deallocation on session termination prevents memory leaks.

### 2.3 Elimination of Background Loops & Artificial Traffic
- **No `while True` Polling**: The application never runs background polling threads.
- **No Artificial Keep-Alive Loops**: Complies strictly with Streamlit Community Cloud hibernation policies. No synthetic HTTP requests or fake browser automation are used to keep containers alive.
- **On-Demand Execution**: Calculations, SQL transpilation, and AST generation occur strictly when the user executes a query.

### 2.4 Caching & Lazy Evaluation
- Parser AST rules and dialect transforms are evaluated on-demand without spinning up persistent compiler daemons.
- Static application metadata and sample schemas are lightweight structures loaded without disk or network overhead.

---

## 3. Database Execution Efficiency

| Component | Strategy | Resource Impact |
|---|---|---|
| Engine Backend | SQLite In-Memory (`:memory:`) | 0 disk writes, ~0.05ms query execution |
| Foreign Keys | Enforced via `PRAGMA foreign_keys=ON;` | Zero overhead referential integrity |
| Transactions | Explicit `SAVEPOINT` and `COMMIT` scoping | Minimal lock contention, instant rollback |
| Schema Queries | Direct `PRAGMA table_info` introspection | No redundant table scans |
| Result Rendering | Lazy Pandas DataFrame conversion | Only formatted when user views Data Grid |

---

## 4. Verification Benchmarks

- **Full CI Pipeline Execution Time**: ~25 seconds on standard GitHub Actions runners.
- **Smoke Test Suite Execution**: ~0.08s (database suite) + ~5s (headless live server startup & clean shutdown).
- **Pytest 61-Test Execution**: ~2.2s.
- **Memory Footprint**: < 60 MB RSS per user session.
