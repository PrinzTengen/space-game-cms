import * as React from 'react';
/** Signed-in user chip for the header (square avatar with initials + handle). */
export interface UserChipProps { initials: string; handle: string; onClick?: () => void; }
export declare function UserChip(props: UserChipProps): JSX.Element;
export interface AvatarProps { initials: string; size?: number; }
export declare function Avatar(props: AvatarProps): JSX.Element;
