# ICE QAgent — Frontend

Standalone React 18 + TypeScript + Vite landing page for the ICE QAgent
onboarding assistant. Custom vanilla-CSS architecture, no utility framework.

## Stack

- React 18 + TypeScript
- Vite 5
- Vanilla CSS layered as `tokens → reset → typography → layout → components`
- EB Garamond (serif display) + Inter (sans utility) from Google Fonts

## Run

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
npm run build        # production build → dist/
npm run preview
```

The `Enter Dashboard` CTA links to the existing Streamlit app. Override
the URL with an env var:

```bash
VITE_DASHBOARD_URL=http://localhost:8501 npm run dev
```

## Layout

```
src/
├── main.tsx                    # entry
├── App.tsx                     # root component
├── config.ts                   # dashboard URL + agent data
├── pages/
│   └── Home.tsx                # landing page composition
├── components/
│   ├── TopBar.tsx
│   ├── Hero.tsx
│   ├── CTAButton.tsx
│   ├── AgentCard.tsx
│   └── AgentsSection.tsx
└── styles/
    ├── index.css               # single import entry
    ├── tokens.css              # CSS custom properties (colors, type, space)
    ├── reset.css
    ├── typography.css          # .u-* utility classes
    ├── layout.css              # .l-* primitives (container, stack, grid)
    └── components/
        ├── topbar.css
        ├── hero.css
        ├── button.css
        ├── card.css
        └── section.css
```

## CSS conventions

- `--color-*`, `--fs-*`, `--space-*`, `--dur-*` tokens in `tokens.css`
- Utility classes prefixed `u-` (typography) and `l-` (layout)
- Component classes use BEM: `.hero`, `.hero__title`, `.card--primary`
- Never write inline styles for anything reusable; add a token + class
