import React from 'react';
import { SQLEditor } from '../components/SQLEditor';
import { OutputPane } from '../components/OutputPane';
import { ExecuteResponse } from '../types';

interface ConsoleViewProps {
  sql: string;
  setSql: (val: string) => void;
  onExecute: () => void;
  onClear: () => void;
  onLoadSample: () => void;
  isExecuting: boolean;
  response: ExecuteResponse | null;
  error: string | null;
}

export const ConsoleView: React.FC<ConsoleViewProps> = ({
  sql,
  setSql,
  onExecute,
  onClear,
  onLoadSample,
  isExecuting,
  response,
  error,
}) => {
  return (
    <div className="console-split">
      <SQLEditor
        sql={sql}
        onChange={setSql}
        onExecute={onExecute}
        onClear={onClear}
        onLoadSample={onLoadSample}
        isExecuting={isExecuting}
      />
      <OutputPane response={response} error={error} />
    </div>
  );
};
