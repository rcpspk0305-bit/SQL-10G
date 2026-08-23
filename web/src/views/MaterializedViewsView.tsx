import React from 'react';
import { Layers, RefreshCw } from 'lucide-react';

interface MaterializedViewsViewProps {
  onRunQuery: (sql: string) => void;
}

export const MaterializedViewsView: React.FC<MaterializedViewsViewProps> = ({ onRunQuery }) => {
  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <div className="view-title">
            <Layers size={20} style={{ color: '#f59e0b' }} />
            <span>Materialized Views</span>
          </div>
          <div className="view-desc">
            Independent snapshot table emulation layer with manual and automatic refresh support.
          </div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '20px' }}>
        <div className="card-title">
          <span>Create Materialized View Emulation</span>
          <span className="badge badge-amber">Emulated Layer</span>
        </div>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '16px' }}>
          Materialized views store the query snapshot physically for fast reporting.
        </p>

        <pre
          style={{
            background: '#070a10',
            padding: '12px',
            borderRadius: '6px',
            fontSize: '12px',
            color: '#fbbf24',
            fontFamily: 'var(--font-mono)',
            marginBottom: '16px',
          }}
        >
{`CREATE TABLE student_mv AS
SELECT rollno, name, cgpa
FROM student;`}
        </pre>

        <button
          className="btn btn-secondary"
          onClick={() => {
            onRunQuery(
              `CREATE TABLE student_mv AS\nSELECT rollno, name, cgpa\nFROM student;\n\nSELECT * FROM student_mv;`
            );
          }}
        >
          <RefreshCw size={13} />
          <span>Generate Snapshot</span>
        </button>
      </div>
    </div>
  );
};
