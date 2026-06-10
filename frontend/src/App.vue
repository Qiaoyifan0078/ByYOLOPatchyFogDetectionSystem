<template>
  <div id="app" :class="{ 'theme-dark': view === 'dashboard' }">
    <login-page v-if="!user" @authenticated="onAuthenticated" />
    <main-layout v-else :user="user" :view="view" @navigate="navigate" @logout="logout">
      <dashboard v-if="view==='dashboard'" :user="user" />
      <component v-else :is="currentComponent" :key="view" :user="user" />
    </main-layout>
    <toast-notification @auth-expired="logout" />
  </div>
</template>
<script>
import LoginPage from "./pages/LoginPage.vue";import MainLayout from "./components/MainLayout.vue";import ToastNotification from "./components/ToastNotification.vue";import Dashboard from "./pages/Dashboard.vue";import ImageDetect from "./pages/ImageDetect.vue";import VideoDetect from "./pages/VideoDetect.vue";import CameraDetect from "./pages/CameraDetect.vue";import WarningList from "./pages/WarningList.vue";import HistoryPage from "./pages/HistoryPage.vue";import TrainingStats from "./pages/TrainingStats.vue";import UserManagement from "./pages/UserManagement.vue";
const views={dashboard:Dashboard,image:ImageDetect,video:VideoDetect,camera:CameraDetect,warnings:WarningList,history:HistoryPage,training:TrainingStats,users:UserManagement};
export default {name:"App",components:{LoginPage,MainLayout,ToastNotification,Dashboard},data(){return{user:null,view:"dashboard"}},computed:{currentComponent(){if(this.view==="users"&&(!this.user||this.user.role!=="admin"))return views.image;return views[this.view]||views.dashboard}},created(){const h=window.location.hash.replace("#/","");if(h)this.view=h;window.addEventListener("hashchange",this.syncHash);if(this.$api.getToken()){this.$api.get("/api/auth/me").then(d=>{this.user=d.user}).catch(()=>this.$api.setToken(""))}},beforeDestroy(){window.removeEventListener("hashchange",this.syncHash)},methods:{syncHash(){const n=window.location.hash.replace("#/","")||"dashboard";if(views[n])this.view=n},onAuthenticated({token,user}){this.$api.setToken(token);this.user=user;this.navigate("dashboard")},navigate(v){this.view=v;window.location.hash="#/"+v},logout(){this.$api.setToken("");this.user=null;window.location.hash=""}}};
</script>
<style>
:root{--ink:#1e293b;--muted:#64748b;--line:#e2e8f0;--page:#f1f5f9;--panel:#ffffff;--nav:#0f172a;--nav-soft:#1e293b;--primary:#0f766e;--primary-dark:#115e59;--accent:#d97706;--danger:#dc2626;--success:#16a34a;--shadow:0 8px 30px rgba(15,23,42,.08);--radius:10px;--radius-lg:14px;--transition:.2s cubic-bezier(.4,0,.2,1)}
*{box-sizing:border-box;margin:0}
html,body,#app{min-height:100vh}
body{background:var(--page);color:var(--ink);font-family:"Microsoft YaHei","PingFang SC","Inter",system-ui,sans-serif;font-size:14px;-webkit-font-smoothing:antialiased;letter-spacing:0}
button,input,select,textarea{font:inherit;color:inherit}
button{cursor:pointer}
a{color:var(--primary);text-decoration:none}
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:3px}
.theme-dark{--bg-deep:#060b14;--bg-surface:#0d1525;--bg-panel:#111b2e;--bg-card:#141f35;--bg-hover:#1a2844;--border:#1e3050;--border-light:#253a54;--text-primary:#e6edf8;--text-secondary:#8ca3be;--text-muted:#4a5d78;--accent-glow:rgba(6,182,212,.35);--accent-soft:rgba(6,182,212,.12)}
.page-head{display:flex;align-items:flex-start;justify-content:space-between;gap:18px;margin-bottom:24px}
.page-title{font-size:22px;font-weight:700;letter-spacing:-.3px}
.page-subtitle{margin-top:6px;color:var(--muted);font-size:13px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius-lg);box-shadow:var(--shadow)}
.field{display:grid;gap:7px;margin-bottom:16px}
.field label{color:#475569;font-size:13px;font-weight:600}
.input,.select{width:100%;min-height:42px;border:1px solid var(--line);border-radius:8px;background:#fff;padding:0 14px;outline:none;transition:var(--transition)}
.input:focus,.select:focus{border-color:var(--primary);box-shadow:0 0 0 3px rgba(15,118,110,.12)}
.input::placeholder{color:#94a3b8}
.select option{background:#fff}
.button{min-height:42px;padding:0 20px;border:1px solid transparent;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;gap:8px;background:var(--primary);color:#fff;font-weight:600;font-size:14px;transition:var(--transition)}
.button:hover{background:var(--primary-dark)}
.button:disabled{cursor:not-allowed;opacity:.45}
.button.secondary{background:transparent;border-color:var(--line);color:var(--ink)}
.button.secondary:hover{background:#f8fafc}
.button.danger{background:var(--danger)}
.button.danger:hover{background:#b91c1c}
.button.small{min-height:34px;padding:0 12px;font-size:13px}
.grid-two{display:grid;grid-template-columns:minmax(320px,430px) minmax(0,1fr);gap:20px}
.stat-row{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:16px}
.stat{border:1px solid var(--line);border-radius:10px;padding:16px;background:#f8fafc}
.stat span{display:block;color:var(--muted);font-size:12px;margin-bottom:6px}
.stat strong{font-size:22px;font-weight:700}
.error-text{color:var(--danger);min-height:20px;margin-top:10px;font-size:13px}
.success-text{color:var(--success);min-height:20px;margin-top:10px;font-weight:600}
.table-wrap{overflow-x:auto;background:var(--panel);border:1px solid var(--line);border-radius:var(--radius-lg)}
table{width:100%;border-collapse:collapse;min-width:760px}
th,td{padding:13px 14px;text-align:left;border-bottom:1px solid var(--line);vertical-align:middle}
th{color:var(--muted);background:#f8fafc;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.5px}
tr:last-child td{border-bottom:0}
tr:hover td{background:#f8fafc}
.tag{display:inline-flex;align-items:center;min-height:26px;border-radius:999px;padding:0 12px;background:#e6f4f1;color:var(--primary-dark);font-size:12px;font-weight:700}
.theme-dark .panel{background:var(--bg-panel);border-color:var(--border)}
.theme-dark .input,.theme-dark .select{background:var(--bg-surface);border-color:var(--border);color:var(--text-primary)}
.theme-dark .input:focus,.theme-dark .select:focus{border-color:#06b6d4;box-shadow:0 0 0 3px var(--accent-soft)}
.theme-dark .button.secondary{background:transparent;border-color:var(--border);color:var(--text-primary)}
.theme-dark .button.secondary:hover{background:var(--bg-hover)}
.theme-dark .stat{background:var(--bg-card);border-color:var(--border)}
.theme-dark .stat span{color:var(--text-secondary)}
.theme-dark .stat strong{color:var(--text-primary)}
.theme-dark .table-wrap{background:var(--bg-panel);border-color:var(--border)}
.theme-dark th{background:var(--bg-surface);color:var(--text-secondary)}
.theme-dark tr:hover td{background:var(--bg-hover)}
.theme-dark th,td{border-color:var(--border)}
.theme-dark body{background:var(--bg-deep);color:var(--text-primary)}
@media(max-width:980px){.grid-two{grid-template-columns:1fr}}
</style>