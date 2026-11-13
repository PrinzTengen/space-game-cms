import React from 'react';

export function DataTable({ columns = [], rows = [], minWidth = 420, emphasizeLast = true }) {
  const last = columns.length - 1;
  return (
    <div style={{ overflowX: 'auto', overflowY: 'hidden' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 15, minWidth, color: 'var(--sg-title)' }}>
        <thead><tr style={{ fontSize: 11, color: 'var(--sg-accent)', borderBottom: '1px solid var(--sg-line)' }}>
          {columns.map((c, i) => <th key={i} scope="col" style={{ textAlign: 'left', padding: i === 0 ? '10px 12px 10px 0' : i === last ? '10px 0 10px 12px' : '10px 12px', fontWeight: 500 }}>{c}</th>)}
        </tr></thead>
        <tbody>{rows.map((r, ri) => <tr key={ri} style={{ borderBottom: '1px solid var(--sg-line)' }}>
          {r.map((cell, i) => i === 0
            ? <th key={i} scope="row" style={{ textAlign: 'left', padding: '14px 12px 14px 0', fontWeight: 500, color: 'var(--sg-text)', verticalAlign: 'top' }}>{cell}</th>
            : <td key={i} style={{ padding: i === last ? '14px 0 14px 12px' : '14px 12px', lineHeight: 1.45, verticalAlign: 'top', fontWeight: emphasizeLast && i === last ? 600 : 400 }}>{cell}</td>)}
        </tr>)}</tbody>
      </table>
    </div>
  );
}
