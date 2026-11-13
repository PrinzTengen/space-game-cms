import * as React from 'react';
/**
 * Large radio tiles (platform choice). Checked = raised hover surface + glowing accent pip.
 * @startingPoint section="Forms" subtitle="Plattform-Auswahl als Radio-Kacheln" viewport="700x140"
 */
export interface RadioCardGroupProps {
  label?: string;
  options: { value: string; label: string; sub?: string }[];
  value: string;
  onChange?: (value: string) => void;
}
export declare function RadioCardGroup(props: RadioCardGroupProps): JSX.Element;
export interface RadioCardProps { label: string; sub?: string; checked?: boolean; onSelect?: () => void; }
export declare function RadioCard(props: RadioCardProps): JSX.Element;
