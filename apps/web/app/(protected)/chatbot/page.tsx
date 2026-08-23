"use client"

import * as React from "react"
import { Send } from "lucide-react"
import { createConversation, getConversation, sendConversationMessage, type ConversationDetail } from "@/lib/api/product-search"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export default function ChatbotPage() {
  const [message, setMessage] = React.useState("")
  const [conversation, setConversation] = React.useState<ConversationDetail | null>(null)
  const [error, setError] = React.useState("")
  const [isSending, setIsSending] = React.useState(false)

  React.useEffect(() => {
    const storedId = window.sessionStorage.getItem("buyseconds:conversation-id")
    if (storedId) {
      void getConversation(storedId).then(setConversation).catch(() => window.sessionStorage.removeItem("buyseconds:conversation-id"))
      return
    }
    void createConversation().then((created) => {
      window.sessionStorage.setItem("buyseconds:conversation-id", created.conversation.id)
      setConversation(created)
    }).catch((reason: Error) => setError(reason.message))
  }, [])

  async function send() {
    if (!message.trim() || !conversation) return
    setIsSending(true)
    try { setConversation(await sendConversationMessage(conversation.conversation.id, message.trim())); setMessage("") }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Could not send message.") }
    finally { setIsSending(false) }
  }

  function renderMessage(content: string) {
    return content.split(/(https?:\/\/[^\s]+)/g).map((part, index) =>
      part.startsWith("http") ? <a key={index} href={part} target="_blank" rel="noreferrer" className="underline">View source</a> : part
    )
  }

  return <div className="mx-auto flex min-h-svh max-w-3xl flex-col px-4 py-8 sm:px-6 sm:py-10"><p className="text-sm font-medium text-primary">Guided discovery</p><h1 className="font-heading text-2xl font-semibold">Find a car by chat</h1><div className="mt-6 flex-1 rounded-xl border bg-card p-5"><div className="max-w-lg rounded-lg bg-muted p-3 text-sm">What kind of used car are you looking for? Start with a city and any preferences you have.</div>{conversation?.messages.map((item) => <div key={item.id} className={`mt-3 max-w-lg whitespace-pre-line rounded-lg p-3 text-sm ${item.role === "user" ? "ml-auto bg-primary text-primary-foreground" : "bg-muted"}`}>{renderMessage(item.content)}</div>)}{conversation?.messages.some((item) => item.role === "assistant" && item.content.startsWith("Top ")) && <Button className="mt-3" variant="outline" onClick={() => { setMessage("Show more results"); void send() }}>More results</Button>}{error && <p className="mt-3 text-sm text-destructive">{error}</p>}</div><form className="mt-4 flex gap-2" onSubmit={(event) => { event.preventDefault(); void send() }}><Input value={message} onChange={(event) => setMessage(event.target.value)} placeholder="For example: a petrol SUV in Bengaluru" aria-label="Chat message" /><Button type="submit" size="icon" aria-label="Send message" disabled={isSending || !conversation}><Send /></Button></form></div>
}
