import * as React from 'react';
/** Pillar card: title 25px + short text in a window. Used in threes ("Erkunden. Abbauen. Handeln."). */
export interface FeatureCardProps {
  title: string;
  text: string;
  as?: 'li' | 'div' | 'article';
}
export declare function FeatureCard(props: FeatureCardProps): JSX.Element;
