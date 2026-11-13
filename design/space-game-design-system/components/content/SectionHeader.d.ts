import * as React from 'react';
/** Eyebrow + title (+ lead) with optional right-aligned action. */
export interface SectionHeaderProps {
  eyebrow?: string;
  title: React.ReactNode;
  lead?: string;
  /** page = Seitentitel h1 72px; section = h2 42px */
  level?: 'page' | 'section';
  as?: 'h1' | 'h2' | 'h3';
  action?: React.ReactNode;
  id?: string;
}
export declare function SectionHeader(props: SectionHeaderProps): JSX.Element;
