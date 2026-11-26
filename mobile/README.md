# InterviewIQ AI — Mobile Application (Android / React Native / Expo)

## Overview
The mobile client for **InterviewIQ AI**, built using React Native, Expo, and TypeScript. It delivers a native mobile interview experience featuring simulated questions, real-time response countdowns, instant AI rubric scoring, and historical performance tracking.

---

## Prerequisites
- Node.js 18+ (verified with Node.js v22.19.0)
- npm or pnpm
- Expo Go app on your physical Android phone (from Google Play Store) OR Android Studio Emulator.

---

## Quick Start Commands

### 1. Install Dependencies
```bash
cd mobile
npm install
```

### 2. Start Expo Development Server
```bash
npx expo start
```

### 3. Running on Android
- **Physical Device**: Scan the QR code displayed in the terminal using the **Expo Go** Android application.
- **Android Emulator**: Press `a` in the terminal to launch on the running emulator.
- **Web Preview**: Press `w` in the terminal to inspect in a browser.

---

## Directory Architecture
```
mobile/
├── src/
│   ├── constants/       # Colors, API endpoints, App configuration
│   ├── types/           # TypeScript interfaces (Auth, Interview, Evaluation)
│   ├── services/        # Axios API client & SecureStore token persistence
│   ├── context/         # AuthProvider & user session state
│   ├── components/      # UI primitives: Button, Input, Card, ProgressBar
│   ├── screens/         # Login, Register, Dashboard, Setup, ActiveInterview, Results, History
│   └── navigation/      # React Navigation Native Stack container
├── App.tsx              # Root component with Providers
├── app.json             # Expo project configuration
└── package.json         # Dependencies & scripts
```

