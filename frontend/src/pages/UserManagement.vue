<template>
  <div>
    <div class="page-head"><div><h2 class="page-title">用户管理</h2><p class="page-subtitle">账号、角色与状态配置</p></div><button class="button secondary" @click="load">刷新列表</button></div>
    <div class="table-wrap"><table><thead><tr><th>用户名</th><th>姓名</th><th>角色</th><th>状态</th><th>创建时间</th><th>最后登录</th><th>操作</th></tr></thead>
    <tbody><tr v-for="item in items" :key="item.id"><td>{{ item.username }}</td><td>{{ item.full_name }}</td><td><select v-model="item.role" class="select compact"><option value="admin">管理员</option><option value="user">检测员</option></select></td><td><select v-model="item.status" class="select compact"><option value="active">启用</option><option value="disabled">禁用</option></select></td><td>{{ item.created_at }}</td><td>{{ item.last_login||'-' }}</td><td><button class="button secondary small" @click="save(item)">保存</button><button class="button danger small" @click="remove(item.id)">删除</button></td></tr>
    <tr v-if="!items.length"><td colspan="7" class="empty-cell">暂无用户数据</td></tr></tbody></table></div>
    <p class="error-text">{{ error }}</p>
  </div>
</template>
<script>export default {name:"UserManagement",props:{user:{type:Object,required:true}},data(){return{items:[],error:""}},created(){this.load()},methods:{async load(){this.error="";try{const d=await this.$api.get("/api/users");this.items=(d.items||[]).map(i=>({...i}))}catch(e){this.error=e.message}},async save(item){this.error="";try{await this.$api.put("/api/users/"+item.id,{role:item.role,status:item.status,full_name:item.full_name,phone:item.phone||""})}catch(e){this.error=e.message}},async remove(id){this.error="";if(!confirm("确认删除该用户？此操作不可撤销。"))return;try{await this.$api.delete("/api/users/"+id);this.items=this.items.filter(i=>i.id!==id)}catch(e){this.error=e.message}}}};</script>
<style scoped>.compact{width:120px}.empty-cell{text-align:center;color:#94a3b8;padding:40px}</style>