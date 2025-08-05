import { createRouter, createWebHistory } from "vue-router";
import NProgress from "nprogress";
import "nprogress/nprogress.css";

NProgress.configure({
  showSpinner: false,
});

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      redirect: "/login",
    },
    {
      path: "/login",
      name: "login",
      meta: { title: "登陆" },
      component: () => import("@/views/login/login.vue"),
      hidden: true,
    },
    {
      path: "/signin",
      name: "signin",
      meta: { title: "注册" },
      component: () => import("@/views/signin/signin.vue"),
      hidden: true,
    },
    {
      path: "/main",
      name: "main",
      meta: { title: "主页" },
      component: () => import("@/views/main/index.vue"),
      children: [
        {
          path: "home",
          name: "home",
          meta: { title: "首页" },
          component: () => import("@/views/home/index.vue"),
        },
        {
          path: "model",
          name: "model",
          meta: { title: "模型管理" },
          component: () => import("@/views/model/index.vue"),
        },
        {
          path: "detect",
          name: "detect",
          meta: { title: "在线检测" },
          component: () => import("@/views/detect/index.vue"),
        },
        {
          path: "result",
          name: "result",
          meta: { title: "检测结果" },
          component: () => import("@/views/result/index.vue"),
        },
      ],
    },
  ],
});

import defaultSettings from "@/settings";

//路由全局前置钩子
router.beforeEach((to, from, next) => {
  NProgress.start();
  document.title = `${to.meta.title || "JDC"} - ${defaultSettings.title}`;
  let token = localStorage.getItem("token");

  // 允许未登录访问的路由白名单
  const whiteList = ["/login", "/signin"];

  if (token) {
    next();
  } else {
    if (whiteList.includes(to.path)) {
      next();
    } else {
      next({ path: "/login" });
    }
  }
});

// //路由全局后置钩子
router.afterEach(() => {
  NProgress.done();
});

export default router;
