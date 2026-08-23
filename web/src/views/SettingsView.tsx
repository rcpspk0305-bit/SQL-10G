import React, { useState } from 'react';
import { Settings as SettingsIcon, Save } from 'lucide-react';

export const SettingsView: React.FC = () => {
  const [pagesize, setPagesize] = useState(14);
  const [linesize, setLinesize] = useState(80);
  const [heading, setHeading] = useState(true);
  const [feedback, setFeedback] = useState(true);
  const [nullValue, setNullValue] = useState('');

  return (
    <div className="view-container" style={{ maxWidth: '700px' }}>
      <div className="view-header">
        <div>
          <div className="view-title">
            <SettingsIcon size={20} style={{ color: '#38bdf8' }} />
            <span>SQL*Plus Environment Settings</span>
          </div>
          <div className="view-desc">
            Configure SQL*Plus client session parameters and formatting rules.
          </div>
        </div>
      </div>

      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div>
          <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
            SET PAGESIZE
          </label>
          <input
            type="number"
            value={pagesize}
            onChange={(e) => setPagesize(Number(e.target.value))}
            style={{
              width: '100%',
              background: '#0b0f19',
              border: '1px solid var(--border)',
              borderRadius: '5px',
              padding: '8px 12px',
              color: '#f8fafc',
              fontSize: '13px',
              fontFamily: 'var(--font-mono)',
            }}
          />
          <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
            Number of lines per page before repeating headers (0 to disable pagination).
          </span>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
            SET LINESIZE
          </label>
          <input
            type="number"
            value={linesize}
            onChange={(e) => setLinesize(Number(e.target.value))}
            style={{
              width: '100%',
              background: '#0b0f19',
              border: '1px solid var(--border)',
              borderRadius: '5px',
              padding: '8px 12px',
              color: '#f8fafc',
              fontSize: '13px',
              fontFamily: 'var(--font-mono)',
            }}
          />
          <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
            Maximum characters per line of output before wrapping.
          </span>
        </div>

        <div style={{ display: 'flex', gap: '24px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: '#e2e8f0', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={heading}
              onChange={(e) => setHeading(e.target.checked)}
            />
            <span>SET HEADING ON</span>
          </label>

          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: '#e2e8f0', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={feedback}
              onChange={(e) => setFeedback(e.target.checked)}
            />
            <span>SET FEEDBACK ON</span>
          </label>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#e2e8f0', marginBottom: '6px' }}>
            SET NULL String
          </label>
          <input
            type="text"
            value={nullValue}
            placeholder="(default empty)"
            onChange={(e) => setNullValue(e.target.value)}
            style={{
              width: '100%',
              background: '#0b0f19',
              border: '1px solid var(--border)',
              borderRadius: '5px',
              padding: '8px 12px',
              color: '#f8fafc',
              fontSize: '13px',
              fontFamily: 'var(--font-mono)',
            }}
          />
        </div>

        <button
          className="btn btn-primary"
          style={{ marginTop: '8px', alignSelf: 'flex-start' }}
          onClick={() => alert('Settings updated for active session.')}
        >
          <Save size={13} />
          <span>Save Settings</span>
        </button>
      </div>
    </div>
  );
};
