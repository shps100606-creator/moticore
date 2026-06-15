<template>
  <main class="posts">
    <h2>所有文章</h2>
    <div v-for="post in posts" :key="post._path" class="post-item">
      <h3><NuxtLink :to="post._path">{{ post.title }}</NuxtLink></h3>
      <p class="post-meta">{{ post.date }} · {{ post.author || 'moti' }}</p>
    </div>
    <p v-if="!posts?.length" style="color:#888">尚無文章。</p>
  </main>
</template>

<script setup>
const { data: posts } = await useAsyncData('all-posts', () =>
  queryContent('posts').sort({ date: -1 }).find()
)
</script>
