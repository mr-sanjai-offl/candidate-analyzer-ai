'use client'

import * as React from 'react'
import { ProtectedRoute, useAuth } from '@/providers/AuthProvider'
import { useChatMessage } from '@/hooks/use-ai'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { PageHeader } from '@/components/ui/layout-primitives'
import { Input } from '@/components/ui/input'
import { Send, Bot, User as UserIcon, MessageSquare } from 'lucide-react'
import { toast } from 'sonner'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

export default function AIChatPage() {
  const { user } = useAuth()
  const chatMutation = useChatMessage()
  
  // Recruiter can paste target candidate profile uuid; Candidate defaults to their own uuid
  const [candidateId, setCandidateId] = React.useState(user?.role === 'CANDIDATE' ? user.id : '')
  const [sessionId, setSessionId] = React.useState<string | undefined>(undefined)
  const [inputMessage, setInputMessage] = React.useState('')
  const [messages, setMessages] = React.useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Hello! I am your candidate assessment assistant. Ask me questions about skills, code repositories, or readiness benchmarks.',
    },
  ])

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputMessage.trim() || !candidateId.trim()) return

    const tempUserMsg: Message = {
      id: Math.random().toString(),
      role: 'user',
      content: inputMessage,
    }

    setMessages((prev) => [...prev, tempUserMsg])
    const sentContent = inputMessage
    setInputMessage('')

    try {
      const response = await chatMutation.mutateAsync({
        candidateId,
        sessionId,
        message: sentContent,
      })

      if (response.session_id) {
        setSessionId(response.session_id)
      }

      const tempAssistantMsg: Message = {
        id: response.reply.id || Math.random().toString(),
        role: 'assistant',
        content: response.reply.content,
      }

      setMessages((prev) => [...prev, tempAssistantMsg])
    } catch {
      toast.error('Failed to communicate with AI helper.')
      setMessages((prev) => [
        ...prev,
        {
          id: Math.random().toString(),
          role: 'assistant',
          content: '⚠️ Failed to get reply from evaluation engine. Please confirm candidate UUID is correct and try again.',
        },
      ])
    }
  }

  const suggestQuestion = (q: string) => {
    setInputMessage(q)
  }

  return (
    <ProtectedRoute allowedRoles={['CANDIDATE', 'RECRUITER', 'ADMIN']}>
      <div className="space-y-6 max-w-5xl mx-auto">
        <PageHeader
          title="Q&A Chat Assistant"
          description="Ask questions about verified capabilities and experience parameters."
        />

        {/* Candidate Identifier Input (Recruiter Mode) */}
        {user?.role !== 'CANDIDATE' && (
          <Card>
            <CardContent className="p-4">
              <Input
                label="Target Candidate Profile UUID"
                placeholder="00000000-0000-0000-0000-000000000000"
                value={candidateId}
                onChange={(e) => setCandidateId(e.target.value)}
              />
            </CardContent>
          </Card>
        )}

        <div className="grid gap-6 md:grid-cols-4">
          {/* Suggestions Sidebar */}
          <div className="md:col-span-1 space-y-4">
            <Card>
              <CardHeader className="p-4">
                <CardTitle className="text-sm font-semibold flex items-center gap-2">
                  <MessageSquare className="h-4 w-4 text-primary" />
                  Suggested Prompts
                </CardTitle>
              </CardHeader>
              <CardContent className="p-3 pt-0 space-y-2">
                {[
                  'What are the strongest skills?',
                  'Rate the LeetCode proficiency.',
                  'List potential project matches.',
                ].map((q) => (
                  <button
                    key={q}
                    onClick={() => suggestQuestion(q)}
                    className="w-full text-left p-2 rounded border hover:bg-muted text-xs transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Chat Interface */}
          <Card className="md:col-span-3 h-[600px] flex flex-col">
            <div className="flex-1 p-4 overflow-y-auto space-y-4">
              {messages.map((m) => (
                <div
                  key={m.id}
                  className={`flex gap-3 max-w-[85%] ${
                    m.role === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'
                  }`}
                >
                  <div
                    className={`p-2.5 rounded-lg text-sm ${
                      m.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted border text-foreground'
                    }`}
                  >
                    <div className="flex items-center gap-1.5 mb-1.5 opacity-80 text-[10px]">
                      {m.role === 'user' ? (
                        <>
                          <span>You</span>
                          <UserIcon className="h-3 w-3" />
                        </>
                      ) : (
                        <>
                          <Bot className="h-3 w-3" />
                          <span>AI Assessment Assistant</span>
                        </>
                      )}
                    </div>
                    <p className="whitespace-pre-wrap">{m.content}</p>
                  </div>
                </div>
              ))}

              {chatMutation.isPending && (
                <div className="flex gap-3 max-w-[80%] mr-auto items-center">
                  <Bot className="h-5 w-5 text-primary animate-pulse" />
                  <div className="flex gap-1">
                    <span className="h-1.5 w-1.5 bg-muted-foreground rounded-full animate-bounce" />
                    <span className="h-1.5 w-1.5 bg-muted-foreground rounded-full animate-bounce [animation-delay:0.2s]" />
                    <span className="h-1.5 w-1.5 bg-muted-foreground rounded-full animate-bounce [animation-delay:0.4s]" />
                  </div>
                </div>
              )}
            </div>

            {/* Input form */}
            <form onSubmit={handleSend} className="p-3 border-t flex gap-2">
              <input
                type="text"
                placeholder="Ask about candidate capabilities..."
                className="flex-1 h-9 rounded-md border border-input bg-transparent px-3 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                disabled={!candidateId.trim() || chatMutation.isPending}
              />
              <Button type="submit" disabled={!candidateId.trim() || !inputMessage.trim()} loading={chatMutation.isPending}>
                <Send className="h-4 w-4" />
              </Button>
            </form>
          </Card>
        </div>
      </div>
    </ProtectedRoute>
  )
}
