import * as React from 'react';
/** Image container with vignette — post covers, article figures. */
export interface MediaFrameProps extends React.HTMLAttributes<HTMLDivElement> {
  src?: string;
  alt?: string;
  /** CSS aspect-ratio: 16/10 Karte · 21/9 Artikelkopf · 16/9 Abbildung */
  ratio?: string;
  bordered?: boolean;
  /** Text, wenn kein Bild vorhanden */
  placeholder?: string;
  children?: React.ReactNode;
}
export declare function MediaFrame(props: MediaFrameProps): JSX.Element;
