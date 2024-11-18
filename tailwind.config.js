import Layout from './src/layouts/Layout.astro';

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{html,js}"],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui'),
  ],
}

