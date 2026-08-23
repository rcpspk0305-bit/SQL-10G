import React from 'react';
import { Eye, Code } from 'lucide-react';

interface ViewsViewProps {
  onRunQuery: (sql: string) => void;
}

export const ViewsView: React.FC<ViewsViewProps> = ({ onRunQuery }) => {
  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <div className="view-title">
            <Eye size={20} style={{ color: '#38bdf8' }} />
            <span>Views Management</span>
          </div>
          <div className="view-desc">
            Define, inspect, and query Oracle-compatible SQL views.
          </div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '20px' }}>
        <div className="card-title">
          <span>Create Oracle View</span>
          <span className="badge badge-emerald">DDL Support</span>
        </div>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '16px' }}>
          Views present data from one or more underlying tables. Use the sample query below to create a view of top students.
        </p>

        <pre
          style={{
            background: '#070a10',
            padding: '12px',
            borderRadius: '6px',
            fontSize: '12px',
            color: '#38bdf8',
            fontFamily: 'var(--font-mono)',
            marginBottom: '16px',
          }}
        >
{`CREATE VIEW top_students AS
SELECT rollno, name, cgpa
FROM student
WHERE cgpa >= 8.5;`}
        </pre>

        <button
          className="btn btn-primary"
          onClick={() => {
            onRunQuery(
              `CREATE VIEW top_students AS\nSELECT rollno, name, cgpa\nFROM student\nWHERE cgpa >= 8.5;\n\nSELECT * FROM top_students;`
            );
          }}
        >
          <Code size={13} />
          <span>Execute Create View</span>
        </button>
      </div>
    </div>
  );
};
