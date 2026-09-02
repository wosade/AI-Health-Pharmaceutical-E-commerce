const BASE = '/api/agent'

export async function chatAdmin(question) {
  const res = await fetch(`${BASE}/admin/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })
  return res.json()
}

export function chatClient(question, onMessage, onDone, onError) {
  fetch(`${BASE}/client/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  }).then(async (res) => {
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.type === 'answer') onMessage(data.content)
            else if (data.type === 'done') onDone(data)
            else if (data.type === 'error') onError(data.message)
          } catch (e) { /* ignore parse errors */ }
        }
      }
    }
  }).catch(onError)
}