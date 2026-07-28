import type { ChatMessageItem } from '../../services/chatService'
import { formatDateTime } from '../../utils/formatters'

export const MessageBubble = ({ message }: { message: ChatMessageItem }) => {
  const isUser = message.role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-3xl rounded-3xl px-4 py-3 ${
          isUser ? 'bg-slate-950 text-white' : 'border border-slate-200 bg-slate-50 text-slate-900'
        }`}
      >
        <p className="whitespace-pre-wrap text-sm leading-6">{message.content}</p>
        <p className={`mt-3 text-xs ${isUser ? 'text-slate-300' : 'text-slate-500'}`}>{formatDateTime(message.created_at)}</p>
      </div>
    </div>
  )
}
