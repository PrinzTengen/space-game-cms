import * as React from 'react';
/** Horizontal progress steps (Download flow). done = green check, current = accent, pending = muted. */
export interface StepperStep { label: string; status: string; state: 'done' | 'current' | 'pending'; }
export interface StepperProps { steps: StepperStep[]; }
export declare function Stepper(props: StepperProps): JSX.Element;
