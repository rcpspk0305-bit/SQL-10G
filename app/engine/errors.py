"""Oracle error representation and SQLite exception mapping."""


class OracleError(Exception):
    """Base exception for all Oracle-style errors."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


class ORA00942TableOrViewDoesNotExist(OracleError):
    """ORA-00942: table or view does not exist."""

    def __init__(self, object_name: str = "") -> None:
        msg = (
            f'table or view does not exist: "{object_name}"'
            if object_name
            else "table or view does not exist"
        )
        super().__init__("ORA-00942", msg)


class ORA00904InvalidIdentifier(OracleError):
    """ORA-00904: invalid identifier."""

    def __init__(self, identifier: str = "") -> None:
        msg = f'"{identifier}": invalid identifier' if identifier else "invalid identifier"
        super().__init__("ORA-00904", msg)


class ORA00933SQLCommandNotProperlyEnded(OracleError):
    """ORA-00933: SQL command not properly ended."""

    def __init__(self, details: str = "") -> None:
        msg = (
            f"SQL command not properly ended ({details})"
            if details
            else "SQL command not properly ended"
        )
        super().__init__("ORA-00933", msg)


class ORA00955NameAlreadyUsed(OracleError):
    """ORA-00955: name is already used by an existing object."""

    def __init__(self, object_name: str = "") -> None:
        msg = (
            f'name is already used by an existing object: "{object_name}"'
            if object_name
            else "name is already used by an existing object"
        )
        super().__init__("ORA-00955", msg)


class ORA01400CannotInsertNull(OracleError):
    """ORA-01400: cannot insert NULL into column."""

    def __init__(self, column: str = "") -> None:
        msg = f'cannot insert NULL into ("{column}")' if column else "cannot insert NULL"
        super().__init__("ORA-01400", msg)


class ORA00001UniqueConstraintViolated(OracleError):
    """ORA-00001: unique constraint violated."""

    def __init__(self, constraint_name: str = "") -> None:
        msg = (
            f"unique constraint ({constraint_name}) violated"
            if constraint_name
            else "unique constraint violated"
        )
        super().__init__("ORA-00001", msg)


class ORA02291IntegrityConstraintViolatedParent(OracleError):
    """ORA-02291: integrity constraint violated - parent key not found."""

    def __init__(self, constraint_name: str = "") -> None:
        msg = (
            f"integrity constraint ({constraint_name}) violated - parent key not found"
            if constraint_name
            else "integrity constraint violated - parent key not found"
        )
        super().__init__("ORA-02291", msg)


class ORA02292IntegrityConstraintViolatedChild(OracleError):
    """ORA-02292: integrity constraint violated - child record found."""

    def __init__(self, constraint_name: str = "") -> None:
        msg = (
            f"integrity constraint ({constraint_name}) violated - child record found"
            if constraint_name
            else "integrity constraint violated - child record found"
        )
        super().__init__("ORA-02292", msg)


def map_sqlite_error(exc: Exception) -> OracleError:
    """Translate an underlying SQLite / database exception to an OracleError."""
    err_str = str(exc).strip()
    lower_err = err_str.lower()

    if "no such table" in lower_err:
        table_name = err_str.split("no such table:")[-1].strip()
        return ORA00942TableOrViewDoesNotExist(table_name)

    if "no such column" in lower_err:
        col_name = err_str.split("no such column:")[-1].strip()
        return ORA00904InvalidIdentifier(col_name)

    if "table" in lower_err and "already exists" in lower_err:
        table_name = err_str.split("already exists")[0].split("table")[-1].strip()
        return ORA00955NameAlreadyUsed(table_name)

    if "unique constraint failed" in lower_err or "primary key constraint failed" in lower_err:
        col = err_str.split(":")[-1].strip() if ":" in err_str else ""
        return ORA00001UniqueConstraintViolated(col)

    if "not null constraint failed" in lower_err:
        col = err_str.split("NOT NULL constraint failed:")[-1].strip()
        return ORA01400CannotInsertNull(col)

    if "foreign key constraint failed" in lower_err:
        return ORA02291IntegrityConstraintViolatedParent()

    if "syntax error" in lower_err or "parse error" in lower_err:
        return ORA00933SQLCommandNotProperlyEnded(err_str)

    # General fallback
    return OracleError("ORA-00600", f"internal error code, arguments: [{err_str}]")
