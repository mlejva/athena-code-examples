'use client'
import {
  useState,
  useEffect,
} from 'react'


export interface ProcessOutput {
  type: 'stdout' | 'stderr'
  line: string
  timestamp: number
}

export default function Home() {
  const [messages, setMessages] = useState<ProcessOutput[]>([])
  const [command, setCommand] = useState('print("hello world")')
  const [ws, setWS] = useState<WebSocket | null>(null)

  function handleWSMessage(event: MessageEvent) {
    console.log('WS message', event)

    const data = JSON.parse(event.data)
    const out: ProcessOutput = {
      type: data.type,
      line: data.line,
      timestamp: data.timestamp,
    }
    setMessages((messages) => [...messages, out])
  }


  useEffect(function connectWS() {
    console.log('Connecting to WS')

    const websocket = new WebSocket("ws://localhost:8000/ws");
    websocket.onmessage = handleWSMessage
    websocket.onopen = () => console.log('WS connection opened')
    setWS(websocket)

    return () => {
      console.log('Closing WS connection')
      websocket.close()
    }
  }, [setWS])


  function sendMessage() {
    if (!ws) {
      console.log('Cannot send message, websocket connection is null')
      return
    }

    const m = JSON.stringify({
      command,
    })
    ws.send(m)
  }


  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="flex flex-col items-start justify-start gap-4">

        <div className="flex flex-col items-start justify-start gap-2">
          <h1 className="text-xl font-semibold">Execute Python in sandbox</h1>
          <div className="w-[640px] flex flex-col items-start justify-start gap-2">
            <textarea
              className="rounded w-full p-2 font-mono w-full h-[300px] scroll"
              value={command}
              onChange={(e) => setCommand(e.target.value)}
            />
            <button
              onClick={sendMessage}
              className="bg-blue-500 hover:bg-blue-700 text-white py-1 px-4 rounded"
            >
              Run
            </button>
          </div>
        </div>

        <div className="flex flex-col items-start justify-start">
          <h2 className="font-bold text-lg">Output</h2>
          <div className="p-1 font-mono text-sm whitespace-pre">
            {messages.map((message) => (
              <>
                {message.type === "stdout" && (
                  <div
                    className="p-1 border-l border-zinc-400"
                    key={message.timestamp}
                  >
                    {message.line}
                  </div>
                )}
                {message.type === "stderr" && (
                  <div
                    className="p-1 border-l border-red-600"
                    key={message.timestamp}
                  >
                    {message.line}
                  </div>
                )}
              </>
            ))}
          </div>
        </div>
      </div>
    </main>
  )
}
