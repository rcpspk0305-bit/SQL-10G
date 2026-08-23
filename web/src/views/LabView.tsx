import React, { useState } from 'react';
import { GraduationCap, CheckCircle2, Play, BookOpen } from 'lucide-react';
import { LabExercise } from '../types';

const LAB_EXERCISES: LabExercise[] = [
  {
    id: 1,
    title: 'Lab 1: Create Student Table & Constraints',
    category: 'DDL & Constraints',
    description: 'Create a STUDENT table with ROLLNO as primary key, NAME as VARCHAR2(50), and CGPA as NUMBER(3,2).',
    instructions: [
      'Define ROLLNO as NUMBER with PRIMARY KEY constraint.',
      'Define NAME as VARCHAR2(50) NOT NULL.',
      'Define CGPA as NUMBER(3,2).',
    ],
    initial_sql: `CREATE TABLE student (\n    rollno NUMBER PRIMARY KEY,\n    name VARCHAR2(50) NOT NULL,\n    cgpa NUMBER(3,2)\n);`,
    solution_hint: `Use CREATE TABLE student (rollno NUMBER PRIMARY KEY, name VARCHAR2(50) NOT NULL, cgpa NUMBER(3,2));`,
    validation_query: `SELECT * FROM student;`,
  },
  {
    id: 2,
    title: 'Lab 2: DML Insert Records',
    category: 'DML Operations',
    description: 'Insert three student records into the STUDENT table.',
    instructions: [
      'Insert (101, "Rahul", 8.70)',
      'Insert (102, "Priya", 9.10)',
      'Insert (103, "Amit", 7.80)',
    ],
    initial_sql: `INSERT INTO student VALUES (101, 'Rahul', 8.7);\nINSERT INTO student VALUES (102, 'Priya', 9.1);\nINSERT INTO student VALUES (103, 'Amit', 7.8);\nSELECT * FROM student;`,
    solution_hint: `Use INSERT INTO student VALUES (...);`,
    validation_query: `SELECT COUNT(*) FROM student;`,
  },
  {
    id: 3,
    title: 'Lab 3: Aggregate Functions & NVL',
    category: 'SQL Functions',
    description: 'Compute the average CGPA, highest CGPA, and total count of students.',
    instructions: [
      'Query AVG(cgpa), MAX(cgpa), and COUNT(*).',
    ],
    initial_sql: `SELECT COUNT(*) AS total_students, ROUND(AVG(cgpa), 2) AS avg_cgpa, MAX(cgpa) AS highest_cgpa FROM student;`,
    solution_hint: `SELECT COUNT(*), AVG(cgpa), MAX(cgpa) FROM student;`,
    validation_query: `SELECT AVG(cgpa) FROM student;`,
  },
  {
    id: 4,
    title: 'Lab 4: Create View for Distinction Students',
    category: 'Views',
    description: 'Create a VIEW named HONORS_STUDENTS for students with CGPA >= 8.5.',
    instructions: [
      'Use CREATE VIEW honors_students AS SELECT ... WHERE cgpa >= 8.5;',
    ],
    initial_sql: `CREATE VIEW honors_students AS\nSELECT rollno, name, cgpa\nFROM student\nWHERE cgpa >= 8.5;\n\nSELECT * FROM honors_students;`,
    solution_hint: `CREATE VIEW honors_students AS SELECT * FROM student WHERE cgpa >= 8.5;`,
    validation_query: `SELECT * FROM honors_students;`,
  },
];

interface LabViewProps {
  onLoadExercise: (sql: string) => void;
}

export const LabView: React.FC<LabViewProps> = ({ onLoadExercise }) => {
  const [selectedExercise, setSelectedExercise] = useState<LabExercise>(LAB_EXERCISES[0]);
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

      <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: '20px' }}>
        {/* Left Exercise List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {LAB_EXERCISES.map((ex) => (
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
