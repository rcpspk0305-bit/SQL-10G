import React from 'react';
import { Info, ShieldCheck, Database, Code, CheckCircle2, Award } from 'lucide-react';

const COMPATIBILITY_MATRIX = [
  { feature: 'DDL (CREATE, ALTER, DROP, TRUNCATE, RENAME, INDEX, VIEW)', status: 'SUPPORTED', color: '#10b981' },
  { feature: 'DML (INSERT, UPDATE, DELETE, SELECT with row feedback)', status: 'SUPPORTED', color: '#10b981' },
  { feature: 'DCL (GRANT, REVOKE, user authorization, ORA-01031)', status: 'SUPPORTED', color: '#10b981' },
  { feature: 'TCL (COMMIT, ROLLBACK, SAVEPOINT, ROLLBACK TO SAVEPOINT)', status: 'SUPPORTED', color: '#10b981' },
  { feature: 'SELECT (WHERE, DISTINCT, ALIASES, SUBQUERIES)', status: 'SUPPORTED', color: '#10b981' },
  { feature: 'WHERE & CONDITIONAL FILTERING', status: 'SUPPORTED', color: '#10b981' },
  { feature: 'ORDER BY (ASC, DESC, MULTIPLE COLUMNS, ALIASES)', status: 'SUPPORTED', color: '#10b981' },
  { feature: 'GROUP BY (SINGLE & MULTIPLE COLUMNS)', status: 'SUPPORTED', color: '#10b981' },
  { feature: 'HAVING (POST-AGGREGATION FILTERING)', status: 'SUPPORTED', color: '#10b981' },
  { feature: 'AGGREGATE FUNCTIONS (COUNT, SUM, AVG, MIN, MAX)', status: 'SUPPORTED', color: '#10b981' },
  { feature: 'CONSTRAINTS (PRIMARY KEY, FOREIGN KEY, UNIQUE, NOT NULL, CHECK, DEFAULT)', status: 'SUPPORTED', color: '#10b981' },
  { feature: 'CASCADE (ON DELETE CASCADE FOREIGN KEYS)', status: 'SUPPORTED', color: '#10b981' },
  { feature: 'VIEWS (CREATE VIEW, QUERY VIEW, DROP VIEW)', status: 'SUPPORTED', color: '#10b981' },
  { feature: 'MATERIALIZED VIEWS (SNAPSHOT REFRESH & EMULATION)', status: 'EMULATED', color: '#f59e0b' },
  { feature: 'PL/SQL (ANONYMOUS BLOCKS, DBMS_OUTPUT, CONTROL STRUCTURES)', status: 'PARTIAL', color: '#38bdf8' },
];

export const AboutView: React.FC = () => {
  return (
    <div className="view-container" style={{ maxWidth: '900px' }}>
      <div className="view-header">
        <div>
          <div className="view-title">
            <Info size={20} style={{ color: '#38bdf8' }} />
            <span>OraCLI 10G Compatibility Matrix & About</span>
          </div>
          <div className="view-desc">
            Oracle 10g SQL*Plus Educational Environment Capability Verification.
          </div>
        </div>
      </div>

      {/* Feature Compatibility Status Table */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <div className="card-title">
          <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Award size={16} style={{ color: '#38bdf8' }} />
            Feature Status System
          </span>
          <span className="badge badge-emerald">Automated Tests Verified</span>
        </div>
        <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '14px' }}>
          Every feature labeled <strong>SUPPORTED</strong> is continuously validated by unit and integration tests.
        </p>

        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>FEATURE</th>
                <th style={{ width: '160px' }}>STATUS</th>
              </tr>
            </thead>
            <tbody>
              {COMPATIBILITY_MATRIX.map((item) => (
                <tr key={item.feature}>
                  <td style={{ fontWeight: 500 }}>{item.feature}</td>
                  <td>
                    <span
                      style={{
                        display: 'inline-block',
                        padding: '2px 8px',
                        borderRadius: '4px',
                        fontSize: '11px',
                        fontWeight: 700,
                        backgroundColor: `${item.color}22`,
                        color: item.color,
                        border: `1px solid ${item.color}44`,
                      }}
                    >
                      {item.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
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
          <span>Core Standards</span>
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

      <div className="card" style={{ marginTop: '16px', textAlign: 'center', padding: '16px' }}>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: 0 }}>
          Maintained by{' '}
          <a
            href="https://github.com/rcpspk0305-bit/SQL-10G.git"
            target="_blank"
            rel="noreferrer"
            style={{ color: '#38bdf8', textDecoration: 'none', fontWeight: 600 }}
          >
            Charan Rajanala
          </a>
          {' '}—{' '}
          <a
            href="https://github.com/rcpspk0305-bit/SQL-10G.git"
            target="_blank"
            rel="noreferrer"
            style={{ color: 'var(--text-muted)', textDecoration: 'underline' }}
          >
            GitHub Repository
          </a>
        </p>
      </div>
    </div>
  );
};
