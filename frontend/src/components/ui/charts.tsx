'use client'

import * as React from 'react'
import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
} from 'recharts'

// --- Radar Chart ---
interface RadarData {
  subject: string
  score: number
}

interface CapabilityRadarProps {
  data: RadarData[]
  title?: string
}

export function CapabilityRadar({ data, title }: CapabilityRadarProps) {
  return (
    <div className="w-full h-[300px] flex flex-col justify-center">
      {title && <h4 className="text-sm font-semibold text-center mb-2">{title}</h4>}
      <ResponsiveContainer width="100%" height="90%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
          <PolarGrid stroke="hsl(var(--muted-foreground))" opacity={0.2} />
          <PolarAngleAxis dataKey="subject" tick={{ fill: 'currentColor', fontSize: 11 }} className="text-muted-foreground" />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: 'currentColor', fontSize: 10 }} className="text-muted-foreground" />
          <Radar
            name="Score"
            dataKey="score"
            stroke="hsl(var(--primary))"
            fill="hsl(var(--primary))"
            fillOpacity={0.6}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}

// --- Bar Chart ---
interface BarData {
  name: string
  score: number
}

interface ReadinessBarProps {
  data: BarData[]
  title?: string
}

export function ReadinessBar({ data, title }: ReadinessBarProps) {
  return (
    <div className="w-full h-[300px] flex flex-col justify-center">
      {title && <h4 className="text-sm font-semibold text-center mb-2">{title}</h4>}
      <ResponsiveContainer width="100%" height="90%">
        <RechartsBarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
          <XAxis dataKey="name" tick={{ fill: 'currentColor', fontSize: 11 }} className="text-muted-foreground" />
          <YAxis domain={[0, 100]} tick={{ fill: 'currentColor', fontSize: 11 }} className="text-muted-foreground" />
          <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--popover))', borderColor: 'hsl(var(--border))' }} />
          <Bar dataKey="score" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  )
}

// --- Pie Chart ---
interface PieData {
  name: string
  value: number
}

interface LanguageDistributionProps {
  data: PieData[]
  title?: string
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

export function LanguageDistribution({ data, title }: LanguageDistributionProps) {
  return (
    <div className="w-full h-[300px] flex flex-col justify-center">
      {title && <h4 className="text-sm font-semibold text-center mb-2">{title}</h4>}
      <ResponsiveContainer width="100%" height="90%">
        <RechartsPieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
          >
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--popover))', borderColor: 'hsl(var(--border))' }} />
          <Legend formatter={(value) => <span className="text-xs text-muted-foreground">{value}</span>} />
        </RechartsPieChart>
      </ResponsiveContainer>
    </div>
  )
}
