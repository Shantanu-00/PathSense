"use client"

import { useState } from "react"
import { SendHorizonal } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { toast } from "sonner"
import type { Place, PlacesData } from "@/lib/types"
import { cn } from "@/lib/utils"
import * as api from "@/utils/api"

type Message = { role: "user" | "bot"; content: string }

export function ChatPanel({
  sessionId,
  onSessionId,
  onIncomingPlaces,
  className,
}: {
  sessionId: string | null
  onSessionId: (id: string) => void
  onIncomingPlaces: (places: Place[], start?: Place, end?: Place) => void
  className?: string
}) {
  const [messages, setMessages] = useState<Message[]>([
    { role: "bot", content: "Hi! Tell me what you're planning and I'll suggest places." },
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)

  const sendMessage = async () => {
    if (!input.trim() || loading) return
    const userMsg: Message = { role: "user", content: input.trim() }
    setMessages((m) => [...m, userMsg])
    setInput("")
    setLoading(true)
    try {
      const data = await api.sendChatMessage(userMsg.content, sessionId)
      if (data?.session_id) onSessionId(data.session_id)
      const botMsg: Message = { role: "bot", content: data?.message ?? "…" }
      setMessages((m) => [...m, botMsg])

      if (Array.isArray(data?.places) && data.places.length > 0) {
        onIncomingPlaces(data.places, data.start, data.end)
        toast.success(`Added ${data.places.length} place(s) from chat.`)
      }
    } catch (e: any) {
      toast.error(e?.message || "Chat error: Something went wrong.")
    } finally {
      setLoading(false)
    }
  }

  const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <Card className={cn("flex h-full min-h-0 flex-col bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100", className)}>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Assistant</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 min-h-0 overflow-hidden pb-2">
        <ScrollArea className="h-full pr-2">
          <div className="flex flex-col gap-3">
            {messages.map((m, idx) => (
              <div key={idx} className="text-sm leading-relaxed">
                <span className={m.role === "user" ? "text-blue-600 font-medium" : "text-green-600 font-medium"}>
                  {m.role === "user" ? "You" : "Genie"}
                </span>
                <span className="text-gray-500 dark:text-gray-400">: </span>
                <span className="text-gray-900 dark:text-gray-100">{m.content}</span>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
      <CardFooter className="pt-0">
        <div className="flex w-full items-center gap-2">
          <Input
            placeholder="Type a message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            disabled={loading}
            aria-label="Chat input"
          />
          <Button onClick={sendMessage} disabled={loading}>
            <SendHorizonal className="mr-1 h-4 w-4" />
            Send
          </Button>
        </div>
      </CardFooter>
    </Card>
  )
}