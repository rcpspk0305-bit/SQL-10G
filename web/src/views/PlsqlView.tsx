import React from 'react';
import { Cpu, Play } from 'lucide-react';

interface PlsqlViewProps {
  onRunQuery: (sql: string) => void;
}

export const PlsqlView: React.FC<PlsqlViewProps> = ({ onRunQuery }) => {
  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <div className="view-title">
            <Cpu size={20} style={{ color: '#10b981' }} />
            <span>PL/SQL Workspace</span>
          </div>
          <div className="view-desc">
            Anonymous blocks, control structures, cursor loops, and DBMS_OUTPUT simulation.
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-title">
          <span>Anonymous Block Example</span>
          <span className="badge badge-emerald">PL/SQL Subset</span>
        </div>
        <pre
          style={{
            background: '#070a10',
            padding: '12px',
            borderRadius: '6px',
            fontSize: '12px',
            color: '#34d399',
            fontFamily: 'var(--font-mono)',
            marginBottom: '16px',
          }}
        >
{`DECLARE
    v_total NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_total FROM student;
    DBMS_OUTPUT.PUT_LINE('Total students registered: ' || v_total);
END;
/`}
        </pre>

        <button
          className="btn btn-primary"
          onClick={() => {
            onRunQuery(
              `-- PL/SQL Anonymous Block\nSELECT 'Total students in database: ' || COUNT(*) AS output FROM student;`
            );
          }}
        >
          <Play size={13} />
          <span>Execute in SQL Console</span>
        </button>
      </div>
    </div>
  );
};
