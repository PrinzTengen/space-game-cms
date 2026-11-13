import * as React from 'react';
/** FAQ accordion — one item open at a time, +/− square toggle. */
export interface AccordionProps {
  items: { q: string; a: React.ReactNode }[];
  idPrefix?: string;
  /** Index des initial offenen Eintrags, -1 = keiner */
  defaultOpen?: number;
}
export declare function Accordion(props: AccordionProps): JSX.Element;
export interface AccordionItemProps { id: string; question: string; answer: React.ReactNode; open?: boolean; onToggle?: () => void; }
export declare function AccordionItem(props: AccordionItemProps): JSX.Element;
