import * as React from 'react';
/** Post-type tag with glowing dot (News, Devlog #7). */
export interface TagProps {
  tone?: 'accent' | 'good' | 'muted';
  size?: 'sm' | 'md';
  children?: React.ReactNode;
}
export declare function Tag(props: TagProps): JSX.Element;
