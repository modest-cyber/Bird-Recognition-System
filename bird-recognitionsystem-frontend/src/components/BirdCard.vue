<template>
  <el-card class="bird-card" shadow="hover" @click="$emit('click')">
    <div class="bird-image">
      <el-image 
        :src="bird.image_url || defaultImage" 
        fit="cover"
        :alt="bird.name"
      >
        <template #error>
          <div class="image-placeholder">
            <el-icon><Picture /></el-icon>
          </div>
        </template>
      </el-image>
    </div>
    <div class="bird-info">
      <h3 class="bird-name">{{ bird.name }}</h3>
      <p class="bird-family">{{ bird.family || '未分类' }}</p>
    </div>
  </el-card>
</template>

<script setup>
defineProps({
  bird: {
    type: Object,
    required: true
  }
})

defineEmits(['click'])

const defaultImage = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgZmlsbD0iI2VlZSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjOTk5IiBmb250LXNpemU9IjE0Ij7ml6Dlm77niYc8L3RleHQ+PC9zdmc+'
</script>

<style scoped>
.bird-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.bird-card:hover {
  transform: translateY(-5px);
}

.bird-image {
  height: 150px;
  overflow: hidden;
  border-radius: 4px;
  margin-bottom: 12px;
}

.bird-image .el-image {
  width: 100%;
  height: 100%;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  color: #ccc;
  font-size: 40px;
}

.bird-info {
  text-align: center;
}

.bird-name {
  font-size: 16px;
  margin: 0 0 8px;
  color: #333;
}

.bird-family {
  font-size: 14px;
  color: #999;
  margin: 0;
}
</style>
