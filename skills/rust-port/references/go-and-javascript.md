# Go, JavaScript, and TypeScript boundaries

Read the section for the source language; the choice of representation follows the observed contract.

## Go

- Translate `(value, error)` to `Result` without losing meaningful partial values, sentinel errors, or wrapped causes. Decide how source panics map separately from expected errors.
- Go strings can carry arbitrary bytes. Validate before using `String` or `&str` where UTF-8 is required. Preserve byte-versus-rune iteration semantics.
- Check whether nil and empty slices/maps are observably distinct, including serialization. Interfaces can contain typed nil values; a blanket `Option` translation may lose a state.
- Goroutines, channels, cancellation, shutdown, and select behaviour need an explicit execution model. Preserve ownership and termination responsibilities instead of translating every goroutine into an unbounded thread or detached task. Map supported channel closure and error behaviour deliberately.
- Preserve specified ordering while recognising that unspecified map order is not a stable contract. Check platform-dependent `int` widths and overflow semantics against supported targets.

Primary reference: [Go specification](https://go.dev/ref/spec).

## JavaScript and TypeScript

- Distinguish an absent property, `undefined`, `null`, and a present value when callers do. Use an enum or another explicit representation for more than two states; `Option<T>` alone cannot preserve all four.
- JavaScript numbers are normally IEEE-754 doubles. Check precision, NaN, signed zero, infinities, coercion, and overflow expectations before choosing Rust integers or `f64`. Treat `BigInt` as a separate contract.
- JavaScript strings expose UTF-16 code-unit behaviour. Rust text is UTF-8; indexing, length, slicing, surrogate handling, and iteration may differ. Preserve the operations actually used by callers rather than assuming a Rust string is interchangeable.
- Preserve object-key enumeration rules and asynchronous ordering where observable. Promise rejection, cancellation, callbacks, and resource cleanup need explicit Rust error and task ownership models.
- TypeScript annotations do not validate runtime input. Preserve validation and distinguish source type assumptions from checks actually enforced on untrusted data.

Primary reference: [ECMAScript specification](https://tc39.es/ecma262/).
