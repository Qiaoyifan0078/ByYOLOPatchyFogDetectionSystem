<template>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand"><div class="brand-mark"><span>YV8</span></div><div><strong>团雾识别检测系统</strong><span>YOLOv8 Platform</span></div></div>
      <nav class="nav">
        <section class="nav-group"><p>检测任务</p>
          <button :class="{active:view==='dashboard'}" @click="$emit('navigate','dashboard')"><icon-glyph name="dashboard"/>可视化大屏</button>
          <button :class="{active:view==='image'}" @click="$emit('navigate','image')"><icon-glyph name="image"/>图片识别</button>
          <button :class="{active:view==='video'}" @click="$emit('navigate','video')"><icon-glyph name="video"/>视频识别</button>
          <button :class="{active:view==='camera'}" @click="$emit('navigate','camera')"><icon-glyph name="camera"/>摄像头识别</button>
        </section>
        <section class="nav-group"><p>记录管理</p>
          <button :class="{active:view==='warnings'}" @click="$emit('navigate','warnings')"><icon-glyph name="warning"/>预警提示</button>
          <button :class="{active:view==='history'}" @click="$emit('navigate','history')"><icon-glyph name="history"/>历史识别</button>
        </section>
        <section class="nav-group"><p>模型分析</p>
          <button :class="{active:view==='training'}" @click="$emit('navigate','training')"><icon-glyph name="stats"/>训练统计</button>
        </section>
        <section v-if="user.role==='admin'" class="nav-group"><p>系统管理</p>
          <button :class="{active:view==='users'}" @click="$emit('navigate','users')"><icon-glyph name="users"/>用户管理</button>
        </section>
      </nav>
      <div class="sidebar-footer"><div class="status-dot"></div><span>系统运行中</span></div>
    </aside>
    <main class="workspace">
      <header class="topbar">
        <span class="breadcrumb">团雾检测 / {{ viewName }}</span>
        <div class="topbar-right"><span class="role-badge">{{ user.role==='admin'?'管理员':'检测员' }}</span><strong>{{ user.full_name||user.username }}</strong><button class="btn-logout" @click="$emit('logout')"><icon-glyph name="logout"/></button></div>
      </header>
      <section class="content"><slot/></section>
    </main>
  </div>
</template>
<script>
import IconGlyph from "./IconGlyph.vue";
export default {name:"MainLayout",components:{IconGlyph},props:{user:{type:Object,required:true},view:{type:String,required:true}},computed:{viewName(){const m={dashboard:"可视化大屏",image:"图片识别",video:"视频识别",camera:"摄像头识别",warnings:"预警提示",history:"历史识别",training:"训练统计",users:"用户管理"};return m[this.view]||this.view}}};
</script>
<style scoped>
.shell{min-height:100vh;display:grid;grid-template-columns:240px minmax(0,1fr)}
.sidebar{background:#0f172a;border-right:1px solid #1e293b;padding:20px 14px;position:sticky;top:0;height:100vh;display:flex;flex-direction:column}
.brand{display:flex;align-items:center;gap:12px;padding:2px 4px 22px}
.brand-mark{width:40px;height:40px;border-radius:10px;background:linear-gradient(135deg,#0f766e,#14b8a6);display:grid;place-items:center;box-shadow:0 0 14px rgba(15,118,110,.3)}
.brand-mark span{color:#fff;font-size:11px;font-weight:800}
.brand strong{display:block;font-size:15px;color:#fff;line-height:1.2}
.brand span{color:#64748b;font-size:11px}
.nav{display:grid;gap:18px;flex:1}
.nav-group p{margin:0 0 8px 12px;color:#475569;font-size:10px;font-weight:700;letter-spacing:1.2px}
.nav button{width:100%;min-height:40px;border:0;border-radius:8px;margin-bottom:2px;padding:0 12px;display:flex;align-items:center;gap:10px;background:transparent;color:#94a3b8;text-align:left;font-size:14px;transition:.2s ease}
.nav button:hover{background:#1e293b;color:#e2e8f0}
.nav button.active{background:rgba(15,118,110,.15);color:#14b8a6;box-shadow:inset 3px 0 0 #14b8a6}
.sidebar-footer{padding:16px 12px;border-top:1px solid #1e293b;display:flex;align-items:center;gap:8px;color:#64748b;font-size:12px}
.status-dot{width:8px;height:8px;border-radius:50%;background:#22c55e;box-shadow:0 0 8px rgba(34,197,94,.5);animation:pulse-glow 2s ease-in-out infinite}
@keyframes pulse-glow{0%,100%{box-shadow:0 0 8px rgba(34,197,94,.5)}50%{box-shadow:0 0 16px rgba(34,197,94,.8)}}
.workspace{min-width:0}
.topbar{height:56px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;background:rgba(255,255,255,.92);border-bottom:1px solid #e2e8f0;backdrop-filter:blur(16px);position:sticky;top:0;z-index:10}
.breadcrumb{color:#94a3b8;font-size:12px}
.topbar-right{display:flex;align-items:center;gap:14px}
.role-badge{display:inline-flex;align-items:center;min-height:24px;border-radius:999px;padding:0 10px;background:#e6f4f1;color:#0f766e;font-size:11px;font-weight:700;letter-spacing:.5px}
.topbar-right strong{font-size:14px;font-weight:600}
.btn-logout{width:36px;height:36px;border:1px solid #e2e8f0;border-radius:8px;background:transparent;display:grid;place-items:center;color:#64748b;transition:.2s}
.btn-logout:hover{background:#fef2f2;color:#dc2626;border-color:#dc2626}
.content{padding:26px}
@media(max-width:860px){.shell{grid-template-columns:1fr}.sidebar{position:relative;height:auto}}
</style>