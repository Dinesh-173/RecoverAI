/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#090D16',
        surface: '#111726',
        surfaceHover: '#1A2238',
        border: '#1E293B',
        primary: {
          DEFAULT: '#3B82F6',
          hover: '#2563EB',
          foreground: '#FFFFFF',
        },
        success: '#10B981',
        warning: '#F59E0B',
        danger: '#EF4444',
        accent: '#8B5CF6',
        muted: '#64748B',
        foreground: '#F8FAFC',
      },
    },
  },
  plugins: [],
}
