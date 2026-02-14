<script>
  import { onMount, onDestroy } from 'svelte';
  import { io } from 'socket.io-client';

  let status = 'standby';
  let transcript = [];
  let waveformData = Array(12).fill(4);
  let socket;
  let showSettings = false;

  const statusConfig = {
    standby: { color: '#94a3b8', text: 'Siap melayani', pulse: false },
    listening: { color: '#f87171', text: 'Mendengarkan...', pulse: true },
    recording: { color: '#fbbf24', text: 'Merekam suara...', pulse: true },
    thinking: { color: '#60a5fa', text: 'Berpikir...', pulse: true },
    speaking: { color: '#34d399', text: 'Berbicara...', pulse: false }
  };

  onMount(() => {
    socket = io('http://127.0.0.1:5000');
    socket.on('state_update', (data) => {
      status = data.status;
      transcript = data.transcript || [];
    });
    animateWaveform();
  });

  onDestroy(() => { socket?.disconnect(); });

  function startListening() { socket?.emit('start'); }
  function stopListening() { socket?.emit('stop'); }
  function clearChat() { 
    socket?.emit('clear'); 
    transcript = []; 
  }

  function animateWaveform() {
    setInterval(() => {
      if (status !== 'standby') {
        waveformData = waveformData.map(() => Math.random() * 40 + 5);
      } else {
        waveformData = waveformData.map(() => 4);
      }
    }, 100);
  }
</script>

<main>
  <div class="glass-container">
    <header>
      <div class="status-indicator">
        <div class="dot" style="background: {statusConfig[status].color}; box-shadow: 0 0 15px {statusConfig[status].color}"></div>
        <span>{statusConfig[status].text}</span>
      </div>
      <button class="icon-btn" on:click={() => showSettings = !showSettings}>⚙️</button>
    </header>

    <div class="visualizer-section">
      <div class="waveform">
        {#each waveformData as height}
          <div class="bar" style="height: {height}px; background: {statusConfig[status].color}"></div>
        {/each}
      </div>
    </div>

    <div class="chat-area">
      {#each transcript as msg}
        <div class="msg-wrapper {msg.type}">
          <div class="bubble">{msg.text}</div>
        </div>
      {/each}
      {#if transcript.length === 0}
        <p class="placeholder">Katakan sesuatu untuk memulai...</p>
      {/if}
    </div>

    {#if showSettings}
      <div class="settings-panel">
        <div class="field">
          <label>Voice</label>
          <select><option>af_sky</option></select>
        </div>
        <div class="field">
          <label>Model</label>
          <select><option>gemma3:1b</option></select>
        </div>
      </div>
    {/if}

    <div class="actions">
      <button class="btn btn-secondary" on:click={clearChat}>Reset</button>
      {#if status === 'standby'}
        <button class="btn btn-primary" on:click={startListening}>Mulai</button>
      {:else}
        <button class="btn btn-danger" on:click={stopListening}>Berhenti</button>
      {/if}
    </div>
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: 'Inter', -apple-system, sans-serif;
    background: #0a0a0c;
    color: #e2e8f0;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
  }

  .glass-container {
    width: 380px;
    background: rgba(23, 23, 26, 0.7);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 28px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  }

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .status-indicator {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.9rem;
    font-weight: 500;
    color: #94a3b8;
  }

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    transition: all 0.3s ease;
  }

  .visualizer-section {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .waveform {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .bar {
    width: 3px;
    border-radius: 10px;
    transition: height 0.1s ease, background 0.3s ease;
  }

  .chat-area {
    height: 250px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding-right: 8px;
  }

  .chat-area::-webkit-scrollbar { width: 4px; }
  .chat-area::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }

  .msg-wrapper { display: flex; width: 100%; }
  .msg-wrapper.user { justify-content: flex-end; }
  
  .bubble {
    max-width: 85%;
    padding: 10px 14px;
    border-radius: 18px;
    font-size: 0.95rem;
    line-height: 1.4;
  }

  .user .bubble { background: #3b82f6; color: white; border-bottom-right-radius: 4px; }
  .ai .bubble { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-bottom-left-radius: 4px; }

  .placeholder { text-align: center; color: #4b5563; font-size: 0.85rem; margin-top: 40px; }

  .actions {
    display: flex;
    gap: 12px;
  }

  .btn {
    flex: 1;
    padding: 12px;
    border: none;
    border-radius: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s, filter 0.2s;
  }

  .btn:active { transform: scale(0.98); }
  
  .btn-primary { background: #f8fafc; color: #0f172a; }
  .btn-secondary { background: rgba(255,255,255,0.05); color: #94a3b8; }
  .btn-danger { background: #ef4444; color: white; }

  .settings-panel {
    background: rgba(0,0,0,0.2);
    padding: 12px;
    border-radius: 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .field {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.8rem;
  }

  select {
    background: transparent;
    border: 1px solid rgba(255,255,255,0.1);
    color: white;
    padding: 4px 8px;
    border-radius: 6px;
  }

  .icon-btn {
    background: none;
    border: none;
    cursor: pointer;
    filter: grayscale(1);
    opacity: 0.5;
  }
</style>