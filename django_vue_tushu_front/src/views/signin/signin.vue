<template>
  <div class="login-container">
    <el-card class="box-card">
      <div class="login-body">
        <div class="login-title" @click="toIndex">django vue图书管理系统 - 注册</div>
        <el-form ref="form" :model="registerForm" :rules="rules" label-position="top" size="default">
          <el-input
            placeholder="请输入账号..."
            v-model="registerForm.accountNumber"
            class="login-input"
            clearable
          ></el-input>
          <el-input
            placeholder="请输入密码..."
            v-model="registerForm.userPassword"
            class="login-input"
            show-password
            clearable
          ></el-input>
          <el-input
            placeholder="请确认密码..."
            v-model="registerForm.confirmPassword"
            class="login-input"
            show-password
            clearable
          ></el-input>

          <div class="login-submit">
            <el-button type="primary" @click="register">注册</el-button>
            <el-button type="warning" style="margin-left: 20px" @click="$router.push('/login')">
              返回登录
            </el-button>
          </div>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: "sign-in",
  data() {
    return {
      registerForm: {
        accountNumber: '',
        userPassword: '',
        confirmPassword: '',
      },
      rules: {
        accountNumber: [
          { required: true, message: '账号不能为空', trigger: 'blur' },
          { min: 3, max: 20, message: '账号长度在3到20个字符', trigger: 'blur' }
        ],
        userPassword: [
          { required: true, message: '密码不能为空', trigger: 'blur' },
          { min: 6, message: '密码长度至少6位', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请确认密码', trigger: 'blur' },
          { validator: (rule, value, callback) => {
              if (value !== this.registerForm.userPassword) {
                callback(new Error('两次输入密码不一致'));
              } else {
                callback();
              }
            }, trigger: 'blur'
          }
        ]
      }
    };
  },
  methods: {
    register() {
      this.$refs.form.validate(valid => {
        if (!valid) return;
        // 调接口注册逻辑
        this.$request.post("/api/signin/", {
          username: this.registerForm.accountNumber,
          password: this.registerForm.userPassword,
        }).then(res => {
          if (res.data.meta.status === 200) {
            this.$message.success("注册成功，请登录");
            this.$router.push('/login');
          } else {
            this.$message.error(res.data.meta.message || "注册失败");
          }
        }).catch(() => {
          this.$message.error("请求失败，请重试");
        });
      });
    },
    toIndex() {
      this.$router.replace({ path: '/index' });
    }
  }
};
</script>

<style scoped>
.login-container {
  background-image: url('@/assets/bj.jpg');
  background-size: cover;
  background-position: center;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100%;
}

.login-body {
  padding: 30px;
  width: 300px;
  height: 100%;
}

.login-title {
  padding-bottom: 30px;
  text-align: center;
  font-weight: 600;
  font-size: 20px;
  color: #409EFF;
  cursor: pointer;
}

.login-input {
  margin-bottom: 20px;
}

.login-submit {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
