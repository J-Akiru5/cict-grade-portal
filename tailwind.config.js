/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./app/**/*.py",
  ],
  theme: {
    extend: {
      colors: {
        'primary-maroon': '#5B0000',
        'maroon-dark': '#3D0000',
        'maroon-light': '#7A0000',
        'accent-gold': '#EAB308',
        'gold-dark': '#CA8A04',
        'surface-dark': '#1A1A1A',
        'surface-mid': '#2D2D2D',
        'surface-light': '#FFFFFF',
        'status-pass': '#22C55E',
        'status-fail': '#EF4444',
        'status-inc': '#F59E0B',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      backgroundImage: {
        'maroon-radial': 'radial-gradient(circle at top right, #5B0000 0%, #1e1e2e 40%, #0f0f0f 100%)',
      },
      boxShadow: {
        'gold': '4px 4px 0px 0px rgba(234,179,8,1)',
        'gold-sm': '2px 2px 0px 0px rgba(234,179,8,1)',
      },
    },
  },
  plugins: [],
}
