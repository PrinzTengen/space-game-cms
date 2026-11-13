import * as React from 'react';
/** Square glyph button (→, +, −). Used for "next post", accordion toggles. */
export interface IconButtonProps extends React.HTMLAttributes<HTMLElement> {
  /** Kantenlänge in px – 44 (Standard), 52 (Nächster Beitrag), 30 (Radio-Marker) */
  size?: number;
  /** Zugänglicher Name – Pflicht, wenn als Button benutzt */
  label?: string;
  /** Unicode-Glyph, Standard "→" */
  children?: React.ReactNode;
  /** "span" wenn in einem größeren Button verschachtelt */
  as?: 'button' | 'span';
}
export declare function IconButton(props: IconButtonProps): JSX.Element;
