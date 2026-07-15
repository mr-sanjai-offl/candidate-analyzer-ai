'use client'

import * as React from 'react'
import {
  useForm,
  FormProvider,
  useFormContext,
  type FieldValues,
  type UseFormReturn,
  type SubmitHandler,
} from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { type ZodType } from 'zod'
import { cn } from '@/lib/utils'

/* eslint-disable @typescript-eslint/no-explicit-any */
// ── Form Wrapper ────────────────────────────────────────────────────────────────
interface FormWrapperProps<T extends FieldValues> {
  schema: ZodType<T, any, any>
  defaultValues?: Partial<T>
  onSubmit: SubmitHandler<T>
  children: (methods: UseFormReturn<T>) => React.ReactNode
  className?: string
}

export function FormWrapper<T extends FieldValues>({
  schema,
  defaultValues,
  onSubmit,
  children,
  className,
}: FormWrapperProps<T>) {
  const methods = useForm<T>({
    resolver: zodResolver(schema) as any,
    defaultValues: defaultValues as any,
  })

  return (
    <FormProvider {...(methods as any)}>
      <form onSubmit={methods.handleSubmit(onSubmit as any)} className={cn('space-y-6', className)}>
        {children(methods)}
      </form>
    </FormProvider>
  )
}
/* eslint-enable @typescript-eslint/no-explicit-any */

// ── Form Field ──────────────────────────────────────────────────────────────────
interface FormFieldProps {
  name: string
  label?: string
  required?: boolean
  children: React.ReactNode
  className?: string
}

export function FormField({ name, label, required, children, className }: FormFieldProps) {
  const {
    formState: { errors },
  } = useFormContext()

  const error = errors[name]

  return (
    <div className={cn('space-y-1.5', className)}>
      {label && (
        <label htmlFor={name} className="text-sm font-medium leading-none">
          {label}
          {required && <span className="text-destructive ml-0.5">*</span>}
        </label>
      )}
      {children}
      {error && (
        <p className="text-xs text-destructive" role="alert">
          {error.message as string}
        </p>
      )}
    </div>
  )
}

// ── Form Section Divider ────────────────────────────────────────────────────────
export function FormSectionHeader({
  title,
  description,
  className,
}: {
  title: string
  description?: string
  className?: string
}) {
  return (
    <div className={cn('space-y-0.5 pb-2 border-b', className)}>
      <h3 className="text-base font-semibold">{title}</h3>
      {description && <p className="text-xs text-muted-foreground">{description}</p>}
    </div>
  )
}
