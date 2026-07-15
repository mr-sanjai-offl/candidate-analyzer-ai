'use client'

import * as React from 'react'
import { Send, User, Bot } from 'lucide-react'
import { Button } from './button'
import { Input } from './input'
import { Avatar, AvatarFallback } from './primitives'
import { cn } from '@/lib/utils'

export interface Message {
  id: string
  sender: 'user' | 'assistant'
  text: string
  timestamp: string
}

interface ChatWindowProps {
  messages: Message[]
  onSendMessage?: (text: string) => void
  loading?: boolean
}

export function ChatWindow({ messages, onSendMessage, loading = false }: ChatWindowProps) {
  const [input, setInput] = React.useState('')
  const scrollRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return
    if (onSendMessage) onSendMessage(input)
    setInput('')
  }

  return (
    <div className="flex flex-col h-[500px] border rounded-lg bg-card overflow-hidden">
      {/* Header */}
      <div className="bg-muted/50 border-b px-4 py-3 flex items-center gap-2">
        <Bot className="h-5 w-5 text-primary animate-pulse" />
        <span className="font-semibold text-sm">AI Assistant</span>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => {
          const isUser = msg.sender === 'user'
          return (
            <div key={msg.id} className={cn('flex items-start gap-3', isUser ? 'flex-row-reverse' : 'flex-row')}>
              <Avatar className="h-8 w-8 select-none">
                <AvatarFallback className={isUser ? 'bg-primary text-primary-foreground' : 'bg-muted'}>
                  {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </AvatarFallback>
              </Avatar>
              <div className={cn('max-w-[70%] rounded-lg p-3 text-sm shadow-sm', isUser ? 'bg-primary text-primary-foreground' : 'bg-muted border')}>
                <p className="whitespace-pre-line leading-relaxed">{msg.text}</p>
                <span className="text-[10px] opacity-70 block text-right mt-1.5">
                  {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
          )
        })}

        {loading && (
          <div className="flex items-start gap-3">
            <Avatar className="h-8 w-8 select-none">
              <AvatarFallback className="bg-muted">
                <Bot className="h-4 w-4" />
              </AvatarFallback>
            </Avatar>
            <div className="bg-muted border rounded-lg p-3 text-sm flex items-center gap-1">
              <span className="h-2 w-2 bg-muted-foreground/40 rounded-full animate-bounce" />
              <span className="h-2 w-2 bg-muted-foreground/40 rounded-full animate-bounce [animation-delay:0.2s]" />
              <span className="h-2 w-2 bg-muted-foreground/40 rounded-full animate-bounce [animation-delay:0.4s]" />
            </div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Input bar */}
      <form onSubmit={handleSend} className="p-3 border-t bg-muted/20 flex gap-2">
        <Input
          placeholder="Ask a question about the candidate..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1"
          disabled={loading}
        />
        <Button type="submit" size="icon" disabled={loading || !input.trim()}>
          <Send className="h-4 w-4" />
        </Button>
      </form>
    </div>
  )
}
