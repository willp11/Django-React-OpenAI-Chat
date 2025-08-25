import { useState, useEffect, useRef } from 'react'

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

const getChatMessages = async (chat_id: string): Promise<{message: string, content: string}[]> => {
  const response = await fetch(`api/chat-messages/${chat_id}/`, {
    method: 'GET',
  })
  const data = await response.json()
  return data
}

function App() {
  const [question, setQuestion] = useState<string>('')
  const [chats, setChats] = useState<string[]>([])
  const [currentChatId, setCurrentChatId] = useState<string | null>(null)
  const [chatData, setChatData] = useState<{message: string, content: string}[]>([])
  const [isStreaming, setIsStreaming] = useState<boolean>(false)

  const chatContainerRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }

  const focusInput = () => {
    if (inputRef.current) {
      inputRef.current.focus()
      console.log('focused')
    }
  }

  const handleCreateChat = async () => {
    const data = await createChat()
    const new_chats = [...chats, data.chat_id]
    localStorage.setItem('chats', JSON.stringify(new_chats))
    setCurrentChatId(data.chat_id)
    setChats(new_chats)
  }

  const handleChat = async () => {
    setChatData(prev => [...prev, {message: question, content: ''}])

    setIsStreaming(true)
    if (!currentChatId) {
      return
    }

    const currentMessageIndex = chatData.length
    let currentMessage = ''
    
    await chatStream(
      currentChatId,
      question,
      (content) => {
        currentMessage += content
        setChatData(currentChatData => {
          const newChatData = [...currentChatData]
          newChatData[currentMessageIndex].content = currentMessage
          return newChatData
        })
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

  const handleSend = () => {
    if (question.trim() && !isStreaming) {
      handleChat()
      setQuestion('')
    }
  }

  useEffect(() => {
    const chats = JSON.parse(localStorage.getItem('chats') || '[]')
    setChats(chats)
    setCurrentChatId(chats[0])
  }, [])

  useEffect(() => {
    if (currentChatId) {
      getChatMessages(currentChatId).then((data) => {
        setChatData(data)
      })
    }
  }, [currentChatId])

  useEffect(() => {
    scrollToBottom()
  }, [chatData])

  useEffect(() => {
    if (isStreaming) {
      scrollToBottom()
    }
  }, [isStreaming])

  useEffect(() => {
    if (!isStreaming && question === '') {
      setTimeout(focusInput, 50)
    }
  }, [isStreaming, question])

  return (
    <div className="flex flex-col h-screen p-4 gap-4 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-center">Chat with AI</h1>
      
      <div className="flex gap-4 flex-1 min-h-0">
        {/* Left sidebar - Chat selection */}
        <div className="flex flex-col gap-2 w-48 flex-shrink-0">
          <button className="px-4 py-2 rounded-md text-white bg-blue-500 hover:bg-blue-600 cursor-pointer" onClick={handleCreateChat}>New Chat</button>
          <div className="flex flex-col gap-2 overflow-y-auto">
            {chats.map((chat_id: string) => (
              <button key={chat_id} onClick={() => {
                setCurrentChatId(chat_id)
                focusInput()
              }} className={`px-4 py-2 rounded-md border-2 border-gray-300 cursor-pointer hover:bg-gray-100 ${currentChatId === chat_id ? 'bg-gray-100' : ''}`}>Chat {chat_id}</button>
            ))}
          </div>
        </div>
        
        {/* Right side - Chat area and input */}
        <div className="flex flex-col gap-4 flex-1 min-h-0">
          {/* Chat messages area - grows to fill available space */}
          <div
            className="flex-1 border-2 border-gray-300 rounded-md p-4 bg-gray-50 overflow-y-auto min-h-0"
            ref={chatContainerRef}
          >
            {chatData ? (
              <div className="flex flex-col gap-4">
                {chatData.map((message) => (
                  <div className="flex flex-col gap-2" key={message.message}>
                    <div className="font-bold">{message.message}</div>
                    <div className="whitespace-pre-wrap bg-gray-100 p-4 rounded-md">{message.content}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-gray-500">AI response will appear here...</div>
            )}
          </div>
          
          {/* Input area - fixed height */}
          <div className="flex flex-col gap-2 flex-shrink-0">
            <input 
              className="border-2 border-gray-300 rounded-md p-2 w-full" 
              value={question} 
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSend()
                }
              }}
              placeholder="Type your message here..."
              disabled={isStreaming}
              ref={inputRef}
            />
            <div className="flex gap-2">
              <button 
                className={`px-4 py-2 w-full rounded-md text-white ${isStreaming ? 'bg-gray-400' : 'bg-blue-500 hover:bg-blue-600 cursor-pointer'}`}
                onClick={handleSend}
                disabled={isStreaming || !question.trim()}
              >
                {isStreaming ? 'Streaming...' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
