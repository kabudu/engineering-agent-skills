# Python boundaries

Read when translating Python values, parsing, ordering, or exceptions.

- Preserve observable dictionary insertion order, stable-sort ties, duplicate-key replacement behaviour, and iteration-dependent output. `HashMap` has no matching ordering guarantee; `BTreeMap` sorts keys rather than preserving insertion order. Choose a representation for the actual contract.
- Python integers are unbounded. Establish accepted bounds before selecting fixed-width Rust arithmetic, or use an appropriate arbitrary-precision representation when required. Checked overflow makes failure explicit but can still change previously accepted behaviour.
- Unicode predicates, case conversion, line splitting, whitespace trimming, and numeric parsing are not interchangeable merely because method names resemble one another. In particular, `str::lines` does not implement all of Python's `splitlines` separators. Exercise supported separators, digits, empty strings, CRLF, and trailing separators against the original.
- Map `None`, missing keys, empty containers, zero, and false according to their distinct meanings. Do not replace a truthiness check with an absence check without verifying which values the source treats alike.
- Preserve exception categories and data callers inspect, translating them to typed errors where appropriate. A single generic string can erase a recoverable distinction. Preserve normal absence separately from failures.
- Use structs for known records and enums/traits for genuine variation. Avoid a dynamic-object framework solely to imitate Python's representation. Preserve laziness, side-effect order, and resource cleanup when generators or context managers are part of the interface.
- Prefer standard Rust methods plus a narrow adapter for required differences. Do not silently exclude supported input or reproduce Python's entire runtime. Document approved compatibility choices and validate them with the source tests and differential cases.

Primary references: [Python built-in types](https://docs.python.org/3/library/stdtypes.html) and [exceptions](https://docs.python.org/3/library/exceptions.html).
