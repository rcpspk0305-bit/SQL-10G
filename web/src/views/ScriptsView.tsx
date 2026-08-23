import React from 'react';
import { FileCode, Play, Download } from 'lucide-react';

interface ScriptsViewProps {
  onLoadScript: (sql: string) => void;
}

const PRESET_SCRIPTS = [
  {
    name: 'student_schema.sql',
    desc: 'Creates student table, inserts 3 records, and selects all rows.',
    sql: `CREATE TABLE student (\n    rollno NUMBER PRIMARY KEY,\n    name VARCHAR2(50),\n    cgpa NUMBER(3,2)\n);\n\nINSERT INTO student VALUES (101, 'Rahul', 8.7);\nINSERT INTO student VALUES (102, 'Priya', 9.1);\nINSERT INTO student VALUES (103, 'Amit', 7.8);\n\nSELECT * FROM student;`,
  },
  {
    name: 'employee_dept.sql',
    desc: 'Creates EMP and DEPT tables with Foreign Key relationships and Joins.',
    sql: `CREATE TABLE dept (\n    deptno NUMBER PRIMARY KEY,\n    dname VARCHAR2(30),\n    loc VARCHAR2(30)\n);\n\nCREATE TABLE emp (\n    empno NUMBER PRIMARY KEY,\n    ename VARCHAR2(50),\n    job VARCHAR2(30),\n    sal NUMBER(7,2),\n    deptno NUMBER REFERENCES dept(deptno)\n);\n\nINSERT INTO dept VALUES (10, 'ACCOUNTING', 'NEW YORK');\nINSERT INTO dept VALUES (20, 'RESEARCH', 'DALLAS');\n\nINSERT INTO emp VALUES (7369, 'SMITH', 'CLERK', 800, 20);\nINSERT INTO emp VALUES (7839, 'KING', 'PRESIDENT', 5000, 10);\n\nSELECT e.ename, e.job, d.dname, d.loc\nFROM emp e\nJOIN dept d ON e.deptno = d.deptno;`,
  },
];

export const ScriptsView: React.FC<ScriptsViewProps> = ({ onLoadScript }) => {
  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <div className="view-title">
            <FileCode size={20} style={{ color: '#38bdf8' }} />
            <span>SQL Scripts Library</span>
          </div>
          <div className="view-desc">
            Standard educational laboratory scripts and sample schemas.
          </div>
        </div>
      </div>

      <div className="card-grid">
        {PRESET_SCRIPTS.map((script) => (
          <div key={script.name} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div className="card-title">
              <span style={{ fontFamily: 'var(--font-mono)' }}>{script.name}</span>
              <span className="badge badge-blue">SQL Script</span>
            </div>

            <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              {script.desc}
            </p>

            <pre
              style={{
                background: '#070a10',
                padding: '8px 12px',
                borderRadius: '4px',
                fontSize: '11px',
                color: '#cbd5e1',
                fontFamily: 'var(--font-mono)',
                maxHeight: '120px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
            >
              {script.sql}
            </pre>

            <div style={{ display: 'flex', gap: '8px', marginTop: 'auto' }}>
              <button
                className="btn btn-primary"
                style={{ flex: 1, fontSize: '11px' }}
                onClick={() => onLoadScript(script.sql)}
              >
                <Play size={11} /> Load & Run
              </button>
              <button
                className="btn btn-secondary"
                style={{ fontSize: '11px' }}
                onClick={() => {
                  const blob = new Blob([script.sql], { type: 'text/sql' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = script.name;
                  a.click();
                }}
              >
                <Download size={11} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
