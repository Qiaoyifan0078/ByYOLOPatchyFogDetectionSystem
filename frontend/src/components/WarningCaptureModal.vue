<template>
  <div v-if="visible" class="modal-overlay" @click.self="close">
    <section class="modal-card" role="dialog" aria-modal="true">
      <header class="modal-head"><div><span class="src-pill">{{ typeName(sourceType) }}</span><h3>发布预警</h3></div><button class="btn-close" @click="close">&times;</button></header>

      <div class="meta-row">
        <div class="meta-item"><span>检测目标</span><strong>{{ result?result.count:0 }}</strong></div>
        <div class="meta-item"><span>最高置信度</span><strong>{{ percent(result&&result.confidence_max) }}</strong></div>
        <div class="meta-item"><span>记录编号</span><strong>{{ result&&result.id?result.id:'-' }}</strong></div>
      </div>

      <!-- 自动分析结果提示 -->
      <div class="auto-banner">
        <span class="auto-icon">&#9881;</span>
        <span>系统根据检测数据自动分析：<strong>{{ autoGrade.fog }}</strong>，能见度 <strong>{{ autoGrade.visibility }}</strong>，建议 <strong>{{ autoGrade.speed }}</strong></span>
      </div>

      <form @submit.prevent="submit">
        <div class="field"><label>路段信息 <span class="required">*</span></label><input v-model.trim="form.road_section" class="input" maxlength="200" placeholder="如: G60 沪昆高速 K118+300"></div>
        <div class="form-row">
          <div class="field">
            <label>团雾等级 <span class="auto-tag">自动</span></label>
            <select v-model="form.fog_level" class="select"><option v-for="o in fogOptions" :key="o" :value="o">{{ o }}</option></select>
          </div>
          <div class="field">
            <label>能见度级别 <span class="auto-tag">自动</span></label>
            <select v-model="form.visibility_level" class="select"><option v-for="o in visOptions" :key="o" :value="o">{{ o }}</option></select>
          </div>
        </div>
        <div class="field">
          <label>限速信息 <span class="auto-tag">自动</span></label>
          <input v-model.trim="form.speed_limit" class="input" maxlength="60" placeholder="如: 限速 60 km/h">
        </div>
        <p class="error-text">{{ error }}</p>
        <footer class="modal-actions">
          <button type="button" class="button secondary" @click="close">取消</button>
          <button type="submit" class="button" :disabled="saving">{{ saving?'发布中...':'确认发布预警' }}</button>
        </footer>
      </form>
    </section>
  </div>
</template>

<script>
export default {
  name: "WarningCaptureModal",
  props: {
    visible: { type: Boolean, default: false },
    sourceType: { type: String, default: "image" },
    result: { type: Object, default: null }
  },
  data() {
    return {
      saving: false,
      error: "",
      form: { road_section: "", fog_level: "中度团雾", visibility_level: "200-500米", speed_limit: "" },
      fogOptions: ["轻度团雾", "中度团雾", "重度团雾", "特重团雾"],
      visOptions: ["500米以上", "200-500米", "50-200米", "50米以下"]
    };
  },
  computed: {
    autoGrade() {
      if (!this.result) return { fog: "-", visibility: "-", speed: "-" };
      const count = Number(this.result.count || 0);
      const maxConf = Number(this.result.confidence_max || 0);

      let fog, visibility, speed;

      if (count >= 10 && maxConf >= 0.7) {
        fog = "特重团雾"; visibility = "50米以下"; speed = "限速 20 km/h，建议封路";
      } else if (count >= 5 && maxConf >= 0.5) {
        fog = "重度团雾"; visibility = "50-200米"; speed = "限速 40 km/h";
      } else if (count >= 2 && maxConf >= 0.3) {
        fog = "中度团雾"; visibility = "200-500米"; speed = "限速 60 km/h";
      } else if (count >= 1) {
        fog = "轻度团雾"; visibility = "500米以上"; speed = "限速 80 km/h";
      } else {
        fog = "轻度团雾"; visibility = "500米以上"; speed = "限速 80 km/h";
      }

      return { fog, visibility, speed };
    }
  },
  watch: {
    visible(next) {
      if (next) this.reset();
    }
  },
  methods: {
    reset() {
      this.error = "";
      this.saving = false;
      // 自动填充检测数据
      if (this.result && this.result.count > 0) {
        const g = this.autoGrade;
        this.form = {
          road_section: "",
          fog_level: g.fog,
          visibility_level: g.visibility,
          speed_limit: g.speed
        };
      } else {
        this.form = {
          road_section: "",
          fog_level: "中度团雾",
          visibility_level: "200-500米",
          speed_limit: ""
        };
      }
    },
    close() {
      if (!this.saving) this.$emit("close");
    },
    async submit() {
      if (!this.form.road_section || !this.form.fog_level || !this.form.visibility_level || !this.form.speed_limit) {
        this.error = "请完整填写预警信息";
        return;
      }
      this.saving = true;
      this.error = "";
      try {
        const data = await this.$api.post("/api/warnings", {
          ...this.form,
          source_type: this.sourceType,
          detection_id: this.result && this.result.id,
          snapshot_url: this.result && this.result.output_url
        });
        this.$emit("saved", data.item);
        this.$emit("close");
      } catch (e) {
        this.error = e.message;
      } finally {
        this.saving = false;
      }
    },
    typeName(t) {
      return { image: "图片识别", video: "视频识别", camera: "摄像头识别" }[t] || t;
    },
    percent(v) {
      return Math.round((Number(v) || 0) * 100) + "%";
    }
  }
};
</script>

<style scoped>
.modal-overlay{position:fixed;inset:0;z-index:100;display:grid;place-items:center;padding:22px;background:rgba(15,23,42,.6);backdrop-filter:blur(4px)}
.modal-card{width:min(560px,100%);max-height:calc(100vh-44px);overflow-y:auto;border-radius:14px;border:1px solid #e2e8f0;background:#fff;box-shadow:0 28px 70px rgba(15,23,42,.2);padding:24px}
.modal-head{display:flex;align-items:flex-start;justify-content:space-between;gap:14px;margin-bottom:16px}
.src-pill{display:inline-flex;align-items:center;min-height:24px;border-radius:999px;padding:0 10px;background:#fef3c7;color:#92400e;font-size:11px;font-weight:700}
h3{margin:8px 0 0;font-size:20px;color:#1e293b}
.btn-close{width:36px;height:36px;border:1px solid #e2e8f0;border-radius:8px;background:#fff;color:#64748b;font-size:22px;line-height:1}
.btn-close:hover{background:#f1f5f9}
.meta-row{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:16px}
.meta-item{border:1px solid #e2e8f0;border-radius:10px;background:#f8fafc;padding:14px}
.meta-item span{display:block;color:#64748b;font-size:11px;margin-bottom:5px}
.meta-item strong{font-size:18px;color:#1e293b}

/* 自动分析提示 */
.auto-banner{display:flex;align-items:center;gap:10px;padding:12px 16px;background:linear-gradient(135deg,#ecfdf5,#f0fdf4);border:1px solid #a7f3d0;border-radius:10px;margin-bottom:18px;font-size:13px;color:#065f46;line-height:1.5}
.auto-icon{font-size:18px;flex-shrink:0}
.auto-banner strong{color:#047857}

/* 自动标签 */
.auto-tag{display:inline-flex;align-items:center;min-height:20px;border-radius:999px;padding:0 8px;background:#dbeafe;color:#1d4ed8;font-size:10px;font-weight:700;margin-left:6px;vertical-align:middle}
.required{color:#dc2626}

.form-row{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.modal-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:18px}
@media(max-width:560px){.meta-row,.form-row{grid-template-columns:1fr}}
</style>