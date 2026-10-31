/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        nexus: {
          950: '#070a11',
          900: '#0b0f19',
          800: '#111827',
          700: '#1f293d',
          accent: '#06b6d4',
          glow: '#38bdf8'
        }
      }
    },
  },
  plugins: [],
}