# API and Cargo decisions

Read when changing externally consumed interfaces, crate dependencies, or features.

- Establish who consumes the interface and the compatibility promise. A local module, internal workspace crate, published library, CLI, and wire format have different evolution constraints. Review downstream callers, not just compilation of the changed crate.
- Keep fields private when enforcing invariants or preserving evolution options. Passive data structures may intentionally expose fields. Newtypes should prevent a meaningful mistake; avoid wrappers that merely rename types.
- Prefer conventional traits (`From`, `TryFrom`, `FromStr`, `IntoIterator`, `Default`) where their contracts fit. Do not implement infallible conversion from arbitrary input into an invariant-bearing type. A zero-argument constructor warrants `Default` only if a meaningful default exists.
- Validate agreement among ordering, equality, and hashing, including ignored metadata, floats, and custom key projections. Test laws and collection behaviour where these implementations are custom.
- Consider whether a public enum should support future variants, whether downstream trait implementations are intended, and whether dependency types are deliberately exposed. Adding `non_exhaustive` or sealing an existing public trait can itself break users.
- Diagnose unclear boolean arguments with their call sites; named options or enums help when meaning is ambiguous. Avoid turning a small stable API into a builder merely to satisfy an argument-count threshold.
- Keep failure types useful to consumers and preserve causes without exposing secrets. Changing errors, panic behaviour, bounds, ownership, or synchronous/asynchronous execution can affect compatibility even if the function name stays the same.
- Inspect feature definitions, target-specific dependencies, `no_std`/`alloc` support, MSRV, and documented supported combinations. Prefer additive features for interoperable libraries. Test default and relevant alternate configurations; all features together may be invalid or miss minimal-feature bugs.
- Reuse workspace dependency/lint policy. Assess new dependencies for maintenance, platform support, build scripts, proc macros, and MSRV cost. Preserve lockfiles according to project policy. Do not upgrade toolchains or dependencies incidentally.
- Check that configured lints actually fire for the declared MSRV. Clippy can suppress MSRV-sensitive diagnostics even on a newer compiler: `allow_attributes` and `allow_attributes_without_reason` do not fire when the declared `rust-version` is below 1.81, where their `#[expect]`-based guidance is unavailable. Do not raise a project's MSRV just to enable these lints; use compatible policy and verify representative violations.
- Run relevant public API integration tests, doctests, and documentation diagnostics. Missing-doc and warning failures require the appropriate lint configuration; `cargo doc` alone is not such a policy.

Consult primary documentation when version-sensitive behaviour matters:

- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [Cargo features](https://doc.rust-lang.org/cargo/reference/features.html)
- [Cargo SemVer compatibility](https://doc.rust-lang.org/cargo/reference/semver.html)
- [Rustdoc lints](https://doc.rust-lang.org/rustdoc/lints.html)

MSRV-specific lint behaviour is documented in [BeautifulRust v1.4.0](https://github.com/morganlinton/BeautifulRust/blob/a2b22682fa69b5e2d41a5d041663df7d51aac521/lints/lints.toml); see also [Clippy allow_attributes](https://clippy.rust-lang.org/master/index.html#allow_attributes).
