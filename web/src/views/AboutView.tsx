import React from 'react';
import { Info, ShieldCheck, Database, Code, CheckCircle2 } from 'lucide-react';

export const AboutView: React.FC = () => {
  return (
    <div className="view-container" style={{ maxWidth: '800px' }}>
      <div className="view-header">
        <div>
          <div className="view-title">
            <Info size={20} style={{ color: '#38bdf8' }} />
            <span>About OraCLI 10G Web</span>
          </div>
          <div className="view-desc">
            Oracle 10g SQL*Plus Educational Environment.
          </div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '16px' }}>
        <div className="card-title">
          <span>Vision & Purpose</span>
          <span className="badge badge-emerald">Educational</span>
        </div>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: '1.7' }}>
          OraCLI 10G Web is an independent, lightweight, browser-based database environment created specifically for university database laboratory practice, coursework, and SQL skill mastery. It reproduces the important user experience, commands, and formatting of Oracle SQL*Plus 10g using modern web technologies and a local SQLite engine.
        </p>
      </div>

      <div className="card" style={{ marginBottom: '16px' }}>
        <div className="card-title">
          <span>Architecture & Stack</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '12px', marginTop: '10px' }}>
          <div style={{ background: '#0b0f19', padding: '10px', borderRadius: '5px', border: '1px solid var(--border)' }}>
            <div style={{ fontWeight: 600, color: '#38bdf8', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Code size={13} /> Frontend
            </div>
            <div style={{ color: 'var(--text-muted)' }}>React 18, TypeScript, Vite, Lucide Icons</div>
          </div>
          <div style={{ background: '#0b0f19', padding: '10px', borderRadius: '5px', border: '1px solid var(--border)' }}>
            <div style={{ fontWeight: 600, color: '#f59e0b', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Database size={13} /> Backend & Engine
            </div>
            <div style={{ color: 'var(--text-muted)' }}>Python 3.12+, FastAPI, SQLGlot, SQLite3</div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-title">
          <span>Core Capabilities</span>
        </div>
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '13px', color: 'var(--text-muted)', marginTop: '8px' }}>
          <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircle2 size={14} style={{ color: '#10b981' }} />
            <span>True Oracle SQL*Plus multiline execution with numbered continuation prompts</span>
          </li>
          <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircle2 size={14} style={{ color: '#10b981' }} />
            <span>Oracle types: NUMBER, NUMBER(p,s), VARCHAR2(n), CHAR(n), DATE, TIMESTAMP, CLOB, BLOB</span>
          </li>
          <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircle2 size={14} style={{ color: '#10b981' }} />
            <span>Oracle scalar functions: NVL, SYSDATE, UPPER, LOWER, SUBSTR, INSTR, ROUND, TRUNC</span>
          </li>
          <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircle2 size={14} style={{ color: '#10b981' }} />
            <span>Canonical ORA-xxxxx error codes for table missing, invalid identifiers, constraints</span>
          </li>
          <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldCheck size={14} style={{ color: '#38bdf8' }} />
            <span>Independent clean-room educational implementation</span>
          </li>
        </ul>
      </div>
    </div>
  );
};
