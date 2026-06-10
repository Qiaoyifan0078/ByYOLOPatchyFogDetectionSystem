<template>
  <section class="panel result">
    <header><h3>检测结果</h3><span v-if="result" class="tag">{{ result.count }} 个目标</span></header>
    <div v-if="!result" class="empty">暂无结果</div>
    <template v-else>
      <div v-if="hasFog" class="alert-bar">检测到大雾天气，请注意行车安全</div>
      <img v-if="mediaType!=='video'" :src="result.output_url" alt="检测结果">
      <video v-else ref="mediaVideo" :src="result.output_url" controls></video>
      <div class="stat-row"><div class="stat"><span>目标数</span><strong>{{ result.count }}</strong></div><div class="stat"><span>最高置信度</span><strong>{{ percent(result.confidence_max) }}</strong></div><div class="stat"><span>耗时</span><strong>{{ result.duration_ms }}ms</strong></div></div>
    </template>
  </section>
</template>
<script>
export default {name:"ResultPanel",props:{result:{type:Object,default:null},mediaType:{type:String,default:"image"}},computed:{hasFog(){return!!this.result&&Number(this.result.count||0)>0}},methods:{percent(v){return Math.round((Number(v)||0)*100)+"%"}}};
</script>
<style scoped>.result{padding:20px;min-height:420px}header{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:16px}h3{margin:0;font-size:17px}.empty{min-height:310px;border:2px dashed #e2e8f0;border-radius:10px;display:grid;place-items:center;color:#94a3b8;background:#f8fafc}.alert-bar{min-height:46px;display:flex;align-items:center;border:1px solid #f59e0b;border-left:4px solid #f59e0b;border-radius:8px;background:#fffbeb;color:#b45309;font-size:16px;font-weight:700;padding:0 15px;margin-bottom:14px}img,video{width:100%;max-height:560px;object-fit:contain;background:#0f172a;border-radius:8px;display:block}</style>