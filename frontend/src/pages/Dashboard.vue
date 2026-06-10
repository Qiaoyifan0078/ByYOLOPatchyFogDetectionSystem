<template>
  <div class="dashboard">
    <div class="dash-header">
      <div><h1 class="dash-title">团雾监测可视化大屏</h1><p class="dash-sub">实时道路团雾检测与预警系统</p></div>
      <div class="dash-controls">
        <div class="live-indicator"><span class="live-dot"></span>实时</div>
        <select v-model="timeRange" class="select" @change="loadData"><option value="today">今日</option><option value="week">本周</option><option value="month">本月</option><option value="all">全部</option></select>
        <button class="button secondary" @click="refreshData" :disabled="loading">{{ loading?'刷新中...':'刷新' }}</button>
      </div>
    </div>
    <div class="stats-grid">
      <div class="stat-card card-cyan"><div class="card-icon"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg></div><div class="card-body"><span class="card-label">预警总数</span><strong class="card-value">{{ stats.totalWarnings }}</strong></div><div class="card-glow"></div></div>
      <div class="stat-card card-rose"><div class="card-icon"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg></div><div class="card-body"><span class="card-label">重度预警</span><strong class="card-value">{{ stats.severeWarnings }}</strong></div><div class="card-glow"></div></div>
      <div class="stat-card card-emerald"><div class="card-icon"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/></svg></div><div class="card-body"><span class="card-label">图片识别</span><strong class="card-value">{{ stats.imageDetections }}</strong></div><div class="card-glow"></div></div>
      <div class="stat-card card-amber"><div class="card-icon"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg></div><div class="card-body"><span class="card-label">视频识别</span><strong class="card-value">{{ stats.videoDetections }}</strong></div><div class="card-glow"></div></div>
    </div>
    <div class="content-grid">
      <div class="panel recent-warnings"><h2 class="panel-title">最新预警</h2>
        <div class="warning-list">
          <div v-for="item in recentWarnings" :key="item.id" class="warning-item">
            <div class="warning-image" v-if="item.snapshot_url"><img v-if="isImage(item.snapshot_url)" :src="item.snapshot_url" alt="截图" @error="onImgError"/><video v-else-if="isVideo(item.snapshot_url)" :src="item.snapshot_url" muted preload="metadata"></video><span v-else class="no-media">无预览</span></div>
            <div class="warning-details"><div class="warning-head"><span class="warning-road">{{ item.road_section }}</span><span :class="['warn-badge',levelClass(item.fog_level)]">{{ item.fog_level }}</span></div><div class="warning-info"><span>能见度: {{ item.visibility_level }}</span><span>限速: {{ item.speed_limit }}</span></div><div class="warning-time">{{ formatTime(item.created_at) }}</div></div>
          </div>
          <div v-if="!recentWarnings.length" class="empty">暂无预警</div>
        </div>
      </div>
      <div class="panel fog-dist"><h2 class="panel-title">团雾等级分布</h2>
        <div class="chart-area">
          <div v-for="(count,level) in fogLevelStats" :key="level" class="chart-row"><span class="bar-label">{{ level }}</span><div class="bar-track"><div class="bar-fill" :style="{width:getBarWidth(count)+'%',background:getLevelColor(level)}"></div></div><span class="bar-num">{{ count }}</span></div>
          <div v-if="!Object.keys(fogLevelStats).length" class="empty">暂无数据</div>
        </div>
      </div>
    </div>
    <div class="panel timeline-panel"><h2 class="panel-title">识别时间线</h2>
      <div class="timeline">
        <div v-for="item in timelineItems" :key="item.id" class="tl-item"><div class="tl-dot"></div><div class="tl-body"><div class="tl-head"><span class="tl-type">{{ typeName(item.source_type) }}</span><span class="tl-count">{{ item.detect_count }} 个目标</span></div><div class="tl-meta"><span>{{ item.original_name }}</span><span>{{ formatTime(item.created_at) }}</span></div></div></div>
        <div v-if="!timelineItems.length" class="empty">暂无记录</div>
      </div>
    </div>
  </div>
</template>
<script>
export default { name:"Dashboard", props:{user:{type:Object,required:true}}, data(){return{timeRange:"today",loading:false,stats:{totalWarnings:0,severeWarnings:0,imageDetections:0,videoDetections:0},recentWarnings:[],fogLevelStats:{},timelineItems:[]}}, created(){this.loadData();this._t=setInterval(()=>this.loadData(),30000)}, beforeDestroy(){clearInterval(this._t)}, methods:{async loadData(){this.loading=true;try{await Promise.all([this.loadWarnings(),this.loadDetections()])}finally{this.loading=false}},async loadWarnings(){const d=await this.$api.get("/api/warnings");this.recentWarnings=(d.items||[]).slice(0,8);this.stats.totalWarnings=(d.items||[]).length;this.stats.severeWarnings=(d.items||[]).filter(i=>/重度|特重/.test(i.fog_level)).length;const s={};(d.items||[]).forEach(i=>{s[i.fog_level]=(s[i.fog_level]||0)+1});this.fogLevelStats=s},async loadDetections(){const d=await this.$api.get("/api/detections");const items=this.filterByTime(d.items||[]);this.stats.imageDetections=items.filter(i=>i.source_type==='image').length;this.stats.videoDetections=items.filter(i=>i.source_type==='video').length;this.timelineItems=items.slice(0,15)},getBarWidth(c){const mx=Math.max(...Object.values(this.fogLevelStats),1);return(c/mx)*100},getLevelColor(l){if(/特重/.test(l))return'#ef4444';if(/重度/.test(l))return'#f59e0b';if(/中度/.test(l))return'#06b6d4';return'#10b981'},levelClass(l){if(/特重/.test(l))return'crit';if(/重度/.test(l))return'high';if(/中度/.test(l))return'med';return'low'},typeName(t){return{image:'图片',video:'视频',camera:'摄像头'}[t]||t},formatTime(t){if(!t)return'-';const d=new Date(t),n=new Date(),df=n-d;if(df<6e4)return'刚刚';if(df<36e5)return Math.floor(df/6e4)+'分钟前';if(df<864e5)return Math.floor(df/36e5)+'小时前';return t.replace('T',' ').substring(0,16)},isImage(url){return /\.(jpg|jpeg|png|bmp|webp)$/i.test(url)},isVideo(url){return /\.(mp4|webm|avi|mov|mkv)$/i.test(url)},onImgError(e){e.target.style.display="none"},refreshData(){this.loadData()}}};
</script>
<style scoped>
.dashboard{min-height:100vh;background:#060b14;padding:0}
.dash-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:28px}
.dash-title{font-size:28px;font-weight:700;background:linear-gradient(135deg,#06b6d4,#10b981);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.dash-sub{margin-top:4px;color:#4a5d78;font-size:13px}
.dash-controls{display:flex;align-items:center;gap:12px}
.live-indicator{display:flex;align-items:center;gap:6px;color:#10b981;font-size:12px;font-weight:700;letter-spacing:.8px}
.live-dot{width:8px;height:8px;border-radius:50%;background:#10b981;box-shadow:0 0 10px rgba(16,185,129,.6);animation:pulse-glow 2s ease-in-out infinite}
@keyframes pulse-glow{0%,100%{box-shadow:0 0 4px rgba(6,182,212,.35)}50%{box-shadow:0 0 18px rgba(6,182,212,.35)}}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px}
.stat-card{background:#111b2e;border:1px solid #1e3050;border-radius:14px;padding:22px;display:flex;align-items:center;gap:16px;position:relative;overflow:hidden;transition:.25s ease}
.stat-card:hover{transform:translateY(-2px)}
.card-icon{width:52px;height:52px;border-radius:12px;display:grid;place-items:center;flex-shrink:0}
.card-cyan .card-icon{background:rgba(6,182,212,.15);color:#06b6d4}
.card-rose .card-icon{background:rgba(244,63,94,.15);color:#f43f5e}
.card-emerald .card-icon{background:rgba(16,185,129,.15);color:#10b981}
.card-amber .card-icon{background:rgba(245,158,11,.15);color:#f59e0b}
.card-glow{position:absolute;top:-20px;right:-20px;width:80px;height:80px;border-radius:50%;opacity:.08}
.card-cyan .card-glow{background:#06b6d4}
.card-rose .card-glow{background:#f43f5e}
.card-emerald .card-glow{background:#10b981}
.card-amber .card-glow{background:#f59e0b}
.card-label{display:block;color:#4a5d78;font-size:11px;margin-bottom:4px;text-transform:uppercase;letter-spacing:.5px}
.card-value{font-size:30px;font-weight:700;color:#e6edf8}
.content-grid{display:grid;grid-template-columns:2fr 1fr;gap:20px;margin-bottom:20px}
.panel{padding:22px;background:#111b2e;border:1px solid #1e3050;border-radius:14px;box-shadow:0 4px 24px rgba(0,0,0,.3)}
.panel-title{font-size:16px;font-weight:700;margin-bottom:18px;color:#e6edf8}
.warning-list{display:grid;gap:12px;max-height:380px;overflow-y:auto}
.warning-item{display:flex;gap:14px;padding:14px;background:#0d1525;border-radius:10px;border:1px solid #1e3050;transition:.2s}
.warning-item:hover{background:#141f35;border-color:#253a54}
.warning-image{width:100px;height:70px;border-radius:6px;overflow:hidden;flex-shrink:0;background:#0a0f1c}
.warning-image img{width:100%;height:100%;object-fit:cover}
.warning-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
.warning-road{font-weight:700;font-size:14px;color:#e6edf8}
.warn-badge{display:inline-flex;align-items:center;min-height:22px;border-radius:999px;padding:0 10px;font-size:11px;font-weight:700}
.warn-badge.low{color:#10b981;background:rgba(16,185,129,.15)}
.warn-badge.med{color:#06b6d4;background:rgba(6,182,212,.15)}
.warn-badge.high{color:#f59e0b;background:rgba(245,158,11,.15)}
.warn-badge.crit{color:#ef4444;background:rgba(239,68,68,.15)}
.warning-info{display:flex;gap:14px;color:#4a5d78;font-size:12px;margin-bottom:4px}
.warning-time{color:#4a5d78;font-size:11px}
.chart-area{display:grid;gap:10px}
.chart-row{display:grid;grid-template-columns:90px 1fr 40px;gap:10px;align-items:center}
.bar-label{font-size:13px;color:#8ca3be;text-align:right}
.bar-track{background:#0d1525;border-radius:6px;height:26px;overflow:hidden}
.bar-fill{height:100%;border-radius:6px;transition:width .5s ease;min-width:3px}
.bar-num{font-size:14px;font-weight:700;color:#e6edf8;text-align:right}
.timeline{display:grid;gap:0;padding-left:20px}
.tl-item{position:relative;padding-bottom:20px}
.tl-item::before{content:'';position:absolute;left:-20px;top:20px;bottom:0;width:2px;background:#1e3050}
.tl-dot{position:absolute;left:-25px;top:4px;width:10px;height:10px;border-radius:50%;background:#06b6d4;border:2px solid #111b2e;box-shadow:0 0 8px rgba(6,182,212,.5)}
.tl-body{padding:14px;background:#0d1525;border-radius:10px;border:1px solid #1e3050}
.tl-head{display:flex;justify-content:space-between;margin-bottom:6px}
.tl-type{font-weight:700;font-size:14px;color:#e6edf8}
.tl-count{color:#8ca3be;font-size:12px}
.tl-meta{display:flex;justify-content:space-between;color:#4a5d78;font-size:12px}
.empty{text-align:center;padding:32px;color:#4a5d78;font-size:13px}
@media(max-width:1200px){.stats-grid{grid-template-columns:repeat(2,1fr)}.content-grid{grid-template-columns:1fr}}
@media(max-width:768px){.stats-grid{grid-template-columns:1fr}}
</style>
