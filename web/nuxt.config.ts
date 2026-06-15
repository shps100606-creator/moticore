export default defineNuxtConfig({
  modules: ['@nuxt/content'],
  css: ['~/assets/main.css'],
  content: {
    highlight: {
      theme: 'github-light',
    },
  },
})
