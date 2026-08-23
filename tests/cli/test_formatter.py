"""Unit tests for OutputFormatter."""

from app.cli.formatter import OutputFormatter
from app.cli.session import Session
from app.database.adapter import QueryResult


def test_format_query_result_basic():
    formatter = OutputFormatter()
    session = Session()

    result = QueryResult(
        columns=["rollno", "name", "cgpa"],
        column_types=["INTEGER", "TEXT", "REAL"],
        rows=[[101, "Rahul", 8.7], [102, "Priya", 9.1]],
        row_count=2,
        feedback_message="",
    )

    formatted = formatter.format_query_result(result, session)

    assert "ROLLNO" in formatted
    assert "NAME" in formatted
    assert "CGPA" in formatted
    assert "------" in formatted
    assert "Rahul" in formatted
    assert "8.7" in formatted
    assert "2 rows selected." in formatted


def test_format_query_result_empty():
    formatter = OutputFormatter()
    session = Session()

    result = QueryResult(
        columns=["id", "val"],
        column_types=["INTEGER", "TEXT"],
        rows=[],
        row_count=0,
        feedback_message="",
    )

    formatted = formatter.format_query_result(result, session)
    assert formatted.strip() == "no rows selected"


def test_format_query_result_null_handling():
    formatter = OutputFormatter()
    session = Session(null_value="(null)")

    result = QueryResult(
        columns=["id", "val"],
        column_types=["INTEGER", "TEXT"],
        rows=[[1, None]],
        row_count=1,
        feedback_message="",
    )

    formatted = formatter.format_query_result(result, session)
    assert "(null)" in formatted
    assert "1 row selected." in formatted


def test_format_heading_off():
    formatter = OutputFormatter()
    session = Session(heading=False)

    result = QueryResult(
        columns=["rollno", "name"],
        column_types=["INTEGER", "TEXT"],
        rows=[[101, "Rahul"]],
        row_count=1,
        feedback_message="",
    )

    formatted = formatter.format_query_result(result, session)
    assert "ROLLNO" not in formatted
    assert "101" in formatted
    assert "Rahul" in formatted
