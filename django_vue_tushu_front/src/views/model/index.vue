<template>
  <el-button type="primary" @click="visible = true">添加模型</el-button>
  <el-card shadow="never" style="margin-top: 10px">
    <!-- 查询区域 -->
    <el-card shadow="never" style="margin: 10px 0">
      <el-form :model="search">
        <el-row :gutter="30">
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item label="模型名称:">
              <el-input v-model="search.name" placeholder="请输入模型名称:" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <div style="text-align: right">
        <el-button type="primary" @click="getList()">查询</el-button>
        <el-button @click="resetSearch()">重置</el-button>
      </div>
    </el-card>

    <!-- 表格区域 -->
    <el-table :data="tableData" stripe>
      <el-table-column type="index" label="ID" width="70" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="labels" label="标签" show-overflow-tooltip />
      <el-table-column prop="note" label="备注" show-overflow-tooltip />
      <el-table-column
        prop="createTime"
        label="创建时间"
        width="280"
        :formatter="formatDate"
      />

      <el-table-column label="操作" width="220" fixed="right">
        <template #default="scope">
          <el-button
            link
            type="primary"
            size="small"
            @click="downloadFile(scope.row)"
          >
            下载
          </el-button>
          <el-button
            link
            type="primary"
            size="small"
            @click="editItem(scope.row)"
            >编辑</el-button
          >
          <el-popconfirm
            title="确定要删除吗?"
            @confirm="deleteItem(scope.row.id)"
          >
            <template #reference>
              <el-button link type="primary" size="small">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <!-- 分页 -->
    <el-pagination
      background
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      layout="sizes, total, prev, pager, next"
      :total="totalNum"
      :currentPage="search.pageNum"
      :pageSize="search.pageSize"
    >
    </el-pagination>
  </el-card>
  <!-- 新增或编辑的抽屉 -->
  <sDrawer
    v-model="visible"
    :title="form.id ? '编辑模型' : '添加模型'"
    size="35%"
    :close-on-click-modal="false"
  >
    <el-form :model="form" label-width="100px" ref="ruleFormRef">
      <el-form-item label="模型名称:">
        <el-input v-model="form.name" />
      </el-form-item>
    </el-form>
    <el-form :model="form" label-width="100px" ref="ruleFormRef">
      <el-form-item label="模型标签:">
        <el-input v-model="form.labels" />
      </el-form-item>
    </el-form>
    <el-form :model="form" label-width="100px" ref="ruleFormRef">
      <el-form-item label="备注:">
        <el-input v-model="form.note" />
      </el-form-item>
    </el-form>
    <el-form :model="form" label-width="100px" ref="ruleFormRef">
      <el-form-item label="模型文件:">
        <el-upload
          class="upload-demo"
          action="http://127.0.0.1:8000/api/upload/"
          :show-file-list="true"
          :limit="1"
          :on-success="handleUploadSuccess"
          :before-upload="beforeUpload"
        >
          <el-button type="primary">上传模型文件</el-button>
        </el-upload>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="saveData()">确定</el-button>
    </template>
  </sDrawer>
</template>

<script>
import sDrawer from "@/components/s-drawer/s-drawer.vue";
import { hostURL } from '@/utils/request.js'
export default {
  components: {
    sDrawer,
  },
  watch: {
    visible(value) {
      if (!value) {
        this.form = {};
      }
    },
  },
  data() {
    return {
      form: {},
      visible: false,
      tableData: [],
      totalNum: 100,
      search: {
        pageNum: 1,
        pageSize: 10,
        // token: "",
      },
    };
  },
  created() {
    // this.search.token = localStorage.getItem("token");
    this.getList();
  },
  methods: {
    async getList() {
      const res = await this.$request.get("/api/model/", {
        params: this.search,
      });

      if (res.data.code === 200) {
        this.tableData = res.data.data;
        this.totalNum = res.data.zs;
      }
    },
    // 每页条数改变时触发 选择一页显示多少行
    handleSizeChange(val) {
      console.log(`每页 ${val} 条`);
      this.search.pageSize = val;
      this.getList();
    },
    // 当前页改变时触发 跳转其他页
    handleCurrentChange(val) {
      console.log(`当前页: ${val}`);
      this.search.pageNum = val;
      this.getList();
    },
    resetSearch() {
      let search = {
        pageNum: this.search.pageNum,
        pageSize: this.search.pageSize,
      };
      this.search = search;
      this.getList();
    },
    editItem(row) {
      this.form = this.$deepClone(row);
      this.visible = true;
    },
    async saveData() {
      if (this.form.id) {
        const res = await this.$request.put("/api/model/", this.form);
        if (res.data.code === 200) {
          this.$message.success(res.data.message);
          this.getList();
          this.visible = false;
        }
      } else {
        const res = await this.$request.post("/api/model/", this.form);
        if (res.data.code === 200) {
          this.$message.success(res.data.message);
          this.getList();
          this.visible = false;
        }
      }
    },
    async deleteItem(id) {
      const res = await this.$request.delete("/api/del/" + id + "/");
      if (res.data.code === 200) {
        this.$message.success(res.data.message);
        this.getList();
      }
    },
    formatDate(row, column,cellValue) {
      if (!cellValue) return "";
      const date = new Date(cellValue);
      const Y = date.getFullYear();
      const M = String(date.getMonth() + 1).padStart(2, "0");
      const D = String(date.getDate()).padStart(2, "0");
      const h = String(date.getHours()).padStart(2, "0");
      const m = String(date.getMinutes()).padStart(2, "0");
      const s = String(date.getSeconds()).padStart(2, "0");
      return `${Y}-${M}-${D} ${h}:${m}:${s}`;
    },
    handleUploadSuccess(response) {
      this.form.path = response.data.file;
      this.$message.success("上传成功");
    },
    beforeUpload(file) {
      const isZip =
        file.type === "application/zip" ||
        file.name.endsWith(".pt") ||
        file.name.endsWith(".onnx");
      if (!isZip) {
        this.$message.error("只能上传模型文件");
      }
      return isZip;
    },
    downloadFile(row) {
      // 假设每条数据里有个 fileUrl 字段存文件地址
      if (!row.path) {
        this.$message.warning("无可下载文件");
        return;
      }
      // 直接打开文件链接触发下载
      downloadPath = hostURL + "/download/" + row.path
      window.open(downloadPath, "_blank");
    },
  },
};
</script>

<style scoped>
.el-pagination {
  margin-top: 10px;
}

.el-row {
  margin-bottom: 20px;
}

.el-row:last-child {
  margin-bottom: 0px;
}
</style>
