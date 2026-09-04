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
        background: '#080B11',
        backgroundDeep: '#05070B',
        surface: '#0F1523',
        surfaceSubtle: '#0B0F19',
        surfaceCard: '#111728',
        surfaceHover: '#182035',
        surfaceActive: '#1F2943',
        border: '#1B2438',
        borderSubtle: '#141B2B',
        borderLight: '#263352',
        primary: {
          DEFAULT: '#3B82F6',
          hover: '#2563EB',
          muted: 'rgba(59, 130, 246, 0.12)',
          foreground: '#FFFFFF',
        },
        success: {
          DEFAULT: '#10B981',
          muted: 'rgba(16, 185, 129, 0.12)',
          foreground: '#FFFFFF',
        },
        warning: {
          DEFAULT: '#F59E0B',
          muted: 'rgba(245, 158, 11, 0.12)',
          foreground: '#FFFFFF',
        },
        danger: {
          DEFAULT: '#EF4444',
          muted: 'rgba(239, 68, 68, 0.12)',
          foreground: '#FFFFFF',
        },
        accent: {
          DEFAULT: '#8B5CF6',
          muted: 'rgba(139, 92, 246, 0.12)',
        },
        muted: '#64748B',
        mutedForeground: '#94A3B8',
        foreground: '#F8FAFC',
      },
      boxShadow: {
        'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.35)',
        'card-elevated': '0 4px 20px -2px rgba(0, 0, 0, 0.45)',
        'popover': '0 10px 30px -5px rgba(0, 0, 0, 0.6)',
      },
      transitionTimingFunction: {
        'fintech': 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
      animation: {
        'fade-in': 'fadeIn 200ms ease-out forwards',
        'slide-up': 'slideUp 250ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'enter-stagger': 'enterStagger 350ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'pulse-subtle': 'pulseSubtle 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        enterStagger: {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
      },
    },
  },
  plugins: [],
};
