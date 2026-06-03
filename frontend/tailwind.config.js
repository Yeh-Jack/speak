/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        learning: {
          bg: {
            primary: '#1a1a2e',
            secondary: '#16213e',
            tertiary: '#0f3460',
          },
          accent: {
            primary: '#e94560',
            secondary: '#00d9ff',
            tertiary: '#f5a623',
          },
          text: {
            primary: '#eaeaea',
            secondary: '#94a3b8',
            muted: '#64748b',
          },
          surface: {
            DEFAULT: '#16213e',
            hover: '#1a2744',
            active: '#0f3460',
          },
          success: '#10b981',
          warning: '#f59e0b',
          error: '#ef4444',
        },
      },
      fontFamily: {
        sans: ['Inter', 'Noto Sans TC', 'system-ui', 'sans-serif'],
        display: ['Outfit', 'Inter', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '8px',
        lg: '12px',
        xl: '16px',
      },
      boxShadow: {
        'card': '0 4px 20px rgba(0, 0, 0, 0.3)',
        'card-hover': '0 8px 30px rgba(0, 0, 0, 0.4)',
        'glow-accent': '0 0 20px rgba(233, 69, 96, 0.3)',
        'glow-cyan': '0 0 20px rgba(0, 217, 255, 0.3)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'pulse-subtle': 'pulseSubtle 2s ease-in-out infinite',
        'bounce-gentle': 'bounceGentle 1s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        bounceGentle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
      },
    },
  },
  plugins: [],
}