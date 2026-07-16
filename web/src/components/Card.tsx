import { motion } from 'framer-motion'
import React from 'react'
import { cn } from '../lib/cn'

interface CardProps {
  children: React.ReactNode
  className?: string
  padding?: boolean
  hover?: boolean
  onClick?: () => void
  /** Accent glow variant on hover */
  glow?: boolean
  /** Escape hatch for one-off overrides (e.g. a highlighted pricing tier's
   * accent border) — merged on top of the default surface, not a replacement. */
  style?: React.CSSProperties
}

export default function Card({ children, className, padding = true, hover, onClick, glow, style }: CardProps) {
  const interactive = hover || !!onClick

  return (
    <motion.div
      onClick={onClick}
      whileHover={interactive ? {
        y: -1,
        boxShadow: glow
          ? 'var(--shadow-card-hover), var(--shadow-glow-blue)'
          : 'var(--shadow-card-hover)',
      } : undefined}
      transition={{ type: 'spring', stiffness: 420, damping: 28 }}
      className={cn(
        'rounded-[10px] border',
        'relative overflow-hidden',
        padding && 'p-5',
        interactive && 'cursor-pointer select-none',
        className
      )}
      style={{
        background: 'var(--bg-elevated)',
        borderColor: 'var(--border-default)',
        boxShadow: 'var(--shadow-card)',
        ...style,
      }}
    >
      {/* Subtle top-edge highlight */}
      <div
        className="pointer-events-none absolute inset-x-0 top-0 h-px opacity-60"
        style={{ background: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.12) 50%, transparent 100%)' }}
      />
      {children}
    </motion.div>
  )
}
