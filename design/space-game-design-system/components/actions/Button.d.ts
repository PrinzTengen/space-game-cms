import * as React from 'react';
/**
 * Primary and secondary actions. variant="galaxy" is the one main CTA per view (glass, stars, orbit, HUD corners, chamfer).
 * @startingPoint section="Actions" subtitle="Galaxy-Hauptbutton und Sekundärbuttons" viewport="700x260"
 */
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** galaxy = Hauptbutton (max. einer pro Ansicht); secondary = Standard */
  variant?: 'galaxy' | 'secondary';
  /** sm 40px · md 46px · lg 56px (galaxy: sm 44 / md+lg 56) */
  size?: 'sm' | 'md' | 'lg';
  /** Versalien mit Sperrung .14em (nur secondary) */
  caps?: boolean;
  /** Glyph nach dem Label, meist "→" oder "↓" – wird in Akzent gesetzt */
  trailing?: React.ReactNode;
  leading?: React.ReactNode;
  fullWidth?: boolean;
  loading?: boolean;
  disabled?: boolean;
  children?: React.ReactNode;
}
export declare function Button(props: ButtonProps): JSX.Element;
