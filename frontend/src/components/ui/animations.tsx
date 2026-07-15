'use client'

import * as React from 'react'
import { motion, AnimatePresence, type Variants } from 'framer-motion'

// Reduce motion check
const prefersReducedMotion =
  typeof window !== 'undefined'
    ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
    : false

const getTransition = (duration = 0.3, delay = 0) =>
  prefersReducedMotion
    ? { duration: 0 }
    : { duration, delay, ease: [0.25, 0.1, 0.25, 1] as [number, number, number, number] }

// ── Fade ────────────────────────────────────────────────────────────────────────
export function Fade({
  children,
  delay = 0,
  className,
}: {
  children: React.ReactNode
  delay?: number
  className?: string
}) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={getTransition(0.3, delay)}
      className={className}
    >
      {children}
    </motion.div>
  )
}

// ── SlideUp ─────────────────────────────────────────────────────────────────────
export function SlideUp({
  children,
  delay = 0,
  className,
}: {
  children: React.ReactNode
  delay?: number
  className?: string
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      transition={getTransition(0.4, delay)}
      className={className}
    >
      {children}
    </motion.div>
  )
}

// ── Scale ───────────────────────────────────────────────────────────────────────
export function ScaleIn({
  children,
  delay = 0,
  className,
}: {
  children: React.ReactNode
  delay?: number
  className?: string
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={getTransition(0.3, delay)}
      className={className}
    >
      {children}
    </motion.div>
  )
}

// ── Stagger Container ───────────────────────────────────────────────────────────
const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: prefersReducedMotion ? 0 : 0.1,
    },
  },
}

const staggerItem: Variants = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0 },
}

export function StaggerList({
  children,
  className,
}: {
  children: React.ReactNode
  className?: string
}) {
  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="show"
      className={className}
    >
      {children}
    </motion.div>
  )
}

export function StaggerItem({
  children,
  className,
}: {
  children: React.ReactNode
  className?: string
}) {
  return (
    <motion.div variants={staggerItem} className={className}>
      {children}
    </motion.div>
  )
}

// ── Page Transition ─────────────────────────────────────────────────────────────
export function PageTransition({
  children,
  className,
}: {
  children: React.ReactNode
  className?: string
}) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        transition={getTransition(0.25)}
        className={className}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}

// ── Hover Scale ─────────────────────────────────────────────────────────────────
export function HoverScale({
  children,
  scale = 1.02,
  className,
}: {
  children: React.ReactNode
  scale?: number
  className?: string
}) {
  return (
    <motion.div
      whileHover={prefersReducedMotion ? {} : { scale }}
      whileTap={prefersReducedMotion ? {} : { scale: 0.98 }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
      className={className}
    >
      {children}
    </motion.div>
  )
}
