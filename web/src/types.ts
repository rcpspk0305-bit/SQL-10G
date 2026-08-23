export type PageId =
  | 'console'
  | 'tables'
  | 'views'
  | 'materialized-views'
  | 'scripts'
  | 'plsql'
  | 'lab'
  | 'history'
  | 'settings'
  | 'about';

export interface StatementResult {
  original_sql: string;
  translated_sql: string;
  command_type: string;
  is_query: boolean;
  is_error: boolean;
  columns: string[];
  column_types: string[];
  rows: (string | number | boolean | null)[][];
  row_count: number;
  feedback_message: string;
  formatted_output: string;
  execution_time_ms: number;
}

export interface ExecuteResponse {
  success: boolean;
  results: StatementResult[];
  total_execution_time_ms: number;
  combined_formatted_output: string;
}

export interface TableColumnInfo {
  name: string;
  oracle_type: string;
  nullable: boolean;
  is_primary_key: boolean;
}

export interface TableInfo {
  table_name: string;
  columns: TableColumnInfo[];
  row_count: number;
}

export interface SchemaTablesResponse {
  tables: TableInfo[];
}

export interface HistoryItem {
  sql: string;
  time: string;
  duration_ms: number;
  success: boolean;
  error?: string;
  rows: number;
}

export interface LabExercise {
  id: number;
  title: string;
  category: string;
  description: string;
  instructions: string[];
  initial_sql: string;
  solution_hint: string;
  validation_query: string;
  expected_columns?: string[];
}
