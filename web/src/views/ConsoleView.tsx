import React from 'react';
import { SQLEditor } from '../components/SQLEditor';
import { OutputPane } from '../components/OutputPane';
import { ExecuteResponse } from '../types';

interface ConsoleViewProps {
  sql: string;
  setSql: (val: string) => void;
  onExecute: () => void;
  onClear: () => void;
  onLoadSample: () => void;
  isExecuting: boolean;
  response: ExecuteResponse | null;
  error: string | null;
}

const CATEGORY_SNIPPETS: { label: string; items: { name: string; sql: string }[] }[] = [
  {
    label: 'DDL',
    items: [
      { name: 'CREATE TABLE', sql: 'CREATE TABLE student (\n    rollno NUMBER PRIMARY KEY,\n    name VARCHAR2(50) NOT NULL,\n    cgpa NUMBER(3,2)\n);' },
      { name: 'ALTER TABLE', sql: 'ALTER TABLE student ADD (email VARCHAR2(100));' },
      { name: 'DROP TABLE', sql: 'DROP TABLE student;' },
      { name: 'TRUNCATE', sql: 'TRUNCATE TABLE student;' },
      { name: 'CREATE INDEX', sql: 'CREATE INDEX idx_student_name ON student (name);' },
      { name: 'CREATE VIEW', sql: 'CREATE VIEW student_view AS\nSELECT rollno, name FROM student;' },
    ],
  },
  {
    label: 'DML',
    items: [
      { name: 'INSERT', sql: "INSERT INTO student VALUES (101, 'Rahul', 8.7);" },
      { name: 'UPDATE', sql: "UPDATE student SET cgpa = 9.0 WHERE rollno = 101;" },
      { name: 'DELETE', sql: "DELETE FROM student WHERE rollno = 101;" },
      { name: 'SELECT', sql: "SELECT * FROM student;" },
    ],
  },
  {
    label: 'DCL',
    items: [
      { name: 'GRANT', sql: 'GRANT SELECT, INSERT ON student TO student_user;' },
      { name: 'REVOKE', sql: 'REVOKE INSERT ON student FROM student_user;' },
    ],
  },
  {
    label: 'TCL',
    items: [
      { name: 'COMMIT', sql: 'COMMIT;' },
      { name: 'ROLLBACK', sql: 'ROLLBACK;' },
      { name: 'SAVEPOINT', sql: 'SAVEPOINT sp1;' },
      { name: 'ROLLBACK TO', sql: 'ROLLBACK TO sp1;' },
    ],
  },
  {
    label: 'QUERY',
    items: [
      { name: 'WHERE & ORDER', sql: 'SELECT name, cgpa FROM student WHERE cgpa >= 8.0 ORDER BY cgpa DESC;' },
      { name: 'GROUP BY & HAVING', sql: 'SELECT dept_id, COUNT(*), AVG(cgpa) FROM student GROUP BY dept_id HAVING AVG(cgpa) > 8;' },
      { name: 'JOINS', sql: 'SELECT s.name, d.dept_name\nFROM student s\nJOIN department d ON s.dept_id = d.dept_id;' },
      { name: 'MINUS (Set Op)', sql: 'SELECT name FROM student WHERE cgpa > 8\nMINUS\nSELECT name FROM student WHERE cgpa = 10;' },
    ],
  },
  {
    label: 'CONSTRAINTS',
    items: [
      { name: 'CASCADE FOREIGN KEY', sql: 'CREATE TABLE student (\n    rollno NUMBER PRIMARY KEY,\n    name VARCHAR2(50),\n    dept_id NUMBER REFERENCES department(dept_id) ON DELETE CASCADE\n);' },
      { name: 'CHECK & DEFAULT', sql: 'CREATE TABLE course (\n    cid NUMBER PRIMARY KEY,\n    credits NUMBER DEFAULT 3 CHECK (credits >= 1 AND credits <= 5)\n);' },
    ],
  },
  {
    label: 'VIEWS',
    items: [
      { name: 'VIEW', sql: 'CREATE VIEW honors_list AS SELECT rollno, name FROM student WHERE cgpa >= 8.5;' },
      { name: 'MATERIALIZED VIEW', sql: 'CREATE MATERIALIZED VIEW student_summary AS\nSELECT dept_id, AVG(cgpa) AS avg_cgpa FROM student GROUP BY dept_id;\n\nREFRESH MATERIALIZED VIEW student_summary;' },
    ],
  },
];

export const ConsoleView: React.FC<ConsoleViewProps> = ({
  sql,
  setSql,
  onExecute,
  onClear,
  onLoadSample,
  isExecuting,
  response,
  error,
}) => {
  return (
    <div className="console-split">
      {/* Category Quick Palette */}
      <div
        style={{
          background: '#0d121f',
          padding: '6px 12px',
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          gap: '12px',
          overflowX: 'auto',
          fontSize: '11px',
          alignItems: 'center',
          flexShrink: 0,
        }}
      >
        <span style={{ color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase' }}>
          Quick Insert:
        </span>
        {CATEGORY_SNIPPETS.map((cat) => (
          <div key={cat.label} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ color: '#38bdf8', fontWeight: 600 }}>{cat.label}:</span>
            {cat.items.map((item) => (
              <button
                key={item.name}
                className="btn btn-secondary"
                style={{ fontSize: '10px', padding: '2px 6px' }}
                onClick={() => setSql(item.sql)}
                title={item.sql}
              >
                {item.name}
              </button>
            ))}
          </div>
        ))}
      </div>

      <SQLEditor
        sql={sql}
        onChange={setSql}
        onExecute={onExecute}
        onClear={onClear}
        onLoadSample={onLoadSample}
        isExecuting={isExecuting}
      />
      <OutputPane response={response} error={error} />
    </div>
  );
};
