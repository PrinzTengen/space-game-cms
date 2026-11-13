import * as React from 'react';
/**
 * Logbook post card: window with 8px inset, 16:10 image, tag + date, title, excerpt, optional "Weiterlesen".
 * @startingPoint section="Content" subtitle="Logbuch-Karte für News und Devlogs" viewport="380x460"
 */
export interface PostCardProps {
  title: string;
  excerpt: string;
  typeLabel: string;
  date: string;
  iso?: string;
  /** z. B. "6 Min. Lesezeit" */
  read?: string;
  image?: string;
  placeholder?: string;
  /** Label des Weiterlesen-Chips; weglassen auf der Startseite */
  more?: string;
  onOpen?: () => void;
  headingLevel?: 'h2' | 'h3';
}
export declare function PostCard(props: PostCardProps): JSX.Element;
