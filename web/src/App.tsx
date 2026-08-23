import React, { useEffect, useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { ConsoleView } from './views/ConsoleView';
import { TablesView } from './views/TablesView';
import { ViewsView } from './views/ViewsView';
import { MaterializedViewsView } from './views/MaterializedViewsView';
import { ScriptsView } from './views/ScriptsView';
import { PlsqlView } from './views/PlsqlView';
import { LabView } from './views/LabView';
import { HistoryView } from './views/HistoryView';
import { SettingsView } from './views/SettingsView';
import { AboutView } from './views/AboutView';
import { PageId, ExecuteResponse, TableInfo } from './types';
import { executeSQL, fetchSchemaTables, resetDatabase } from './api';

const DEFAULT_SQL = `-- Student table sample script
CREATE TABLE student (
    rollno NUMBER,
    name VARCHAR2(50),
    cgpa NUMBER(3,2)
);

INSERT INTO student VALUES (101, 'Rahul', 8.7);
INSERT INTO student VALUES (102, 'Priya', 9.1);

SELECT * FROM student;`;

export const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<PageId>('console');
  const [sql, setSql] = useState<string>(DEFAULT_SQL);
  const [response, setResponse] = useState<ExecuteResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [tables, setTables] = useState<TableInfo[]>([]);
  const [isResetting, setIsResetting] = useState<boolean>(false);

  const loadTables = async () => {
    try {
      const data = await fetchSchemaTables();
      setTables(data.tables);
    } catch (err) {
      console.error('Failed to load schema tables:', err);
    }
  };

  useEffect(() => {
    loadTables();
  }, []);

  const handleExecute = async () => {
    if (!sql.trim()) return;
    setIsExecuting(true);
    setError(null);
    try {
      const res = await executeSQL(sql);
      setResponse(res);
      await loadTables();
    } catch (err: any) {
      setError(err.message || 'Execution error');
    } finally {
      setIsExecuting(false);
    }
  };

  const handleClear = () => {
    setSql('');
    setResponse(null);
    setError(null);
  };

  const handleLoadSample = () => {
    setSql(DEFAULT_SQL);
  };

  const handleRunQueryFromOtherViews = (querySql: string) => {
    setSql(querySql);
    setCurrentPage('console');
  };

  const handleResetDB = async () => {
    if (!window.confirm('Are you sure you want to reset the database? All tables will be dropped.')) {
      return;
    }
    setIsResetting(true);
    try {
      await resetDatabase();
      setResponse(null);
      setError(null);
      await loadTables();
    } catch (err: any) {
      alert('Reset failed: ' + err.message);
    } finally {
      setIsResetting(false);
    }
  };

  return (
    <div className="app-container">
      <Sidebar
        currentPage={currentPage}
        onSelectPage={setCurrentPage}
        tableCount={tables.length}
      />

      <div className="main-wrapper">
        <Header onResetDB={handleResetDB} isResetting={isResetting} />

        <div className="content-pane">
          {currentPage === 'console' && (
            <ConsoleView
              sql={sql}
              setSql={setSql}
              onExecute={handleExecute}
              onClear={handleClear}
              onLoadSample={handleLoadSample}
              isExecuting={isExecuting}
              response={response}
              error={error}
            />
          )}

          {currentPage === 'tables' && (
            <TablesView
              tables={tables}
              onRefresh={loadTables}
              onRunQuery={handleRunQueryFromOtherViews}
            />
          )}

          {currentPage === 'views' && (
            <ViewsView onRunQuery={handleRunQueryFromOtherViews} />
          )}

          {currentPage === 'materialized-views' && (
            <MaterializedViewsView onRunQuery={handleRunQueryFromOtherViews} />
          )}

          {currentPage === 'scripts' && (
            <ScriptsView onLoadScript={handleRunQueryFromOtherViews} />
          )}

          {currentPage === 'plsql' && (
            <PlsqlView onRunQuery={handleRunQueryFromOtherViews} />
          )}

          {currentPage === 'lab' && (
            <LabView onLoadExercise={handleRunQueryFromOtherViews} />
          )}

          {currentPage === 'history' && (
            <HistoryView onRunQuery={handleRunQueryFromOtherViews} />
          )}

          {currentPage === 'settings' && <SettingsView />}

          {currentPage === 'about' && <AboutView />}
        </div>
      </div>
    </div>
  );
};
