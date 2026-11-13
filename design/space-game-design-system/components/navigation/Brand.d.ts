import * as React from 'react';
/** Wordmark: warm planet orb + "Space Game" + optional status badge. The orb is the only warm color in UI. */
export interface BrandProps {
  /** z. B. "Pre-Alpha" */
  badge?: string;
  label?: string;
  onClick?: () => void;
}
export declare function Brand(props: BrandProps): JSX.Element;
