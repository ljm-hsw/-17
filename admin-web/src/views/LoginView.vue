<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const submitting = ref(false)
const errorMessage = ref('')

function redirectTarget() {
  const target = route.query.redirect
  if (typeof target !== 'string' || !target.startsWith('/') || target.startsWith('//')) {
    return '/dashboard'
  }
  return target
}

async function submit() {
  if (submitting.value) return
  errorMessage.value = ''
  submitting.value = true
  try {
    await auth.login(username.value.trim(), password.value)
    await router.push(redirectTarget())
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '登录失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-brand" aria-labelledby="brand-title">
      <p class="eyebrow">TRAVELWEAVE · JIANG'AN</p>
      <h1 id="brand-title">让每一次抵达<br />都织成校园故事</h1>
      <p>游迹织梦连接点位、设备、卡片与真实游览数据，为江安校区文旅体验提供统一运营入口。</p>
    </section>

    <section class="login-panel" aria-labelledby="login-title">
      <div class="brand-mark" aria-hidden="true">游</div>
      <p class="panel-kicker">游迹织梦管理中心</p>
      <h2 id="login-title">欢迎回来</h2>
      <p class="panel-description">请使用团队管理员账号登录测试环境</p>

      <form @submit.prevent="submit">
        <label for="username">用户名</label>
        <input
          id="username"
          v-model="username"
          data-test="login-username"
          name="username"
          autocomplete="username"
          placeholder="请输入管理员用户名"
          required
        />

        <label for="password">密码</label>
        <input
          id="password"
          v-model="password"
          data-test="login-password"
          name="password"
          type="password"
          autocomplete="current-password"
          placeholder="请输入密码"
          required
        />

        <p v-if="errorMessage" class="form-error" role="alert">{{ errorMessage }}</p>
        <button data-test="login-submit" type="submit" :disabled="submitting">
          {{ submitting ? '正在登录…' : '登录管理中心' }}
        </button>
      </form>

      <p class="demo-note">本地测试账号与初始化方式请查看后台 README；演示账号无法用于生产环境。</p>
    </section>
  </main>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(420px, 0.9fr);
  background:
    radial-gradient(circle at 14% 18%, rgb(213 232 221 / 80%), transparent 34%),
    linear-gradient(145deg, #f7f1e6, #e7f0eb);
  color: #173f35;
}

.login-brand {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: clamp(48px, 8vw, 120px);
  background: linear-gradient(160deg, rgb(23 63 53 / 4%), rgb(23 63 53 / 12%));
}

.eyebrow,
.panel-kicker {
  color: #a56237;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.15em;
}

.login-brand h1 {
  max-width: 680px;
  margin: 18px 0;
  font-size: clamp(42px, 6vw, 78px);
  line-height: 1.08;
}

.login-brand p:last-child {
  max-width: 560px;
  color: #536c63;
  line-height: 1.8;
}

.login-panel {
  align-self: center;
  width: min(440px, calc(100% - 48px));
  margin: 24px auto;
  padding: 48px;
  border: 1px solid rgb(47 128 102 / 14%);
  border-radius: 24px;
  background: rgb(255 255 255 / 86%);
  box-shadow: 0 24px 70px rgb(30 66 53 / 14%);
  backdrop-filter: blur(16px);
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  border-radius: 14px;
  background: #2f8066;
  color: #fff8e9;
  font-family: serif;
  font-size: 22px;
  font-weight: 800;
}

.panel-kicker {
  margin: 20px 0 10px;
}

h2 {
  margin: 0;
  font-size: 34px;
}

.panel-description,
.demo-note {
  color: #60736c;
  font-size: 14px;
  line-height: 1.6;
}

form {
  display: grid;
  gap: 10px;
  margin-top: 28px;
}

label {
  margin-top: 8px;
  font-size: 14px;
  font-weight: 700;
}

input {
  min-height: 46px;
  padding: 0 14px;
  border: 1px solid #d5e0db;
  border-radius: 10px;
  background: #fff;
  color: #173f35;
  font: inherit;
}

input:focus-visible {
  border-color: #2f8066;
  outline: 3px solid rgb(47 128 102 / 16%);
}

button {
  min-height: 48px;
  margin-top: 16px;
  border: 0;
  border-radius: 10px;
  background: #2f8066;
  color: #fff;
  cursor: pointer;
  font: inherit;
  font-weight: 800;
}

button:disabled {
  cursor: wait;
  opacity: 0.65;
}

.form-error {
  margin: 6px 0 0;
  color: #a84432;
  font-size: 13px;
}

.demo-note {
  margin: 24px 0 0;
  padding-top: 18px;
  border-top: 1px solid #e5ebe7;
  font-size: 12px;
}

@media (max-width: 900px) {
  .login-page {
    grid-template-columns: 1fr;
  }

  .login-brand {
    display: none;
  }
}

@media (max-width: 480px) {
  .login-panel {
    width: calc(100% - 28px);
    padding: 34px 24px;
  }
}
</style>
