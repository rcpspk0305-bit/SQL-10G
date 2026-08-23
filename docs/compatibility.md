# Oracle 10g SQL*Plus Feature Compatibility Matrix

OraCLI 10G reproduces the key syntax, semantics, command interface, and feedback conventions of **Oracle SQL*Plus 10g** for academic and laboratory use.

---

## 1. Compatibility Summary Table

| Category | Oracle 10g Feature | OraCLI Implementation | Compatibility Status |
|---|---|---|---|
| **DDL** | `CREATE TABLE` | PK, FK, UNIQUE, NOT NULL, CHECK, DEFAULT | ✅ FULLY SUPPORTED |
| **DDL** | `ALTER TABLE` | Add / Drop column, Rename table | ✅ FULLY SUPPORTED |
| **DDL** | `DROP TABLE` | Drop table with cleanup | ✅ FULLY SUPPORTED |
| **DDL** | `TRUNCATE TABLE` | Fast table truncation | ✅ FULLY SUPPORTED |
| **DDL** | `RENAME` | `RENAME old TO new` | ✅ FULLY SUPPORTED |
| **DDL** | `CREATE / DROP INDEX` | B-tree index creation and drop | ✅ FULLY SUPPORTED |
| **DML** | `INSERT INTO` | Single row and `INSERT INTO ... SELECT` | ✅ FULLY SUPPORTED |
| **DML** | `UPDATE` | With expressions, `WHERE`, arithmetic | ✅ FULLY SUPPORTED |
| **DML** | `DELETE FROM` | With `WHERE`, referential cascade | ✅ FULLY SUPPORTED |
| **DML** | Feedback Messages | "N row(s) created.", "N row(s) updated." | ✅ FULLY SUPPORTED |
| **DCL** | `GRANT / REVOKE` | `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `ALL` | ✅ FULLY SUPPORTED |
| **DCL** | Security Model | Prevents unauthorized queries with `ORA-01031` | ✅ FULLY SUPPORTED |
| **TCL** | `COMMIT` | Transaction persistence | ✅ FULLY SUPPORTED |
| **TCL** | `ROLLBACK` | Full transaction rollback | ✅ FULLY SUPPORTED |
| **TCL** | `SAVEPOINT` | Savepoint creation | ✅ FULLY SUPPORTED |
| **TCL** | `ROLLBACK TO` | Partial rollback to savepoint | ✅ FULLY SUPPORTED |
| **Queries**| Filtering & Sorting | `WHERE`, `DISTINCT`, `ORDER BY (ASC/DESC/alias)` | ✅ FULLY SUPPORTED |
| **Queries**| Aggregates | `COUNT`, `SUM`, `AVG`, `MIN`, `MAX` | ✅ FULLY SUPPORTED |
| **Queries**| Grouping | `GROUP BY`, `HAVING` | ✅ FULLY SUPPORTED |
| **Queries**| Joins | `INNER JOIN`, `LEFT OUTER JOIN`, `CROSS JOIN` | ✅ FULLY SUPPORTED |
| **Queries**| Set Operators | `UNION`, `UNION ALL`, `INTERSECT`, `MINUS` | ✅ FULLY SUPPORTED |
| **Referential**| `ON DELETE CASCADE` | Automatic cascading child row deletion | ✅ FULLY SUPPORTED |
| **Views** | Standard Views | `CREATE VIEW`, `DROP VIEW`, query view | ✅ FULLY SUPPORTED |
| **Views** | Materialized Views | `CREATE/REFRESH/DROP MATERIALIZED VIEW` | ✅ FULLY SUPPORTED |
| **Functions**| Built-in Scalar | `NVL`, `SYSDATE`, `INSTR`, `TRUNC`, `UPPER`, `\|\|` | ✅ FULLY SUPPORTED |
| **SQL\*Plus**| Commands | `DESC / DESCRIBE`, `SHOW`, `SET`, `CLEAR`, `RUN` | ✅ FULLY SUPPORTED |
| **System** | `DUAL` Table | Built-in 1-row dummy table | ✅ FULLY SUPPORTED |
| **Errors** | Canonical Codes | `ORA-00942`, `ORA-00904`, `ORA-00001`, `ORA-01031` | ✅ FULLY SUPPORTED |

---

## 2. Test Verification

Every subsystem listed above is automatically exercised and validated in every CI run:
- **Pytest Integration Suite**: `tests/integration/test_exhaustive_suite.py` (26 test cases)
- **Pre-Deployment Smoke Test**: `scripts/smoke_test.py` (9 validation stages)
