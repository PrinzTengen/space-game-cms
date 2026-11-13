import * as React from 'react';
/** Site footer with glowing accent line at the top edge. */
export interface FooterProps {
  line?: string;
  pagesLabel?: string;
  links?: { label: string; onClick?: () => void }[];
  rights?: string;
}
export declare function Footer(props: FooterProps): JSX.Element;
