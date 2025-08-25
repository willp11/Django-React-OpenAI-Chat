import { useState } from 'react'

const chatFetch = async (message: string): Promise<{reply: string}> => {
  const response = await fetch('api/chat/', {
    method: 'POST',
    body: JSON.stringify({message}),
    headers: {
      'Content-Type': 'application/json',
    },
  })
  const data = await response.json()
  return data
}

function App() {
  const [message, setMessage] = useState<string>('')
  const [chatData, setChatData] = useState<string | null>(null)

  const handleChat = async () => {
    const data = await chatFetch(message)
    setChatData(data.reply)
  }

  return (
    <div className="flex flex-col items-center h-screen gap-4 p-4 w-full max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold">Chat with AI</h1>
      <div className="flex flex-col items-center gap-2 w-full">
        <textarea className="border-2 border-gray-300 rounded-md p-2 w-full" value={message} onChange={(e) => setMessage(e.target.value)} />
        <button className="bg-blue-500 text-white p-2 rounded-md" onClick={handleChat}>
          Chat Fetch
        </button>
        <p>{chatData}</p>
      </div>
    </div>
  )
}

export default App
