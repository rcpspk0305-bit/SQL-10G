import React, { useState } from 'react';
import { GraduationCap, CheckCircle2, Play, BookOpen } from 'lucide-react';
import { LabExercise } from '../types';

const FULL_LAB_EXERCISES: LabExercise[] = [
  {
    id: 1,
    title: 'Lab 1: DDL & Constraints Setup',
    category: 'DDL & Constraints',
    description: 'Create DEPARTMENT and STUDENT tables with Primary Key, Foreign Key with ON DELETE CASCADE, Unique, and Check constraints.',
    instructions: [
      'Create DEPARTMENT table (dept_id NUMBER PRIMARY KEY, dept_name VARCHAR2(50) UNIQUE).',
      'Create STUDENT table with foreign key referencing department with ON DELETE CASCADE.',
      'Add CHECK constraint for CGPA (0 to 10).',
    ],
    initial_sql: `CREATE TABLE department (\n    dept_id NUMBER PRIMARY KEY,\n    dept_name VARCHAR2(50) UNIQUE\n);\n\nCREATE TABLE student (\n    rollno NUMBER PRIMARY KEY,\n    name VARCHAR2(50) NOT NULL,\n    cgpa NUMBER(3,2) CHECK (cgpa >= 0 AND cgpa <= 10),\n    dept_id NUMBER,\n    FOREIGN KEY (dept_id) REFERENCES department(dept_id) ON DELETE CASCADE\n);`,
    solution_hint: 'CREATE TABLE department ...; CREATE TABLE student ...;',
    validation_query: 'SELECT * FROM department;',
  },
  {
    id: 2,
    title: 'Lab 2: DML & Transactions (TCL)',
    category: 'DML & TCL',
    description: 'Insert records into DEPARTMENT and STUDENT, create a SAVEPOINT, perform updates, rollback to savepoint, and commit.',
    instructions: [
      'Insert 2 departments (10, "CSE") and (20, "ECE").',
      'Insert 3 students.',
      'Use SAVEPOINT, UPDATE, ROLLBACK TO, and COMMIT.',
    ],
    initial_sql: `INSERT INTO department VALUES (10, 'CSE');\nINSERT INTO department VALUES (20, 'ECE');\n\nINSERT INTO student VALUES (101, 'Rahul', 8.7, 10);\nINSERT INTO student VALUES (102, 'Priya', 9.1, 10);\nINSERT INTO student VALUES (103, 'Arjun', 7.8, 20);\n\nSAVEPOINT sp1;\nUPDATE student SET cgpa = 9.5 WHERE rollno = 101;\nROLLBACK TO sp1;\nCOMMIT;\n\nSELECT * FROM student;`,
    solution_hint: 'Use SAVEPOINT sp1; ... ROLLBACK TO sp1; COMMIT;',
    validation_query: 'SELECT COUNT(*) FROM student;',
  },
  {
    id: 3,
    title: 'Lab 3: Aggregates, GROUP BY & HAVING',
    category: 'Querying',
    description: 'Calculate total count, average CGPA, highest CGPA, and lowest CGPA grouped by department with HAVING filter.',
    instructions: [
      'GROUP BY dept_id.',
      'Calculate COUNT(*), AVG(cgpa), MAX(cgpa), MIN(cgpa).',
      'Filter departments where AVG(cgpa) > 8 using HAVING.',
    ],
    initial_sql: `SELECT dept_id,\n       COUNT(*) AS total_students,\n       AVG(cgpa) AS average_cgpa,\n       MAX(cgpa) AS highest_cgpa,\n       MIN(cgpa) AS lowest_cgpa\nFROM student\nGROUP BY dept_id\nHAVING AVG(cgpa) > 8\nORDER BY average_cgpa DESC;`,
    solution_hint: 'SELECT dept_id, COUNT(*), AVG(cgpa) ... GROUP BY dept_id HAVING AVG(cgpa) > 8;',
    validation_query: 'SELECT AVG(cgpa) FROM student GROUP BY dept_id;',
  },
  {
    id: 4,
    title: 'Lab 4: Views & Materialized Views',
    category: 'Views',
    description: 'Create a standard VIEW and an emulated MATERIALIZED VIEW with manual snapshot refresh.',
    instructions: [
      'Create VIEW topper_view for students with CGPA >= 8.5.',
      'Create MATERIALIZED VIEW student_summary grouped by department.',
      'Refresh the materialized view.',
    ],
    initial_sql: `CREATE VIEW topper_view AS\nSELECT rollno, name, cgpa\nFROM student\nWHERE cgpa >= 8.5;\n\nSELECT * FROM topper_view;\n\nCREATE MATERIALIZED VIEW student_summary AS\nSELECT dept_id, AVG(cgpa) AS avg_cgpa\nFROM student\nGROUP BY dept_id;\n\nREFRESH MATERIALIZED VIEW student_summary;\nSELECT * FROM student_summary;`,
    solution_hint: 'CREATE VIEW ...; CREATE MATERIALIZED VIEW ...;',
    validation_query: 'SELECT * FROM topper_view;',
  },
  {
    id: 5,
    title: 'Lab 5: Cascade Deletion & DCL Privileges',
    category: 'Cascade & DCL',
    description: 'Verify ON DELETE CASCADE when deleting a department, and test GRANT/REVOKE privileges.',
    instructions: [
      'Delete from DEPARTMENT where dept_id = 10 (auto deletes dependent students).',
      'Grant SELECT on student to student_user.',
      'Revoke SELECT on student from student_user.',
    ],
    initial_sql: `DELETE FROM department WHERE dept_id = 10;\nSELECT * FROM student;\n\nGRANT SELECT ON student TO student_user;\nREVOKE SELECT ON student FROM student_user;`,
    solution_hint: 'DELETE FROM department WHERE dept_id = 10;',
    validation_query: 'SELECT * FROM student;',
  },
  {
    id: 6,
    title: 'Lab 6: Full MVP Acceptance Test',
    category: 'Comprehensive Exam',
    description: 'Execute the complete end-to-end multi-table Oracle 10g database coursework lifecycle.',
    instructions: [
      'Executes DDL, Foreign Keys, CASCADE, DML, TCL, Aggregates, GROUP BY, HAVING, Views, Savepoints, Rollbacks, and DCL in one unified script.',
    ],
    initial_sql: `CREATE TABLE department (\n    dept_id NUMBER PRIMARY KEY,\n    dept_name VARCHAR2(50) UNIQUE\n);\n\nCREATE TABLE student (\n    rollno NUMBER PRIMARY KEY,\n    name VARCHAR2(50) NOT NULL,\n    cgpa NUMBER(3,2),\n    dept_id NUMBER,\n    FOREIGN KEY (dept_id) REFERENCES department(dept_id) ON DELETE CASCADE\n);\n\nINSERT INTO department VALUES (10, 'CSE');\nINSERT INTO department VALUES (20, 'ECE');\n\nINSERT INTO student VALUES (101, 'Rahul', 8.7, 10);\nINSERT INTO student VALUES (102, 'Priya', 9.1, 10);\nINSERT INTO student VALUES (103, 'Arjun', 7.8, 20);\n\nCOMMIT;\n\nSELECT * FROM student ORDER BY cgpa DESC;\n\nSELECT dept_id,\n       COUNT(*) AS total_students,\n       AVG(cgpa) AS average_cgpa,\n       MAX(cgpa) AS highest_cgpa,\n       MIN(cgpa) AS lowest_cgpa\nFROM student\nGROUP BY dept_id\nHAVING AVG(cgpa) > 8\nORDER BY average_cgpa DESC;\n\nCREATE VIEW topper_view AS\nSELECT rollno, name, cgpa\nFROM student\nWHERE cgpa >= 8.5;\n\nSELECT * FROM topper_view;\n\nSAVEPOINT before_delete;\nDELETE FROM department WHERE dept_id = 10;\nROLLBACK TO before_delete;\nCOMMIT;\n\nGRANT SELECT ON student TO student_user;\nREVOKE SELECT ON student FROM student_user;`,
    solution_hint: 'Execute all statements sequentially.',
    validation_query: 'SELECT COUNT(*) FROM student;',
  },
];

interface LabViewProps {
  onLoadExercise: (sql: string) => void;
}

export const LabView: React.FC<LabViewProps> = ({ onLoadExercise }) => {
  const [selectedExercise, setSelectedExercise] = useState<LabExercise>(FULL_LAB_EXERCISES[0]);
  const [mode, setMode] = useState<'practice' | 'exam'>('practice');

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <div className="view-title">
            <GraduationCap size={22} style={{ color: '#38bdf8' }} />
            <span>Oracle 10G Database Laboratory</span>
          </div>
          <div className="view-desc">
            Standard college coursework exercises with live database state verification.
          </div>
        </div>

        <div style={{ display: 'flex', gap: '6px', background: '#0f1422', padding: '4px', borderRadius: '6px', border: '1px solid var(--border)' }}>
          <button
            className={`btn ${mode === 'practice' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '11px' }}
            onClick={() => setMode('practice')}
          >
            Practice Mode
          </button>
          <button
            className={`btn ${mode === 'exam' ? 'btn-danger' : 'btn-secondary'}`}
            style={{ fontSize: '11px' }}
            onClick={() => setMode('exam')}
          >
            Exam Mode (Timed)
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '20px' }}>
        {/* Left Exercise List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {FULL_LAB_EXERCISES.map((ex) => (
            <div
              key={ex.id}
              className="card"
              style={{
                cursor: 'pointer',
                borderLeft: selectedExercise.id === ex.id ? '3px solid #38bdf8' : undefined,
                backgroundColor: selectedExercise.id === ex.id ? '#182035' : undefined,
              }}
              onClick={() => setSelectedExercise(ex)}
            >
              <div style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc', marginBottom: '4px' }}>
                {ex.title}
              </div>
              <span className="badge badge-blue">{ex.category}</span>
            </div>
          ))}
        </div>

        {/* Right Exercise Details */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: '17px', color: '#f8fafc' }}>{selectedExercise.title}</h3>
            <span className="badge badge-emerald">{selectedExercise.category}</span>
          </div>

          <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
            {selectedExercise.description}
          </p>

          <div style={{ background: '#070a10', padding: '12px', borderRadius: '6px', border: '1px solid var(--border)' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <BookOpen size={13} style={{ color: '#38bdf8' }} /> Instructions:
            </div>
            <ul style={{ paddingLeft: '20px', fontSize: '12px', color: 'var(--text-muted)' }}>
              {selectedExercise.instructions.map((inst, i) => (
                <li key={i} style={{ marginBottom: '4px' }}>{inst}</li>
              ))}
            </ul>
          </div>

          <div style={{ display: 'flex', gap: '10px', marginTop: '8px' }}>
            <button
              className="btn btn-primary"
              onClick={() => onLoadExercise(selectedExercise.initial_sql)}
            >
              <Play size={13} fill="currentColor" />
              <span>Load Into SQL Console</span>
            </button>

            {mode === 'practice' && (
              <button
                className="btn btn-secondary"
                onClick={() => alert(`Hint:\n${selectedExercise.solution_hint}`)}
              >
                <CheckCircle2 size={13} />
                <span>Show Hint</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
