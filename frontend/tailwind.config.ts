import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './services/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1A3A5C',
        'primary-dark': '#0D2540',
        'primary-light': '#EEF3F8',
        accent: '#0F6E56',
        'accent-dark': '#085041',
        'accent-light': '#E1F5EE',
        gold: '#C9A84C',
        'gold-light': '#FBF5E6',
        warning: '#BA7517',
        danger: '#A32D2D',
        surface: '#F8F9FA',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        devanagari: ['Noto Sans Devanagari', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        badge: '99px',
        input: '10px',
        card: '14px',
        modal: '20px',
      },
      boxShadow: {
        card: '0 1px 3px rgba(13,27,42,0.06), 0 4px 12px rgba(13,27,42,0.05)',
        modal: '0 8px 32px rgba(13,27,42,0.14)',
        lifted: '0 2px 8px rgba(13,27,42,0.10)',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-400px 0' },
          '100%': { backgroundPosition: '400px 0' },
        },
        'sonar-ring': {
          '0%': { transform: 'scale(1)', opacity: '0.6' },
          '100%': { transform: 'scale(2.2)', opacity: '0' },
        },
      },
      animation: {
        shimmer: 'shimmer 1.4s infinite',
        'sonar-1': 'sonar-ring 1.4s infinite',
        'sonar-2': 'sonar-ring 1.4s 0.5s infinite',
      },
    },
  },
  plugins: [],
}
export default config
