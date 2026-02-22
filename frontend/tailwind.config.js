export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        bg:       'rgb(var(--color-bg) / <alpha-value>)',
        surface:  'rgb(var(--color-surface) / <alpha-value>)',
        surface2: 'rgb(var(--color-surface-2) / <alpha-value>)',
        primary:  'rgb(var(--color-primary) / <alpha-value>)',
        accent:   'rgb(var(--color-accent) / <alpha-value>)',
        apptext:  'rgb(var(--color-text) / <alpha-value>)',
        muted:    'rgb(var(--color-text-muted) / <alpha-value>)',
        success:  'rgb(var(--color-success) / <alpha-value>)',
        danger:   'rgb(var(--color-danger) / <alpha-value>)',
        apbborder: 'rgb(var(--color-border) / <alpha-value>)',
      },
      borderRadius: {
        card: 'var(--radius-card)',
        btn:  'var(--radius-btn)',
      },
    },
  },
  plugins: [],
}
