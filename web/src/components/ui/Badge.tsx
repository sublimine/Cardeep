import type { CSSProperties, ReactNode } from 'react';
import './Badge.css';

type BadgeVariant = 'dot' | 'solid' | 'outline';

interface BadgeProps {
  children: ReactNode;
  color?: string;
  variant?: BadgeVariant;
  title?: string;
}

export function Badge({ children, color, variant = 'dot', title }: BadgeProps) {
  const style = color ? ({ '--badge-color': color } as CSSProperties) : undefined;
  return (
    <span className={`badge badge--${variant}`} style={style} title={title}>
      {variant === 'dot' && <i className="badge__dot" aria-hidden="true" />}
      {children}
    </span>
  );
}
