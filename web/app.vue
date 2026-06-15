<template>
  <div>
    <nav class="nav">
      <NuxtLink to="/" class="nav-logo">moticore</NuxtLink>
      <div class="nav-links">
        <NuxtLink to="/posts">文章</NuxtLink>
        <NuxtLink to="/about">了解我們</NuxtLink>
      </div>
    </nav>
    <slot />
    <footer>
      <p>© {{ new Date().getFullYear() }} Moticore · 萬象由動機而生</p>
    </footer>
  </div>
</template>
