import {createApp} from "vue";
import App from "./App.vue";
import router from "./router";
import request from "@/utils/request.js";
import "normalize.css/normalize.css";
import deepClone from "@/utils/deepClone.js";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import zhCn from "element-plus/es/locale/lang/zh-cn";
import * as ElementPlusIconsVue from "@element-plus/icons-vue";
import * as echarts from 'echarts';


const app = createApp(App);

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component);
}

app.config.globalProperties.$request = request;
app.config.globalProperties.$deepClone = deepClone;
app.config.globalProperties.$echarts = echarts;

app.use(router);
app.use(ElementPlus, {locale: zhCn});
app.mount("#app");
