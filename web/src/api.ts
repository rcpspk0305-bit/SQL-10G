import { ExecuteResponse, SchemaTablesResponse, HistoryItem } from './types';

const API_BASE = '';

export async function executeSQL(sql: string, sessionUser: string = 'SYSTEM'): Promise<ExecuteResponse> {
  const res = await fetch(`${API_BASE}/api/sql/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sql, session_user: sessionUser }),
  });
  if (!res.ok) {
    throw new Error(`Execution failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchSchemaTables(): Promise<SchemaTablesResponse> {
  const res = await fetch(`${API_BASE}/api/schema/tables`);
  if (!res.ok) {
    throw new Error(`Failed to load tables: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchHistory(): Promise<HistoryItem[]> {
  const res = await fetch(`${API_BASE}/api/history`);
  if (!res.ok) {
    throw new Error(`Failed to load history: ${res.statusText}`);
  }
  return res.json();
}

export async function resetDatabase(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE}/api/database/reset`, { method: 'POST' });
  if (!res.ok) {
    throw new Error(`Failed to reset database: ${res.statusText}`);
  }
  return res.json();
}

export async function checkHealth(): Promise<{ status: string; app_name: string; version: string; database: string }> {
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) {
    throw new Error(`Failed to reach health endpoint: ${res.statusText}`);
  }
  return res.json();
}
