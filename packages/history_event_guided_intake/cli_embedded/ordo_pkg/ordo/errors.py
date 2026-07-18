class OrdoError(Exception):
    """Base Ordo CLI error."""

class OrdoLintError(OrdoError):
    """Raised when linting fails in strict execution paths."""
