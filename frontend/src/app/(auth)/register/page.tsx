'use client'

import * as React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useAuthStore } from '@/store/authStore'
import { GuestRoute } from '@/providers/AuthProvider'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Checkbox } from '@/components/ui/checkbox'
import { Label, Badge } from '@/components/ui/primitives'
import { Eye, EyeOff, UserPlus, AlertCircle, Check, X } from 'lucide-react'
import { toast } from 'sonner'
import { AxiosError } from 'axios'

const registerSchema = z
  .object({
    fullName: z.string().min(2, 'Name must be at least 2 characters').max(100),
    email: z.string().min(1, 'Email is required').email('Invalid email address'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Must contain an uppercase letter')
      .regex(/[a-z]/, 'Must contain a lowercase letter')
      .regex(/[0-9]/, 'Must contain a digit')
      .regex(/[^a-zA-Z0-9]/, 'Must contain a special character'),
    confirmPassword: z.string().min(1, 'Please confirm your password'),
    role: z.enum(['CANDIDATE', 'RECRUITER']),
    terms: z.boolean().refine((v) => v === true, { message: 'You must accept the terms' }),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  })

type RegisterFormData = z.infer<typeof registerSchema>

function PasswordStrength({ password }: { password: string }) {
  const checks = [
    { label: '8+ characters', met: password.length >= 8 },
    { label: 'Uppercase letter', met: /[A-Z]/.test(password) },
    { label: 'Lowercase letter', met: /[a-z]/.test(password) },
    { label: 'Number', met: /[0-9]/.test(password) },
    { label: 'Special character', met: /[^a-zA-Z0-9]/.test(password) },
  ]

  const score = checks.filter((c) => c.met).length
  const color =
    score <= 1 ? 'bg-destructive' : score <= 3 ? 'bg-amber-500' : score <= 4 ? 'bg-sky-500' : 'bg-emerald-500'

  if (!password) return null

  return (
    <div className="space-y-2 mt-2">
      <div className="flex gap-1">
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className={`h-1.5 flex-1 rounded-full transition-colors ${i < score ? color : 'bg-muted'}`}
          />
        ))}
      </div>
      <div className="grid grid-cols-2 gap-1">
        {checks.map((check) => (
          <div key={check.label} className="flex items-center gap-1.5 text-xs">
            {check.met ? (
              <Check className="h-3 w-3 text-emerald-500" />
            ) : (
              <X className="h-3 w-3 text-muted-foreground" />
            )}
            <span className={check.met ? 'text-emerald-600 dark:text-emerald-400' : 'text-muted-foreground'}>
              {check.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function RegisterPage() {
  const router = useRouter()
  const registerUser = useAuthStore((s) => s.registerUser)
  const loginAction = useAuthStore((s) => s.login)
  const loading = useAuthStore((s) => s.loading)
  const [showPassword, setShowPassword] = React.useState(false)
  const [apiError, setApiError] = React.useState('')

  const {
    register,
    handleSubmit,
    control,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: { fullName: '', email: '', password: '', confirmPassword: '', role: 'CANDIDATE', terms: false },
  })

  const watchPassword = watch('password')
  const watchRole = watch('role')

  const onSubmit = async (data: RegisterFormData) => {
    setApiError('')
    try {
      await registerUser(data.email, data.password, data.fullName, data.role)
      toast.success('Account created! Signing you in...')

      // Auto login
      await loginAction(data.email, data.password)
      router.push('/dashboard')
    } catch (error) {
      if (error instanceof AxiosError) {
        const detail = error.response?.data?.detail
        if (typeof detail === 'string' && detail.toLowerCase().includes('already')) {
          setApiError('An account with this email already exists.')
        } else {
          setApiError(typeof detail === 'string' ? detail : 'Registration failed. Please try again.')
        }
      } else {
        setApiError('An unexpected error occurred.')
      }
    }
  }

  return (
    <GuestRoute>
      <div className="space-y-6">
        <div className="space-y-2 text-center">
          <h1 className="text-2xl font-bold tracking-tight">Create your account</h1>
          <p className="text-sm text-muted-foreground">Get started with ApexGuidance AI</p>
        </div>

        {apiError && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{apiError}</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Full Name"
            placeholder="Jane Doe"
            autoComplete="name"
            error={errors.fullName?.message}
            required
            {...register('fullName')}
          />

          <Input
            label="Email"
            type="email"
            placeholder="you@example.com"
            autoComplete="email"
            error={errors.email?.message}
            required
            {...register('email')}
          />

          <div className="space-y-1.5">
            <label className="text-sm font-medium">
              Password <span className="text-destructive">*</span>
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                autoComplete="new-password"
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 pr-10"
                {...register('password')}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {errors.password && (
              <p className="text-xs text-destructive" role="alert">{errors.password.message}</p>
            )}
            <PasswordStrength password={watchPassword || ''} />
          </div>

          <Input
            label="Confirm Password"
            type="password"
            placeholder="••••••••"
            autoComplete="new-password"
            error={errors.confirmPassword?.message}
            required
            {...register('confirmPassword')}
          />

          {/* Role Selector */}
          <div className="space-y-2">
            <label className="text-sm font-medium">
              I am a <span className="text-destructive">*</span>
            </label>
            <div className="grid grid-cols-2 gap-3">
              {(['CANDIDATE', 'RECRUITER'] as const).map((role) => (
                <label
                  key={role}
                  className={`relative flex cursor-pointer flex-col items-center gap-2 rounded-lg border-2 p-4 text-center transition-colors ${
                    watchRole === role
                      ? 'border-primary bg-primary/5'
                      : 'border-muted-foreground/20 hover:border-muted-foreground/40'
                  }`}
                >
                  <input type="radio" value={role} className="sr-only" {...register('role')} />
                  <span className="text-xl">{role === 'CANDIDATE' ? '👤' : '🏢'}</span>
                  <span className="text-sm font-medium">{role === 'CANDIDATE' ? 'Candidate' : 'Recruiter'}</span>
                  <Badge variant={watchRole === role ? 'default' : 'outline'} className="text-[10px]">
                    {role === 'CANDIDATE' ? 'Job Seeker' : 'Hiring Manager'}
                  </Badge>
                </label>
              ))}
            </div>
            {errors.role && (
              <p className="text-xs text-destructive" role="alert">{errors.role.message}</p>
            )}
          </div>

          {/* Terms */}
          <div className="flex items-start gap-2">
            <Controller
              name="terms"
              control={control}
              render={({ field }) => (
                <Checkbox
                  id="terms"
                  checked={field.value}
                  onCheckedChange={(checked) => field.onChange(!!checked)}
                />
              )}
            />
            <Label htmlFor="terms" className="text-sm cursor-pointer leading-relaxed">
              I agree to the{' '}
              <Link href="#" className="text-primary hover:underline">
                Terms of Service
              </Link>{' '}
              and{' '}
              <Link href="#" className="text-primary hover:underline">
                Privacy Policy
              </Link>
            </Label>
          </div>
          {errors.terms && (
            <p className="text-xs text-destructive" role="alert">{errors.terms.message}</p>
          )}

          <Button type="submit" className="w-full" loading={loading}>
            <UserPlus className="h-4 w-4" />
            Create Account
          </Button>
        </form>

        <div className="text-center text-sm">
          Already have an account?{' '}
          <Link href="/login" className="font-medium text-primary hover:underline">
            Sign in
          </Link>
        </div>
      </div>
    </GuestRoute>
  )
}
