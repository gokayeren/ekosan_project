/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./app/templates/**/*.html",
    "./app/**/*.py"
  ],
  safelist: [
    "alert-info",
    "alert-success",
    "alert-warning",
    "alert-error"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["ui-sans-serif", "system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"]
      },
      colors: {
        "ekosan-dark": "#232e48",
        "ekosan-blue": "#1877F2"
      }
    }
  },
  daisyui: {
    themes: ["light"]
  },
  plugins: [
    require("daisyui")
  ]
};
