import React from 'react';
import { Database, RotateCcw, User } from 'lucide-react';

interface HeaderProps {
  onResetDB: () => void;
  isResetting: boolean;
}

export const Header: React.FC<HeaderProps> = ({ onResetDB, isResetting }) => {
  return (
    <header className="top-header">
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div className="status-pill">
          <span className="status-dot" />
          <span>ORACLE 10G CONNECTED</span>
        </div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '12px',
            color: 'var(--text-muted)',
            fontFamily: 'var(--font-mono)',
          }}
        >
          <User size={13} style={{ color: '#38bdf8' }} />
          <span>SYSTEM</span>
          <span style={{ color: '#475569' }}>@</span>
          <Database size={13} style={{ color: '#f59e0b' }} />
          <span>LOCAL_EDU</span>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <button
          className="btn btn-danger"
          onClick={onResetDB}
          disabled={isResetting}
          title="Reset database to empty state"
        >
          <RotateCcw size={13} />
          <span>{isResetting ? 'Resetting...' : 'Reset Database'}</span>
        </button>
      </div>
    </header>
  );
};
