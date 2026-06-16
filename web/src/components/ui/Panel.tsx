import type { ReactNode } from 'react';
import './Panel.css';

interface PanelProps {
  children: ReactNode;
  className?: string;
}

// Glass command-center surface: inner-refraction edge + tinted depth shadow.
// The reusable premium surface that replaces flat cards across the app.
export function Panel({ children, className = '' }: PanelProps) {
  return <div className={`panel ${className}`.trim()}>{children}</div>;
}
