import React from 'react';
import {
  Terminal,
  Table2,
  Eye,
  Layers,
  FileCode,
  Cpu,
  GraduationCap,
  History,
  Settings,
  Info,
} from 'lucide-react';
import { PageId } from '../types';

interface SidebarProps {
  currentPage: PageId;
  onSelectPage: (page: PageId) => void;
  tableCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentPage,
  onSelectPage,
  tableCount,
}) => {
  const navItems: { id: PageId; label: string; icon: React.ReactNode; badge?: string | number }[] = [
    { id: 'console', label: 'SQL Console', icon: <Terminal size={16} /> },
    { id: 'tables', label: 'Tables', icon: <Table2 size={16} />, badge: tableCount },
    { id: 'views', label: 'Views', icon: <Eye size={16} /> },
    { id: 'materialized-views', label: 'Mat. Views', icon: <Layers size={16} /> },
    { id: 'scripts', label: 'SQL Scripts', icon: <FileCode size={16} /> },
    { id: 'plsql', label: 'PL/SQL', icon: <Cpu size={16} /> },
    { id: 'lab', label: 'Lab Exercises', icon: <GraduationCap size={16} />, badge: 'Lab' },
    { id: 'history', label: 'History', icon: <History size={16} /> },
    { id: 'settings', label: 'Settings', icon: <Settings size={16} /> },
    { id: 'about', label: 'About', icon: <Info size={16} /> },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <span className="logo-badge">10g</span>
        <div className="sidebar-title">
          <span>OraCLI Web</span>
          <span className="sidebar-subtitle">Educational Edition</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const isActive = currentPage === item.id;
          return (
            <div
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => onSelectPage(item.id)}
            >
              {item.icon}
              <span style={{ flex: 1 }}>{item.label}</span>
              {item.badge !== undefined && (
                <span
                  style={{
                    fontSize: '10px',
                    padding: '1px 6px',
                    borderRadius: '9999px',
                    backgroundColor: isActive ? '#0284c7' : '#334155',
                    color: 'white',
                    fontWeight: 600,
                  }}
                >
                  {item.badge}
                </span>
              )}
            </div>
          );
        })}
      </nav>

      <div className="sidebar-footer" style={{ flexDirection: 'column', gap: '4px', alignItems: 'flex-start' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
          <span>Oracle 10.2.0.1 Emulation</span>
          <span style={{ color: '#10b981' }}>● Online</span>
        </div>
        <div style={{ fontSize: '11px', marginTop: '4px' }}>
          Maintained by{' '}
          <a
            href="https://github.com/rcpspk0305-bit/SQL-10G.git"
            target="_blank"
            rel="noreferrer"
            style={{ color: '#38bdf8', textDecoration: 'none', fontWeight: 600 }}
          >
            Charan Rajanala
          </a>
        </div>
      </div>
    </aside>
  );
};
