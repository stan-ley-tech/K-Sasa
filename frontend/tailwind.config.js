/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        'grok-bg': '#0F0F13',
        'grok-sidebar': '#17171D',
        'grok-input': '#1E1E24',
        'grok-text': '#E0E0E0',
        'grok-accent': '#7C3AED',
        'grok-user-msg': '#2D2D3A',
        'grok-ai-msg': '#1E1E24',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
