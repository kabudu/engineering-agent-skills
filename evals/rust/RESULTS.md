# Local validation results

Date: 25 October 2026.

Upstream: BeautifulRust revision `2b2d53a66f6f36ab4b8d6a93070183d91e77fad4`.
Counts use Python whitespace splitting of the complete SKILL.md, including frontmatter and attribution; they are word counts, not tokenizer measurements.

| Entrypoint | Upstream words | Adapted words | Reduction |
| --- | ---: | ---: | ---: |
| rust-best-practices | 4,422 | 912 | 79.4% |
| rust-review | 1,224 | 542 | 55.7% |
| Combined | 5,646 | 1,454 | 74.2% |

Supporting references, notices, and tool output are excluded from this entrypoint comparison. Reference-heavy tasks will have smaller savings; total input/output token savings remain unmeasured.

Checks performed using Python 3.9.6 and rustc 1.97.0:

- Both skills passed skill-creator's quick_validate.py (frontmatter and naming validation).
- `python3 evals/rust/check_fixtures.py` compiled the review fixture as a library without executing its unsound function, and passed the clean fixture's boundary test.
- The same script checked Markdown resource links within both skills and the presence of Morgan Linton's retained MIT notice.
- Both distributed licence files were compared byte-for-byte with the pinned upstream LICENSE.
- `git diff --check` passed.

No independent agent runs, three-condition comparisons, automatic-routing experiments, or total-token measurements have been performed. The six behavioural evaluation cases and protocol are ready for those runs; these local checks do not establish behavioural equivalence.
