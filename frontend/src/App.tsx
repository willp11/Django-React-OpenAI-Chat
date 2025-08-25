import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

const testFetch = async (): Promise<{message: string}> => {
  const response = await fetch('api/test/')
  const data = await response.json()
  return data
}

function App() {
  const [count, setCount] = useState(0)
  const [data, setData] = useState<string | null>(null)

  const handleClick = async () => {
    const data = await testFetch()
    setData(data.message)
  }

  return (
    <div className="flex flex-col items-center h-screen gap-4">
      <div className="flex justify-center items-center">
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1 className="text-2xl font-bold">Vite + React</h1>
      <div className="flex flex-col items-center gap-2">
        <button className="bg-blue-500 text-white p-2 rounded-md" onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
      <button className="bg-blue-500 text-white p-2 rounded-md" onClick={handleClick}>
        Test Fetch
      </button>
      <p>{data}</p>
    </div>
  )
}

export default App
