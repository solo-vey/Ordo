# Legacy all-in-one implementation instruction

1. First confirm the requested scope with the user.
2. Scope confirmation does not authorize repository mutation.
3. Assess change complexity before selecting an execution route.
4. Select the execution route and obtain explicit mutation authorization.
5. Only after authorization, implement the code changes.
6. Run code review and tests before packaging.
7. Packaging must include source code, tests, repository patch, and test evidence.
8. Do not label the package release-ready when implementation evidence is missing.
9. If unauthorized mutation occurs, stop further changes and route to review; do not automatically roll back.
10. Return a final package with a traceable completion report.
