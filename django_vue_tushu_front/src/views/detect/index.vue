<template>
  <div class="container">
    <!-- Canvas画布 -->
    <canvas
      ref="canvasRef"
      width="600"
      height="400"
      class="canvas"
    />

    <!-- 操作按钮 -->
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

      <el-button @click="downloadImage">
        下载
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import axios from "axios";

const canvasRef = ref(null);
const image = ref(null);
const originalImage = ref(null);
const detections = ref([]);
const isComparing = ref(false);

// 上传文件变化
const handleFileChange = (uploadFile) => {
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

// 阻止自动上传
const handleUpload = () => false;

// 重置画布
const reset = () => {
  detections.value = [];
  image.value = null;
  originalImage.value = null;
  const ctx = canvasRef.value.getContext("2d");
  ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
};

// 绘制图像和检测框
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

// 下载画布图像
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

// 对比模式变化监听
watch(isComparing, () => {
  drawCanvas();
});

// 发送检测请求
const sendToDetect = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  try {
    const res = await axios.post("http://localhost:8000/api/detect/", formData);
    detections.value = res.data.data || [];
    drawCanvas();
  } catch (err) {
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
</style>
