import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    proxy: {
      '/chat': 'http://127.0.0.1:8000',
      '/config/model': 'http://127.0.0.1:8000',
      '/session/usage': 'http://127.0.0.1:8000',
      '/session/clear': 'http://127.0.0.1:8000',
      '/idle': 'http://127.0.0.1:8000',
      '/blink': 'http://127.0.0.1:8000',
      '/talk': 'http://127.0.0.1:8000',
      '/think': 'http://127.0.0.1:8000',
      '/think_blink': 'http://127.0.0.1:8000',
      '/error': 'http://127.0.0.1:8000',
    }
  }
})
