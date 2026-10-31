# Security and boundaries

Sources reviewed 2026-10-31. Apply checks to affected trust boundaries; ordinary edits do not require a repository-wide security audit.

## Data, authority, and effects

Use prepared statements for database values. Placeholders cannot represent arbitrary SQL identifiers or keywords; map requested sorting and column choices to an explicit allowlist. Check transaction rollback and concurrent-update semantics where the operation needs atomicity. Follow the database driver's actual placeholder and error behaviour.

Encode output at its destination. HTML text, attributes, JavaScript, URLs, and JSON require different handling. Prefer the framework's autoescaping templates and response APIs, understanding their context limits. HTML encoding does not make an arbitrary URL safe. Input validation and output encoding solve separate problems.

Check authorisation for the particular object and operation, not merely authentication. For cookie-authenticated state changes, follow the framework's CSRF protection and session configuration. Use established password hashing and verification APIs; do not invent cryptography or log credentials, tokens, or sensitive request bodies.

Do not deserialize untrusted PHP objects. Decode interchange data into validated structures, with explicit error handling and size/depth bounds. Treat uploads, filesystem paths, URL fetches, and process arguments as separate boundaries: constrain allowed destinations and resources, prevent traversal, and prefer APIs that avoid a shell. Escaping alone does not establish authorisation or prevent SSRF.

For long-running workers, review state retained between jobs/requests, resource cleanup, and idempotency. Bound retries and external calls; preserve failure visibility and avoid retrying irreversible operations without a safe contract. Do not add concurrency machinery solely because a runtime supports it.

## Primary sources

- [PDO prepared statements](https://www.php.net/manual/en/pdo.prepared-statements.php).
- [HTML escaping](https://www.php.net/manual/en/function.htmlspecialchars.php): HTML-specific behaviour, not universal sanitisation.
- [Password hashing](https://www.php.net/manual/en/book.password.php).
- [Unserialization warnings](https://www.php.net/manual/en/function.unserialize.php).
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/): consult the relevant authorisation, XSS, CSRF, SSRF, or upload guidance when that boundary changes.

Use the installed framework's official security documentation for concrete middleware and configuration. Do not assume Laravel, Symfony, WordPress, and standalone PHP share the same integration contracts.
