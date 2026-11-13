import * as React from 'react';
/** Segmented toggle — blog filter (with counts) or bare language switch DE/EN. */
export interface SegmentOption { value: string; label: string; count?: number; lang?: string; }
export interface SegmentProps {
  options: SegmentOption[];
  value: string;
  onChange?: (value: string) => void;
  size?: 'sm' | 'md';
  /** Ohne Rahmen-Panel – Sprachwahl im Header */
  bare?: boolean;
  label?: string;
}
export declare function Segment(props: SegmentProps): JSX.Element;
