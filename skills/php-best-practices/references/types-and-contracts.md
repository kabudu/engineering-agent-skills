# Types and observable contracts

Sources reviewed 2026-10-31. Prefer the project's established public contracts to mechanical modernisation.

## PHP semantics that change outcomes

- `isset` treats a null value like an absent key; `array_key_exists` distinguishes them. Null coalescing also treats missing and null alike. `empty` includes values such as zero and the string "0"; it is unsuitable when those are valid supplied values.
- Use strict equality when identity of type and value is intended. Do not mechanically replace intentional numeric comparisons. Validate numeric strings before conversion, including range and precision; casting can discard information. Use integer minor units or an appropriate decimal representation for money according to domain requirements.
- PHP arrays are ordered maps with key conversion rules. Numeric string keys can become integer keys; sparse integer keys can serialize as a JSON object. Preserve list/map distinctions and duplicate-key policy across boundaries.
- Strings are byte sequences. Choose byte or Unicode operations deliberately, establish encoding, and check required extensions. Do not assume byte length measures user-visible characters.
- Scalar argument strictness is determined by the caller for ordinary userland calls. Strict typing has specific exceptions and internal-call behaviour; consult the manual when relevant. It does not validate untrusted shapes, ranges, encodings, or domain rules.

## Model useful states

Use nullable types for legitimate absence, not as a universal error channel. Prefer a small value object or enum when it prevents real invalid states and the supported runtime permits it. Avoid replacing every array with a class; array shapes and generic annotations can clarify structured internal data without expanding the API.

Retain existing coercion and error contracts during refactors. Narrowing mixed input to a native type can reject previously valid callers. Wrapping an exception should retain its cause and avoid leaking sensitive inputs. Handle normal false-return APIs explicitly rather than losing the distinction through truthiness.

Check database nullability, ORM casts, serializer output, and external payloads before adding property types or readonly. Do not expose mutable internals accidentally or apply immutability modifiers where framework lifecycle operations require mutation. Use framework documentation for the installed version rather than inventing replacement infrastructure.

## Primary sources

- [Type declarations and strict typing](https://www.php.net/manual/en/language.types.declarations.php).
- [Arrays and key conversion](https://www.php.net/manual/en/language.types.array.php).
- [Comparison rules](https://www.php.net/manual/en/language.operators.comparison.php).
- [Strings](https://www.php.net/manual/en/language.types.string.php).
- [JSON encoding](https://www.php.net/manual/en/function.json-encode.php).
