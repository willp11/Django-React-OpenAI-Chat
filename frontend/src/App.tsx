import { useState, useEffect } from 'react'

const createChat = async (): Promise<{chat_id: string}> => {
  const response = await fetch('api/create-chat/', {
    method: 'POST',
  })
  const data = await response.json()
  return data
}

const chatStream = async (chat_id: string, message: string, onChunk: (content: string) => void, onComplete: () => void, onError: (error: string) => void) => {
  try {
    const response = await fetch(`api/chat-stream/${chat_id}/`, {
      method: 'POST',
      body: JSON.stringify({message}),
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('No reader available')
    }

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      
      if (done) break
      
      const chunk = decoder.decode(value, { stream: true })
      buffer += chunk

      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            
            if (data.type === 'content') {
              onChunk(data.content)
            } else if (data.type === 'done') {
              onComplete()
              return
            } else if (data.type === 'error') {
              onError(data.error)
              return
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e)
          }
        }
      }
    }
  } catch (error) {
    onError(error instanceof Error ? error.message : 'Unknown error')
  }
}

function App() {
  const [message, setMessage] = useState<string>('')
  const [chatData, setChatData] = useState<string>('')
  const [isStreaming, setIsStreaming] = useState<boolean>(false)
  const [chats, setChats] = useState<string[]>([])
  const [currentChatId, setCurrentChatId] = useState<string | null>(null)


  const handleCreateChat = async () => {
    const data = await createChat()
    const new_chats = [...chats, data.chat_id]
    localStorage.setItem('chats', JSON.stringify(new_chats))
    setCurrentChatId(data.chat_id)
    setChats(new_chats)
  }

  const handleChat = async () => {
    setChatData('')
    setIsStreaming(true)
    if (!currentChatId) {
      return
    }
    
    await chatStream(
      currentChatId,
      message,
      (content) => {
        console.log(content)
        setChatData(prev => prev + content)
      },
      () => {
        setIsStreaming(false)
      },
      (error) => {
        console.error('Streaming error:', error)
        setIsStreaming(false)
      }
    )
  }

  useEffect(() => {
    const chats = JSON.parse(localStorage.getItem('chats') || '[]')
    setChats(chats)
    setCurrentChatId(chats[0])
  }, [])

  return (
    <div className="flex flex-col items-center h-screen gap-4 p-4 w-full max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold">Chat with AI</h1>
      <button className="px-4 py-2 rounded-md text-white bg-blue-500 hover:bg-blue-600 cursor-pointer" onClick={handleCreateChat}>Create Chat</button>
      <div className="flex flex-col gap-2">
        {chats.map((chat_id: string) => (
          <button key={chat_id} onClick={() => setCurrentChatId(chat_id)} className={`px-4 py-2 rounded-md border-2 border-gray-300 cursor-pointer hover:bg-gray-100 ${currentChatId === chat_id ? 'bg-gray-100' : ''}`}>Chat {chat_id}</button>
        ))}
      </div>
      <div className="flex flex-col items-center gap-2 w-full">
        <textarea 
          className="border-2 border-gray-300 rounded-md p-2 w-full h-24" 
          value={message} 
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              if (message.trim() && !isStreaming) {
                handleChat()
              }
            }
          }}
          placeholder="Type your message here..."
          disabled={isStreaming}
        />
        <div className="flex gap-2">
          <button 
            className={`px-4 py-2 rounded-md text-white ${isStreaming ? 'bg-gray-400' : 'bg-blue-500 hover:bg-blue-600 cursor-pointer'}`}
            onClick={handleChat}
            disabled={isStreaming || !message.trim()}
          >
            {isStreaming ? 'Streaming...' : 'Start Chat'}
          </button>
        </div>
        <div className="w-full min-h-32 border-2 border-gray-300 rounded-md p-2 bg-gray-50">
          {chatData ? (
            <div className="whitespace-pre-wrap">{chatData}</div>
          ) : (
            <div className="text-gray-500">AI response will appear here...</div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
