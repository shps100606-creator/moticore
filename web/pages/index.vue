<template>
  <main>
    <section class="hero">
      <h1>
        At the Core of All Motivation, There Lies Intention.<br>
        <span>萬象由動機而生，核心即是 Moticore</span>
      </h1>
      <p>
        我們創造了一個理論與系統，去理解、評估、發展與實務動機。<br>
        無論是人類、人工智慧，或是社會組織，皆由動機驅動。
      </p>
      <div class="hero-buttons">
        <NuxtLink to="/theory" class="btn">了解動機論 →</NuxtLink>
        <NuxtLink to="/assessment" class="btn">開始評估 →</NuxtLink>
        <NuxtLink to="/about" class="btn">了解我們 →</NuxtLink>
      </div>
    </section>

    <section class="posts" v-if="posts && posts.length">
      <h2>最新文章</h2>
      <div v-for="post in posts" :key="post._path" class="post-item">
        <h3><NuxtLink :to="post._path">{{ post.title }}</NuxtLink></h3>
        <p class="post-meta">{{ post.date }} · {{ post.author || 'moti' }}</p>
      </div>
    </section>
  </main>
</template>

<script setup>
const { data: posts } = await useAsyncData('posts', () =>
  queryContent('posts').sort({ date: -1 }).limit(5).find()
)
</script>
