---
name: JWT dependency choice
description: Why authentication uses PyJWT rather than python-jose.
---

Use PyJWT without the python-ecdsa dependency for the application's shared-secret JWT authentication.

**Why:** The dependency audit identified a timing vulnerability in python-ecdsa that upstream considers out of scope and does not plan to fix. Updating python-jose alone would retain that dependency. The replacement preserves standard HS256 tokens and existing sessions.

**How to apply:** Avoid reintroducing python-jose or python-ecdsa during authentication changes. Keep the decoder's explicit algorithm allowlist and test compatibility with existing tokens when changing JWT implementations.
