<template>
  <div>
    <div class="page-head"><div><h2 class="page-title">训练统计</h2><p class="page-subtitle">YOLOv8 模型训练结果分析</p></div></div>
    <div class="charts-grid"><div v-for="item in charts" :key="item.filename" class="panel chart-card"><h3>{{ item.title }}</h3><img :src="item.url" :alt="item.title"></div><div v-if="!charts.length" class="empty-cell">暂无训练数据，请先完成模型训练</div></div><p class="error-text">{{ error }}</p>
  </div>
</template>
<script>export default {name:"TrainingStats",data(){return{charts:[],error:""}},created(){this.load()},methods:{async load(){this.error="";try{const d=await this.$api.get("/api/training/stats");this.charts=d.items||[]}catch(e){this.error=e.message}}}};</script>
<style scoped>.charts-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:20px}.chart-card{padding:20px;text-align:center}.chart-card h3{font-size:15px;color:#64748b;margin-bottom:14px}.chart-card img{width:100%;max-height:340px;object-fit:contain;border-radius:6px;background:#f8fafc}.empty-cell{text-align:center;color:#94a3b8;padding:40px;grid-column:1/-1}</style>