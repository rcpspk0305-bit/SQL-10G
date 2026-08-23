import React from 'react';
import { Play, Trash2, Sparkles, Code2 } from 'lucide-react';

interface SQLEditorProps {
  sql: string;
  onChange: (val: string) => void;
  onExecute: () => void;
  onClear: () => void;
  onLoadSample: () => void;
  isExecuting: boolean;
}

export const SQLEditor: React.FC<SQLEditorProps> = ({
  sql,
  onChange,
  onExecute,
  onClear,
  onLoadSample,
  isExecuting,
}) => {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Ctrl + Enter or Cmd + Enter to execute
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      onExecute();
    }
  };

  return (
    <div className="editor-section">
      <div className="editor-toolbar">
        <div className="editor-toolbar-left">
          <button
            className="btn btn-primary"
            onClick={onExecute}
            disabled={isExecuting || !sql.trim()}
          >
            <Play size={13} fill="currentColor" />
            <span>{isExecuting ? 'Executing...' : 'Run (Ctrl+Enter)'}</span>
          </button>

          <button className="btn btn-secondary" onClick={onClear} title="Clear Editor">
            <Trash2 size={13} />
            <span>Clear</span>
          </button>

          <button className="btn btn-secondary" onClick={onLoadSample} title="Load Student Sample Script">
            <Code2 size={13} />
            <span>Sample Script</span>
          </button>
        </div>

        <div className="editor-toolbar-right">
          <Sparkles size={12} style={{ color: '#38bdf8' }} />
          <span>Oracle 10g Dialect</span>
        </div>
      </div>

      <textarea
        className="code-textarea"
        value={sql}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={`-- Enter Oracle SQL statement or SQL*Plus script here:\nCREATE TABLE student (\n    rollno NUMBER,\n    name VARCHAR2(50),\n    cgpa NUMBER(3,2)\n);\n\nINSERT INTO student VALUES (101, 'Rahul', 8.7);\nSELECT * FROM student;`}
        spellCheck={false}
        autoFocus
      />
    </div>
  );
};
