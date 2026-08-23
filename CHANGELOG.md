# Changelog

All notable changes to **OraCLI 10G** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0-alpha] - 2026-08-23

### Added
- Core architecture, project layout, and pyproject.toml configuration.
- Interactive SQL*Plus 10g terminal shell with `SQL>` prompt and multiline continuation `  2  `.
- Multiline input buffer with quote, string literal, and comment awareness.
- Oracle SQL to SQLite transpiler supporting `NUMBER`, `VARCHAR2`, `DATE`, `CHAR`, `INTEGER`.
- SQLite database adapter with in-memory and file-backed persistence.
- Oracle SQL*Plus table and feedback output formatter (aligned headers, dashed separators, right-aligned numbers).
- Error mapper for `ORA-00942`, `ORA-00904`, `ORA-00001`, `ORA-01400`, `ORA-00933`.
- Basic SQL*Plus commands (`EXIT`, `QUIT`, `SHOW USER`, `SET`).
- Test suite with unit and end-to-end integration tests.
