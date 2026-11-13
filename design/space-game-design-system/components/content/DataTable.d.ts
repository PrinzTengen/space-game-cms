import * as React from 'react';
/** Plain comparison table (system requirements). Horizontal scroll inside, accent column labels. */
export interface DataTableProps {
  columns: string[];
  /** Erste Zelle jeder Zeile wird zum Zeilenkopf */
  rows: React.ReactNode[][];
  minWidth?: number;
  emphasizeLast?: boolean;
}
export declare function DataTable(props: DataTableProps): JSX.Element;
