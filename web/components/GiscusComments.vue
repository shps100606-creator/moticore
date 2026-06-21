<template>
  <div ref="container" class="giscus"></div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const container = ref(null)

onMounted(() => {
  const script = document.createElement('script')
  script.src = 'https://giscus.app/client.js'
  script.setAttribute('data-repo', 'shps100606-creator/moticore')
  script.setAttribute('data-repo-id', 'PLACEHOLDER_REPO_ID')
  script.setAttribute('data-category', 'PLACEHOLDER_CATEGORY')
  script.setAttribute('data-category-id', 'PLACEHOLDER_CATEGORY_ID')
  script.setAttribute('data-mapping', 'pathname')
  script.setAttribute('data-strict', '0')
  script.setAttribute('data-reactions-enabled', '1')
  script.setAttribute('data-emit-metadata', '0')
  script.setAttribute('data-input-position', 'bottom')
  script.setAttribute('data-theme', 'light')
  script.setAttribute('data-lang', 'zh-TW')
  script.crossOrigin = 'anonymous'
  script.async = true
  if (container.value) {
    container.value.appendChild(script)
  }
})
</script>
