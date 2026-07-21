<template>
  <main class="status-page">
    <p>404</p>
    <h1>页面不存在</h1>
    <RouterLink to="/dashboard">返回展示看板</RouterLink>
  </main>
</template>

<style scoped>
.status-page {
  min-height: 100vh;
  display: grid;
  place-content: center;
  gap: 12px;
  text-align: center;
  color: #173f35;
}

p {
  margin: 0;
  color: #c76a32;
  font-size: 64px;
  font-weight: 800;
}

h1 {
  margin: 0;
}

a {
  color: #2f8066;
}
</style>
