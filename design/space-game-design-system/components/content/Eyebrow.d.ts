import * as React from 'react';
/** Uppercase kicker above headings. */
export interface EyebrowProps extends React.HTMLAttributes<HTMLElement> {
  tone?: 'dim' | 'accent';
  /** 12 (Standard) oder 11 */
  size?: number;
  as?: 'p' | 'span' | 'div';
  children?: React.ReactNode;
}
export declare function Eyebrow(props: EyebrowProps): JSX.Element;
