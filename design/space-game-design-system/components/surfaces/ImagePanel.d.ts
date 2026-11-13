import * as React from 'react';
/** Full-width image panel with dark scrim — closing CTA sections. */
export interface ImagePanelProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Bild-URL (Spielbild, z. B. assets/cta-station.png) */
  src: string;
  /** background-position, Standard "center 55%" */
  position?: string;
  align?: 'center' | 'left';
  children?: React.ReactNode;
}
export declare function ImagePanel(props: ImagePanelProps): JSX.Element;
