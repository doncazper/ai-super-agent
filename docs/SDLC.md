# SDLC

The project follows a safety-first lifecycle.

1. Specification: define mission, non-goals, architecture, trust boundaries, and acceptance criteria.
2. Requirements: define functional and safety requirements before implementation.
3. Design: describe interfaces, data flow, policies, and audit behavior.
4. Threat model: identify abuse paths, unsafe defaults, and mitigations.
5. Implementation: add the smallest milestone-scoped code needed.
6. Tests: add unit/integration/security tests matching the risk.
7. Security review: confirm policy, permission, approval, and audit behavior.
8. Release gate: check docs, tests, forbidden capabilities, and approvals.
9. Documentation: update milestone docs and completion report.
10. Monitoring and iteration: inspect audit output, failures, and user feedback.

## Mini-SDLC for Every Milestone

1. Confirm scope.
2. Confirm non-goals.
3. Define requirements.
4. Define risks and threat-model notes.
5. Implement.
6. Add tests.
7. Run tests.
8. Update docs.
9. Update completion report.
10. Stop at approval gates.
