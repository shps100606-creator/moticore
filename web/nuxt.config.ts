export default defineNuxtConfig({
  modules: ['@nuxt/content'],
  css: ['~/assets/main.css'],
  content: {
    highlight: {
      theme: 'github-light',
    },
  },
  app: {
    head: {
      title: 'Moticore',
      meta: [
        { name: 'description', content: '萬象由動機而生，核心即是 Moticore' }
      ]
    }
  }
})
