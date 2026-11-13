import * as React from 'react';
/** Key/value readout in an inset well (file name, size, version, SHA-256). */
export interface SpecListProps {
  items: [string, React.ReactNode][];
}
export declare function SpecList(props: SpecListProps): JSX.Element;
