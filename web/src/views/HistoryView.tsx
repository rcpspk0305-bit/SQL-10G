import React, { useEffect, useState } from 'react';
import { History, Play, Clock, CheckCircle2, AlertCircle } from 'lucide-react';
import { HistoryItem } from '../types';
import { fetchHistory } from '../api';

interface HistoryViewProps {
  onRunQuery: (sql: string) => void;
}

export const HistoryView: React.FC<HistoryViewProps> = ({ onRunQuery }) => {
  const [history, setHistory] = useState<HistoryItem[]>([]);

  useEffect(() => {
    fetchHistory().then(setHistory).catch(console.error);
  }, []);

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <div className="view-title">
            <History size={20} style={{ color: '#38bdf8' }} />
            <span>Query History</span>
          </div>
          <div className="view-desc">
            Audit log of executed SQL statements, timing, and row counts.
          </div>
        </div>
      </div>

      {history.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-dim)' }}>
          No queries executed in this session yet.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {history.map((item, idx) => (
            <div key={idx} className="card" style={{ padding: '12px 16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px' }}>
                  <span
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      color: item.success ? '#34d399' : '#fb7185',
                      fontWeight: 600,
                    }}
                  >
                    {item.success ? <CheckCircle2 size={12} /> : <AlertCircle size={12} />}
                    {item.success ? 'Success' : 'Error'}
                  </span>
                  <span style={{ color: 'var(--text-dim)' }}>•</span>
                  <span style={{ color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '3px' }}>
                    <Clock size={11} /> {item.duration_ms} ms
                  </span>
                  <span style={{ color: 'var(--text-dim)' }}>•</span>
                  <span style={{ color: 'var(--text-dim)' }}>{item.time}</span>
                </div>

                <button
                  className="btn btn-secondary"
                  style={{ fontSize: '11px', padding: '3px 8px' }}
                  onClick={() => onRunQuery(item.sql)}
                >
                  <Play size={10} /> Re-run
                </button>
              </div>

              <pre
                style={{
                  background: '#070a10',
                  padding: '8px 12px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  color: item.success ? '#38bdf8' : '#fb7185',
                  fontFamily: 'var(--font-mono)',
                  overflowX: 'auto',
                }}
              >
                {item.sql}
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
