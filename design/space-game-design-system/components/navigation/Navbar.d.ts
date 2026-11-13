import * as React from 'react';
/**
 * Sticky top bar: blurred panel glass, 1px bottom line, wordmark, uppercase nav with accent underline, right slot.
 * @startingPoint section="Navigation" subtitle="Header mit Wortmarke, Navigation, Sprache, Anmelden" viewport="1100x80"
 */
export interface NavbarItem { label: string; active?: boolean; onClick?: () => void; }
export interface NavbarProps {
  items?: NavbarItem[];
  badge?: string;
  onHome?: () => void;
  navLabel?: string;
  /** Rechter Bereich: Sprachwahl + Anmelden/UserChip */
  right?: React.ReactNode;
  sticky?: boolean;
}
export declare function Navbar(props: NavbarProps): JSX.Element;
