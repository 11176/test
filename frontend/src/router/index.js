// ✅ 完整的 router/index.js 配置（重构后，仅保留首页，构建三个主要模块框架）
import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/test',
    component: () => import('@/views/test/test.vue')
  },
  // 首页（保留原 Home 页面）
  {
    path: '/',
    component: () => import('@/views/Home.vue')
  },

  { 
    path: '/portrait', component: () => import('@/views/portrait/PortraitIndex.vue') 
  },
  // 画像分析模块
  {
    path: '/portrait/user',
    component: () => import('@/views/portrait/UserAnalysis.vue')
  },
  {
    path: '/portrait/region',
    component: () => import('@/views/portrait/RegionAnalysis.vue')
  },

  // 商品运营分析模块
  {
    path: '/product',
    name: 'ProductIndex',
    component: () => import('@/views/product/ProductIndex.vue'),
  },
  {
    path: '/product/overview',
    component: () => import('@/views/product/ProductOverview.vue'),
  },
  {
    path: '/product/category-rank',
    component: () => import('@/views/product/ProductCategoryRank.vue'),
  },
  {
    path: '/product/risk',
    component: () => import('@/views/product/ProductRisk.vue'),
  },
  {
    path: '/product/health',
    component: () => import('@/views/product/ProductHealth.vue'),
  },
  {
    path: '/product/association',
    component: () => import('@/views/product/ProductAssociation.vue'),
  },
  // 智能分析建议模块
  {
    path: '/intelligence',
    component: () => import('@/views/intelligent/IntelligentIndex.vue')
  },
  {
    path: '/intelligence/summary',
    component: () => import('@/views/intelligent/IntelligentSummary.vue')
  },
  {
    path: '/intelligence/qa',
    component: () => import('@/views/intelligent/IntelligentQA.vue')
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
