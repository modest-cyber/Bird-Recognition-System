<template>
  <Layout>
    <section class="home-hero">
      <div class="hero-noise"></div>
      <div class="hero-orbit orbit-a"></div>
      <div class="hero-orbit orbit-b"></div>

      <div class="hero-grid">
        <div class="hero-copy">
          <p class="eyebrow">BIRD RECOGNITION</p>
          <h1>上传一张图，立刻圈出画面里的鸟</h1>
          <p class="summary">
            聚焦单一动作，不做分心导航。进入识别页后直接上传图片，系统会返回鸟区域位置、置信度与标注结果。
          </p>

          <div class="hero-actions">
            <el-button class="cta-button" type="primary" size="large" @click="goRecognize">
              <el-icon><Camera /></el-icon>
              立即识别
            </el-button>
            <span class="cta-note">支持 jpg / png / webp，单张图片不超过 10MB</span>
          </div>
        </div>

        <div class="hero-stage" aria-hidden="true">
          <div class="stage-frame frame-main">
            <div class="frame-label">实时检测</div>
            <div class="scan-surface">
              <div class="bbox box-a"><span>鸟区域 A</span></div>
              <div class="bbox box-b"><span>鸟区域 B</span></div>
              <div class="bbox box-c"><span>鸟区域 C</span></div>
            </div>
          </div>
          <div class="stage-frame frame-side frame-top">
            <span>定位</span>
            <strong>bbox</strong>
          </div>
          <div class="stage-frame frame-side frame-bottom">
            <span>输出</span>
            <strong>confidence</strong>
          </div>
        </div>
      </div>

      <div class="hero-footer">
        <div class="footer-line"></div>
        <div class="footer-text">
          <span>上传图片</span>
          <span>检测鸟区域</span>
          <span>查看结果</span>
        </div>
      </div>
    </section>
  </Layout>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Layout from '@/components/Layout.vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const goRecognize = () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后再开始识别')
    router.push('/login')
    return
  }

  router.push('/recognize')
}
</script>

<style scoped>
.home-hero {
  position: relative;
  min-height: calc(100vh - 140px);
  overflow: hidden;
  border-radius: 28px;
  padding: clamp(28px, 5vw, 56px);
  background:
    radial-gradient(circle at top left, rgba(255, 214, 153, 0.34), transparent 34%),
    radial-gradient(circle at 80% 20%, rgba(120, 167, 255, 0.28), transparent 26%),
    linear-gradient(135deg, #f6f1e8 0%, #edf3fb 42%, #dfeaf7 100%);
  box-shadow: 0 22px 60px rgba(29, 53, 87, 0.14);
}

.hero-noise {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgba(35, 55, 86, 0.06) 0.7px, transparent 0.7px);
  background-size: 18px 18px;
  opacity: 0.35;
  pointer-events: none;
}

.hero-orbit {
  position: absolute;
  border-radius: 999px;
  border: 1px solid rgba(28, 53, 87, 0.12);
  pointer-events: none;
}

.orbit-a {
  width: 420px;
  height: 420px;
  right: -120px;
  top: -80px;
}

.orbit-b {
  width: 260px;
  height: 260px;
  left: -90px;
  bottom: -70px;
}

.hero-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(320px, 0.95fr);
  gap: clamp(28px, 4vw, 56px);
  align-items: center;
  min-height: calc(100vh - 260px);
}

.hero-copy {
  max-width: 640px;
  animation: fadeUp 0.8s ease-out both;
}

.eyebrow {
  margin: 0 0 18px;
  font-size: 12px;
  letter-spacing: 0.28em;
  color: #7c5f1b;
  font-weight: 700;
}

.hero-copy h1 {
  margin: 0;
  max-width: 10ch;
  color: #172033;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: clamp(44px, 7vw, 82px);
  line-height: 0.98;
  letter-spacing: -0.04em;
}

.summary {
  margin: 24px 0 0;
  max-width: 34em;
  font-size: clamp(15px, 1.7vw, 18px);
  line-height: 1.8;
  color: rgba(23, 32, 51, 0.76);
}

.hero-actions {
  margin-top: 32px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 14px;
}

.cta-button {
  min-width: 176px;
  height: 54px;
  padding: 0 28px;
  border: none;
  border-radius: 999px;
  background: linear-gradient(135deg, #183153 0%, #2a5b8f 100%);
  box-shadow: 0 18px 34px rgba(24, 49, 83, 0.24);
}

.cta-button:hover {
  transform: translateY(-1px);
}

.cta-note {
  font-size: 13px;
  color: rgba(23, 32, 51, 0.58);
}

.hero-stage {
  position: relative;
  min-height: 560px;
  animation: fadeUp 1s ease-out both;
}

.stage-frame {
  position: absolute;
  border-radius: 26px;
  backdrop-filter: blur(16px);
  background: rgba(255, 255, 255, 0.58);
  border: 1px solid rgba(255, 255, 255, 0.65);
  box-shadow: 0 18px 40px rgba(35, 55, 86, 0.14);
}

.frame-main {
  inset: 34px 18px 34px 34px;
  padding: 22px;
}

.frame-label {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 7px 14px;
  border-radius: 999px;
  background: rgba(24, 49, 83, 0.9);
  color: #fff;
  font-size: 12px;
  letter-spacing: 0.12em;
}

.scan-surface {
  position: absolute;
  inset: 72px 22px 22px;
  border-radius: 22px;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(29, 52, 84, 0.08), rgba(29, 52, 84, 0.04)),
    radial-gradient(circle at 30% 30%, rgba(240, 190, 117, 0.55), transparent 24%),
    radial-gradient(circle at 70% 25%, rgba(130, 178, 255, 0.5), transparent 22%),
    linear-gradient(160deg, #405f36 0%, #7f6d3e 35%, #243645 100%);
}

.scan-surface::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    linear-gradient(transparent 0%, rgba(255, 255, 255, 0.18) 48%, transparent 100%);
  transform: translateY(-100%);
  animation: scanLine 3.6s ease-in-out infinite;
}

.bbox {
  position: absolute;
  border-radius: 14px;
  border: 2px solid;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.18);
}

.bbox span {
  position: absolute;
  top: -14px;
  left: 10px;
  padding: 6px 10px;
  border-radius: 999px;
  color: #fff;
  font-size: 12px;
  white-space: nowrap;
  background: rgba(17, 24, 39, 0.78);
}

.box-a {
  left: 14%;
  top: 24%;
  width: 28%;
  height: 22%;
  border-color: #6ae3d3;
}

.box-b {
  right: 16%;
  top: 18%;
  width: 22%;
  height: 18%;
  border-color: #ffd670;
}

.box-c {
  left: 40%;
  bottom: 18%;
  width: 20%;
  height: 16%;
  border-color: #7cb7ff;
}

.frame-side {
  width: 158px;
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.frame-side span {
  font-size: 12px;
  color: rgba(23, 32, 51, 0.56);
  letter-spacing: 0.12em;
}

.frame-side strong {
  font-size: 26px;
  color: #172033;
  font-family: Georgia, 'Times New Roman', serif;
}

.frame-top {
  left: 0;
  top: 0;
}

.frame-bottom {
  right: 0;
  bottom: 0;
}

.hero-footer {
  position: relative;
  z-index: 1;
  margin-top: 12px;
}

.footer-line {
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(23, 32, 51, 0.18) 18%, rgba(23, 32, 51, 0.18) 82%, transparent 100%);
}

.footer-text {
  margin-top: 18px;
  display: flex;
  justify-content: space-between;
  gap: 16px;
  font-size: 12px;
  letter-spacing: 0.18em;
  color: rgba(23, 32, 51, 0.56);
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(18px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes scanLine {
  0% {
    transform: translateY(-100%);
  }
  50% {
    transform: translateY(0%);
  }
  100% {
    transform: translateY(100%);
  }
}

@media (max-width: 980px) {
  .home-hero {
    min-height: auto;
    padding: 24px;
  }

  .hero-grid {
    grid-template-columns: 1fr;
    min-height: auto;
  }

  .hero-copy h1 {
    max-width: none;
  }

  .hero-stage {
    min-height: 440px;
  }

  .frame-main {
    inset: 30px 10px 24px 18px;
  }

  .frame-side {
    width: 132px;
    padding: 14px 16px;
  }

  .frame-side strong {
    font-size: 22px;
  }
}

@media (max-width: 640px) {
  .home-hero {
    border-radius: 20px;
    padding: 18px;
  }

  .hero-copy h1 {
    font-size: 42px;
  }

  .summary {
    font-size: 15px;
  }

  .hero-stage {
    min-height: 360px;
  }

  .frame-main {
    inset: 18px 0 22px;
    padding: 16px;
  }

  .scan-surface {
    inset: 56px 16px 16px;
  }

  .frame-side {
    display: none;
  }

  .footer-text {
    flex-direction: column;
    gap: 10px;
    letter-spacing: 0.1em;
  }
}
</style>
