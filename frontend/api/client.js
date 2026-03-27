const API_BASE = 'http://localhost:8000';

export async function fetchPersonas() {
    const response = await fetch(`${API_BASE}/personas`);
    return response.json();
}

export async function chatStream(personaName, message, onChunk, onDone, onError) {
    const response = await fetch(
        `${API_BASE}/chat/stream?persona_name=${encodeURIComponent(personaName)}`,
        {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: message, thread_id: 'default' })
        }
    );

    if (!response.ok) {
        onError(`Error: ${response.status}`);
        return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        // SSE parsing
        chunk.split('\n').forEach(line => {
            if (line.startsWith('data: ')) {
                const data = line.slice(6);
                if (data === '[DONE]') {
                    onDone();
                } else if (data.startsWith('[ERROR]')) {
                    onError(data);
                } else {
                    onChunk(data);
                }
            }
        });
    }
}
