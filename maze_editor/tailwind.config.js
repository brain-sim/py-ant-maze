/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        mono: ['"IBM Plex Mono"', '"JetBrains Mono"', '"Courier New"', 'monospace'],
      },
      colors: {
        primary: "#111",
        secondary: "#444",
        accent: "#0070f3",
      }
    },
  },
  plugins: [],
}
