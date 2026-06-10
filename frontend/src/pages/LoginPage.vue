<template>
  <main class="auth-page">
    <div class="auth-bg"><div class="bg-shape shape-1"></div><div class="bg-shape shape-2"></div></div>
    <section class="auth-card">
      <div class="auth-header"><div class="auth-mark"><span>YV8</span></div><div><h1>团雾识别检测系统</h1><p>YOLOv8 智能监测平台</p></div></div>
      <form @submit.prevent="submit">
        <div class="field"><label>用户名</label><input v-model.trim="form.username" class="input" autocomplete="username" placeholder="请输入用户名"></div>
        <div v-if="mode==='register'" class="field"><label>姓名</label><input v-model.trim="form.full_name" class="input" placeholder="请输入姓名"></div>
        <div class="field"><label>密码</label><input v-model="form.password" class="input" type="password" autocomplete="current-password" placeholder="请输入密码"></div>
        <button class="button auth-btn" type="submit" :disabled="loading">{{ loading?'处理中...':mode==='login'?'登 录':'注 册' }}</button>
      </form>
      <p class="error-text">{{ error }}</p>
      <button class="switch-link" type="button" @click="toggleMode">{{ mode==='login'?'创建新账号':'返回登录' }}</button>
    </section>
  </main>
</template>
<script>
export default { name:"LoginPage", data(){return{mode:"login",loading:false,error:"",form:{username:"",full_name:"",password:""}}}, methods:{toggleMode(){this.mode=this.mode==="login"?"register":"login";this.error=""},async submit(){this.loading=true;this.error="";try{const ep=this.mode==="login"?"/api/auth/login":"/api/auth/register";const data=await this.$api.post(ep,this.form);this.$emit("authenticated",data)}catch(e){this.error=e.message}finally{this.loading=false}}}};
</script>
<style scoped>
.auth-page{min-height:100vh;display:grid;place-items:center;padding:24px;position:relative;overflow:hidden;background:#f1f5f9}
.auth-bg{position:absolute;inset:0}
.bg-shape{position:absolute;border-radius:50%;opacity:.06}
.shape-1{top:-120px;right:-80px;width:500px;height:500px;background:#0f766e}
.shape-2{bottom:-100px;left:-60px;width:400px;height:400px;background:#d97706}
.auth-card{width:min(440px,100%);padding:36px;background:#fff;border:1px solid #e2e8f0;border-radius:16px;box-shadow:0 20px 60px rgba(15,23,42,.1);position:relative;z-index:1}
.auth-header{display:flex;align-items:center;gap:14px;margin-bottom:32px}
.auth-mark{width:48px;height:48px;border-radius:12px;background:linear-gradient(135deg,#0f766e,#14b8a6);display:grid;place-items:center;box-shadow:0 4px 14px rgba(15,118,110,.25)}
.auth-mark span{color:#fff;font-size:13px;font-weight:800}
h1{font-size:22px;font-weight:700;color:#1e293b;margin:0}
p{color:#64748b;margin:4px 0 0;font-size:13px}
.auth-btn{width:100%;margin-top:4px}
.switch-link{display:block;margin-top:14px;border:0;background:transparent;color:#0f766e;font-size:13px;font-weight:600;padding:0;cursor:pointer}
.switch-link:hover{color:#115e59}
</style>