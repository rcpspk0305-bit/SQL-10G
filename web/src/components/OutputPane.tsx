import React, { useState } from 'react';
import { Terminal as TermIcon, Table as TableIcon, Clock, CheckCircle2, AlertCircle } from 'lucide-react';
import { ExecuteResponse } from '../types';

interface OutputPaneProps {
  response: ExecuteResponse | null;
  error: string | null;
}

export const OutputPane: React.FC<OutputPaneProps> = ({ response, error }) => {
  const [activeTab, setActiveTab] = useState<'sqlplus' | 'grid'>('sqlplus');

  // Find first query result for grid view if available
  const queryResult = response?.results.find((r) => r.is_query && r.columns.length > 0);

  return (
    <div className="output-section">
      <div className="output-tabs">
        <div
          className={`output-tab ${activeTab === 'sqlplus' ? 'active' : ''}`}
          onClick={() => setActiveTab('sqlplus')}
        >
          <TermIcon size={14} />
          <span>SQL*Plus Terminal Output</span>
        </div>

        {queryResult && (
          <div
            className={`output-tab ${activeTab === 'grid' ? 'active' : ''}`}
            onClick={() => setActiveTab('grid')}
          >
            <TableIcon size={14} />
            <span>Grid View ({queryResult.row_count} rows)</span>
          </div>
        )}

        {response && (
          <div
            style={{
              marginLeft: 'auto',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              fontSize: '11px',
              color: 'var(--text-dim)',
            }}
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Clock size={12} />
              {response.total_execution_time_ms} ms
            </span>
            <span
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                color: response.success ? '#34d399' : '#fb7185',
                fontWeight: 600,
              }}
            >
              {response.success ? <CheckCircle2 size={12} /> : <AlertCircle size={12} />}
              {response.success ? 'Success' : 'Error'}
            </span>
          </div>
        )}
      </div>

      <div className="output-content">
        {error && (
          <div style={{ color: '#fb7185', whiteSpace: 'pre-wrap' }}>
            {error}
          </div>
        )}

        {!error && !response && (
          <div style={{ color: 'var(--text-dim)', fontStyle: 'italic' }}>
            Ready. Write your SQL statement above and press Run (or Ctrl+Enter).
          </div>
        )}

        {!error && response && activeTab === 'sqlplus' && (
          <div className="sqlplus-terminal">
            {response.combined_formatted_output || 'Statement processed.'}
          </div>
        )}

        {!error && response && activeTab === 'grid' && queryResult && (
          <div className="data-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  {queryResult.columns.map((col, idx) => (
                    <th key={idx}>{col.toUpperCase()}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {queryResult.rows.map((row, rIdx) => (
                  <tr key={rIdx}>
                    {row.map((cell, cIdx) => (
                      <td key={cIdx}>
                        {cell === null ? (
                          <span style={{ color: '#64748b', fontStyle: 'italic' }}>NULL</span>
                        ) : (
                          String(cell)
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
