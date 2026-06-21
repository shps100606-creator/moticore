<template>
  <main class="article">
    <template v-if="post">
      <h1>{{ post.title }}</h1>
      <p class="meta">{{ post.date }} · {{ post.author || 'moti' }}</p>
      <div class="article-body">
        <ContentRenderer :value="post" />
      </div>
      <GiscusComments />
    </template>
  </main>
</template>

<script setup>
const route = useRoute()
const { data: post } = await useAsyncData(route.path, () =>
  queryContent(route.path).findOne()
)
</script>
