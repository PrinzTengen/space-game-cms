import * as React from 'react';
/** Small status pip. Signal colors only with meaning. */
export interface StatusDotProps {
  tone?: 'good' | 'warn' | 'danger' | 'accent' | 'muted';
  size?: number;
  /** Zugänglicher Text, sonst dekorativ */
  label?: string;
}
export declare function StatusDot(props: StatusDotProps): JSX.Element;
