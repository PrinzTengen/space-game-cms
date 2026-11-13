import * as React from 'react';
/** Inline result message (download started, warning, error). Signal color only. */
export interface NoticeProps {
  tone?: 'success' | 'warn' | 'danger';
  title: string;
  children?: React.ReactNode;
  action?: React.ReactNode;
}
export declare function Notice(props: NoticeProps): JSX.Element;
