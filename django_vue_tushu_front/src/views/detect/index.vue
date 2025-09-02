<template>
  <div class="container">
    <!-- Canvas -->
    <canvas ref="canvasRef" width="600" height="400" class="canvas" />

    <!-- 按钮区 -->
    <div class="button-group">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :show-file-list="false"
        :before-upload="handleUpload"
        :on-change="handleFileChange"
        action=""
        name="file"
      >
        <el-button type="primary">上传</el-button>
      </el-upload>

      <el-button @click="reset">重置</el-button>

      <el-button
        @mousedown="isComparing = true"
        @mouseup="isComparing = false"
        @mouseleave="isComparing = false"
      >
        对比
      </el-button>

      <el-button @click="downloadImage">下载</el-button>
    </div>

    <!-- 下拉选择器 + 滑动条 -->
    <div class="controls">
      <el-select
        v-model="selectedModelPath"
        placeholder="选择模型"
        style="width: 200px"
      >
        <el-option
          v-for="item in modelList"
          :key="item.id"
          :label="item.name"
          :value="item.path"
        />
      </el-select>

      <div class="slider">
        <span class="slider-label">置信度：{{ (confidenceThreshold * 100).toFixed(0) }}%</span>
        <el-slider
          v-model="confidenceThreshold"
          :min="0"
          :max="1"
          :step="0.01"
          style="width: 200px"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import request from "@/utils/request";

const canvasRef = ref(null);
const image = ref(null);
const originalImage = ref(null);
const detections = ref([]);
const isComparing = ref(false);

// 模型列表和选择
const modelList = ref([]);
const selectedModelPath = ref("");

// 获取模型列表
const fetchModelList = async () => {
  try {
    const res = await request.get("/api/model/");
    if (res.data.code === 200 && Array.isArray(res.data.data)) {
      modelList.value = res.data.data;
      if (res.data.data.length > 0) {
        selectedModelPath.value = res.data.data[0].path;
      }
    }
  } catch (err) {
    console.error("获取模型列表失败:", err);
  }
};

// 页面加载时获取模型
onMounted(() => {
  fetchModelList();
});

const confidenceThreshold = ref(0.5);

// 上传处理
const handleFileChange = (uploadFile) => {
  reset();

  const reader = new FileReader();
  reader.onload = (e) => {
    const img = new Image();
    img.onload = () => {
      originalImage.value = img;
      drawCanvas();
      sendToDetect(uploadFile.raw);
    };
    img.src = e.target.result;
    image.value = img;
  };
  reader.readAsDataURL(uploadFile.raw);
};


const handleUpload = () => false;

// 重置画布
const reset = () => {
  detections.value = [];
  image.value = null;
  originalImage.value = null;
  const ctx = canvasRef.value.getContext("2d");
  ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
};

// 绘制画布
const drawCanvas = () => {
  const canvas = canvasRef.value;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (!originalImage.value) return;

  const img = originalImage.value;
  const maxWidth = 600;
  const maxHeight = 400;
  const aspectRatio = img.width / img.height;

  let drawWidth = img.width;
  let drawHeight = img.height;

  if (img.height > maxHeight) {
    drawHeight = maxHeight;
    drawWidth = maxHeight * aspectRatio;
  }
  if (drawWidth > maxWidth) {
    drawWidth = maxWidth;
    drawHeight = maxWidth / aspectRatio;
  }

  canvas.width = drawWidth;
  canvas.height = drawHeight;

  ctx.drawImage(img, 0, 0, drawWidth, drawHeight);

  if (!isComparing.value) {
    detections.value.forEach((det) => {
      if (det.confidence < confidenceThreshold.value) return;

      const [x1, y1, w1, h1] = det.bbox;
      const x = x1 * drawWidth;
      const y = y1 * drawHeight;
      const w = w1 * drawWidth;
      const h = h1 * drawHeight;

      ctx.strokeStyle = "red";
      ctx.lineWidth = 2;
      ctx.strokeRect(x, y, w, h);

      ctx.font = "14px Arial";
      ctx.fillStyle = "red";
      ctx.fillText(
        `${det.label} (${(det.confidence * 100).toFixed(1)}%)`,
        x,
        y - 5
      );
    });
  }
};

// 下载图像
const downloadImage = () => {
  const canvas = canvasRef.value;
  if (!canvas) return;
  drawCanvas();
  const dataURL = canvas.toDataURL("image/png");
  const link = document.createElement("a");
  link.href = dataURL;
  link.download = "detected_image.png";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// 监听状态变化
watch(isComparing, () => {
  drawCanvas();
});

watch(confidenceThreshold, () => {
  drawCanvas();
});

// 发送检测请求
const sendToDetect = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("model_path", selectedModelPath.value);
  try {
    const res = await request.post("/api/detect/", formData);
    detections.value = res.data.data || [];
    drawCanvas();
  } catch (err) {
    console.error("检测失败:", err);
  }
};
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.canvas {
  border: 1px solid #ccc;
}

.button-group {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.controls {
  margin-top: 20px;
  display: flex;
  gap: 30px;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
}

.slider {
  display: flex;
  align-items: center;
  gap: 10px;
}

.slider-label {
  font-size: 14px;
  white-space: nowrap;
}
</style>
