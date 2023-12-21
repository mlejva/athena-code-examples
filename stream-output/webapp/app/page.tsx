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

const generateShortID = () => Math.random().toString(36).substring(2, 15)
const userID = 'user-1'
const startingCode = `import time

print("Start")
for i in range(1, 11):
    print(i)
    time.sleep(1)
print("End")`

export interface Session {
  id: string
  timestamp: number
}

export default function Home() {
  const [sessionID, setSessionID] = useState<string | null>(null)
  const [sessionStatus, setSessionStatus] = useState<string>('session_loading')
  const [previousSessions, setPreviousSessions] = useState<Session[]>([])
  const [messages, setMessages] = useState<ProcessOutput[]>([])
  const [code, setCode] = useState(startingCode)
  const [ws, setWS] = useState<WebSocket | null>(null)

  function handleWSMessage(event: MessageEvent) {
    console.log('WS message', event)
    const data = JSON.parse(event.data)
    if (data['status']) {
      setSessionStatus(data['status'])
    } else if (data['message_type'] === 'process_output') {
      const out: ProcessOutput = {
        type: data.type,
        line: data.line,
        timestamp: data.timestamp,
      }
      setMessages((messages) => [...messages, out])
    } else {
      console.log('Unknown message type', data)
    }
  }

  function handleWSConnOpen(ws: WebSocket) {
    console.log('WS connection opened', ws)

    const m = JSON.stringify({
      message_type: 'new_session',
      user_id: userID,
    })
    ws?.send(m)
  }

  function sendMessage() {
    if (!ws) {
      console.log('Cannot send message, websocket connection is null')
      return
    }

    const m = JSON.stringify({
      message_type: 'code',
      code,
    })
    ws.send(m)
  }

  useEffect(function fetchPreviousSessions() {
    fetch(`http://localhost:8000/${userID}/sessions`, {
      headers: {
        'Content-Type': 'application/json',
      },
      method: 'GET',
    }).then(response => {
      if (response.ok) {
        return response.json()
      } else {
        throw new Error('Failed to fetch previous sessions')
      }
    }).then(data => {
      console.log('Previous sessions', data)
      setPreviousSessions(
        // Extract session ID
        data['sessions'].map((session: any) => ({
          id: session[0],
          timestamp: session[2],
        }))
      )
    })
  }, [])

  useEffect(function fetchSessionOutputs() {
    if (!sessionID) return
    fetch(`http://localhost:8000/sessions/${sessionID}`, {
      headers: {
        'Content-Type': 'application/json',
      },
      method: 'GET',
    }).then(response => {
      if (response.ok) {
        return response.json()
      } else {
        throw new Error('Failed to fetch session outputs')
      }
    }).then(data => {
      console.log('Session outputs', data)
      if (data['outputs'].length == 0) return
      const out: ProcessOutput[] = JSON.parse(data['outputs'][0][1])
      console.log('Session outputs', out)
      setMessages(out)
    })
  }, [sessionID])


  useEffect(function connectWS() {
    const sessID = generateShortID()

    console.log('Connecting to WS')

    const websocket = new WebSocket(`ws://localhost:8000/ws/${sessID}`)
    websocket.onmessage = handleWSMessage
    websocket.onopen = () => handleWSConnOpen(websocket)
    setWS(websocket)
    setSessionID(sessID)

    return () => {
      console.log('Closing WS connection')
      websocket.close()
    }
  }, [])




  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="flex flex-col items-start justify-start gap-4">

        <div className="flex items-center gap-8">
          <div className="flex flex-col items-start justify-start gap-2">
            <h2 className="text-base">Session: {sessionID} ({sessionStatus})</h2>
            <h1 className="text-xl font-semibold">Execute Python in sandbox & stream it back</h1>
            <div className="w-[640px] flex flex-col items-start justify-start gap-2">
              <span className="text-sm">Code</span>
              <textarea
                className="rounded w-full p-2 font-mono w-full h-[300px] scroll"
                value={code}
                onChange={(e) => setCode(e.target.value)}
              />
              <button
                onClick={sendMessage}
                className="bg-blue-500 hover:bg-blue-700 text-white py-1 px-4 rounded"
              >
                Run
              </button>
            </div>
          </div>

          <div className="flex flex-col items-start justify-start gap-2">
            <h2 className="font-bold text-lg">Previous sessions</h2>
            <span className="text-sm">Select a session to view its outputs</span>
            <div className="flex flex-col items-start justify-start gap-2 max-h-[400px] overflow-y-auto w-full">
              {previousSessions.map((session) => (
                <button
                  className="flex items-center gap-2 text-blue-500 hover:text-blue-700"
                  key={session.id}
                  onClick={() => setSessionID(session.id)}
                >{session.id} ({session.timestamp})</button>
              ))}
            </div>
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
