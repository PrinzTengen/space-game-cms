import * as React from 'react';
/**
 * HUD window — the core surface: 1px border, 14px accent corner brackets, scanlines, dark glass. Square corners.
 * @startingPoint section="Surfaces" subtitle="HUD-Fenster mit Eckwinkeln und Scanlines" viewport="700x280"
 */
export interface WindowProps extends React.HTMLAttributes<HTMLElement> {
  as?: 'div' | 'section' | 'article' | 'li' | 'aside';
  /** Opakes Panel statt Glas */
  solid?: boolean;
  /** Hover hebt um 3px und hellt den Rand auf (Karten) */
  interactive?: boolean;
  /** none · sm 8 (Bildkarten) · md · lg · card (28/26/30) oder eigener CSS-Wert */
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'card' | string;
  children?: React.ReactNode;
}
export declare function Window(props: WindowProps): JSX.Element;
