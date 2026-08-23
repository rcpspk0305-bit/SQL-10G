import React from 'react';
import { Table2, Key, Play, RefreshCw } from 'lucide-react';
import { TableInfo } from '../types';

interface TablesViewProps {
  tables: TableInfo[];
  onRefresh: () => void;
  onRunQuery: (sql: string) => void;
}

export const TablesView: React.FC<TablesViewProps> = ({
  tables,
  onRefresh,
  onRunQuery,
}) => {
  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <div className="view-title">
            <Table2 size={20} style={{ color: '#38bdf8' }} />
            <span>Database Tables</span>
          </div>
          <div className="view-desc">
            Explore schema, columns, datatypes, and constraints for user tables.
          </div>
        </div>

        <button className="btn btn-secondary" onClick={onRefresh}>
          <RefreshCw size={13} />
          <span>Refresh</span>
        </button>
      </div>

      {tables.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <div style={{ color: 'var(--text-dim)', marginBottom: '12px' }}>
            No user tables exist in the database.
          </div>
          <button
            className="btn btn-primary"
            onClick={() => {
              onRunQuery(
                `CREATE TABLE student (\n    rollno NUMBER,\n    name VARCHAR2(50),\n    cgpa NUMBER(3,2)\n);\n\nINSERT INTO student VALUES (101, 'Rahul', 8.7);\nSELECT * FROM student;`
              );
            }}
          >
            Create Sample Student Table
          </button>
        </div>
      ) : (
        <div className="card-grid">
          {tables.map((table) => (
            <div key={table.table_name} className="card">
              <div className="card-title">
                <span>{table.table_name.toUpperCase()}</span>
                <span className="badge badge-blue">{table.row_count} rows</span>
              </div>

              <div style={{ margin: '12px 0' }}>
                <table className="data-table" style={{ fontSize: '11px' }}>
                  <thead>
                    <tr>
                      <th>COLUMN</th>
                      <th>TYPE</th>
                      <th>KEY</th>
                    </tr>
                  </thead>
                  <tbody>
                    {table.columns.map((col) => (
                      <tr key={col.name}>
                        <td>{col.name.toUpperCase()}</td>
                        <td style={{ color: '#38bdf8' }}>{col.oracle_type}</td>
                        <td>
                          {col.is_primary_key && (
                            <span style={{ color: '#fbbf24', display: 'flex', alignItems: 'center', gap: '2px' }}>
                              <Key size={10} /> PK
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
                <button
                  className="btn btn-secondary"
                  style={{ flex: 1, fontSize: '11px' }}
                  onClick={() => onRunQuery(`SELECT * FROM ${table.table_name};`)}
                >
                  <Play size={11} /> SELECT *
                </button>
                <button
                  className="btn btn-secondary"
                  style={{ flex: 1, fontSize: '11px' }}
                  onClick={() => onRunQuery(`DESC ${table.table_name}`)}
                >
                  DESC
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
