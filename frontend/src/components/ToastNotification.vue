<template>
  <transition-group name="toast" tag="div" class="toast-container">
    <div
      v-for="item in toasts"
      :key="item.id"
      :class="['toast-item', 'toast-' + item.type]"
    >
      <span class="toast-icon">{{ iconFor(item.type) }}</span>
      <span class="toast-text">{{ item.message }}</span>
      <button class="toast-close" @click="dismiss(item.id)">&times;</button>
    </div>
  </transition-group>
</template>

<script>
import { emitter } from "../services/api";

let _id = 0;

export default {
  name: "ToastNotification",
  data() {
    return { toasts: [] };
  },
  methods: {
    iconFor(type) {
      const map = { success: "\u2713", error: "\u2717", warning: "\u26a0", info: "\u2139" };
      return map[type] || map.info;
    },
    show(message, type, duration) {
      type = type || "info";
      duration = duration || 4000;
      const id = ++_id;
      this.toasts.push({ id, message, type });
      if (duration > 0) {
        setTimeout(() => this.dismiss(id), duration);
      }
    },
    dismiss(id) {
      this.toasts = this.toasts.filter(t => t.id !== id);
    }
  },
  mounted() {
    emitter.on("toast", (payload) => {
      this.show(payload.message, payload.type, payload.duration);
    });
    emitter.on("api-error", (payload) => {
      if (payload.status !== 401) { // Auth expiry handled separately
        this.show(payload.message || "Request failed", "error", 5000);
      }
    });
    emitter.on("auth-expired", () => {
      this.show("Session expired, please login again", "warning", 6000);
      this.$emit("auth-expired");
    });
  }
};
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none;
}

.toast-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 18px;
  border-radius: 6px;
  font-size: 14px;
  color: #fff;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.18);
  pointer-events: auto;
  min-width: 280px;
  max-width: 420px;
  backdrop-filter: blur(6px);
}

.toast-success { background: #16a34a; }
.toast-error   { background: #dc2626; }
.toast-warning { background: #d97706; }
.toast-info    { background: #2563eb; }

.toast-icon { font-size: 16px; flex-shrink: 0; }
.toast-text { flex: 1; line-height: 1.4; }
.toast-close {
  background: none;
  border: none;
  color: #fff;
  font-size: 18px;
  cursor: pointer;
  flex-shrink: 0;
  opacity: 0.7;
  padding: 0 2px;
}
.toast-close:hover { opacity: 1; }

.toast-enter-active, .toast-leave-active {
  transition: all 0.35s ease;
}
.toast-enter { opacity: 0; transform: translateX(40px); }
.toast-leave-to { opacity: 0; transform: translateX(40px); }
</style>
