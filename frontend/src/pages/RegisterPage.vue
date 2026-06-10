
<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <div class="logo"></div>
        <h1>团雾识别检测系统</h1>
        <p>用户注册</p>
      </div>

      <form @submit.prevent="handleRegister" class="register-form">
        <div class="field">
          <label>用户名</label>
          <input v-model="form.username" type="text" placeholder="请输入用户名（至少3个字符）" class="input" required />
        </div>

        <div class="field">
          <label>姓名</label>
          <input v-model="form.full_name" type="text" placeholder="请输入姓名" class="input" />
        </div>

        <div class="field">
          <label>密码</label>
          <input v-model="form.password" type="password" placeholder="请输入密码（至少6个字符）" class="input" required />
        </div>

        <div class="field">
          <label>确认密码</label>
          <input v-model="form.confirm_password" type="password" placeholder="请再次输入密码" class="input" required />
        </div>

        <button type="submit" class="button register-btn" :disabled="loading">
          {{ loading ? '注册中...' : '立即注册' }}
        </button>

        <div class="error-text" v-if="error">{{ error }}</div>

        <div class="register-footer">
          <span>已有账号？</span>
          <a href="#" @click.prevent="goToLogin">立即登录</a>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: "RegisterPage",
  data() {
    return {
      form: {
        username: "",
        full_name: "",
        password: "",
        confirm_password: ""
      },
      loading: false,
      error: ""
    };
  },
  methods: {
    async handleRegister() {
      this.error = "";

      if (this.form.username.length < 3) {
        this.error = "用户名至少需要3个字符";
        return;
      }

      if (this.form.password.length < 6) {
        this.error = "密码至少需要6个字符";
        return;
      }

      if (this.form.password !== this.form.confirm_password) {
        this.error = "两次输入的密码不一致";
        return;
      }

      this.loading = true;
      try {
        const response = await this.$api.post("/api/auth/register", {
          username: this.form.username,
          password: this.form.password,
          full_name: this.form.full_name
        });

        this.$emit("authenticated", {
          token: response.token,
          user: response.user
        });
      } catch (err) {
        this.error = err.message || "注册失败，请稍后重试";
      } finally {
        this.loading = false;
      }
    },
    goToLogin() {
      this.$emit("show-login");
    }
  }
};
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;
  width: 100%;
  max-width: 420px;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo {
  width: 60px;
  height: 60px;
  margin: 0 auto 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, #d7a741 0%, #d7a741 34%, transparent 34%),
              linear-gradient(135deg, #1aa38f 0%, #1aa38f 100%);
}

.register-header h1 {
  margin: 0 0 8px;
  font-size: 24px;
  color: var(--ink);
}

.register-header p {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
}

.register-form {
  display: grid;
  gap: 16px;
}

.field label {
  display: block;
  margin-bottom: 6px;
  color: #354255;
  font-weight: 650;
  font-size: 14px;
}

.input {
  width: 100%;
  min-height: 42px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: #fff;
  color: var(--ink);
  padding: 0 12px;
  outline: none;
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}

.input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.15);
}

.register-btn {
  width: 100%;
  min-height: 46px;
  margin-top: 8px;
  font-size: 16px;
  font-weight: 700;
}

.error-text {
  color: var(--danger);
  min-height: 20px;
  margin: 0;
  text-align: center;
  font-size: 14px;
}

.register-footer {
  text-align: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 14px;
}

.register-footer a {
  color: var(--primary);
  font-weight: 700;
  text-decoration: none;
  margin-left: 6px;
}

.register-footer a:hover {
  text-decoration: underline;
}
</style>
