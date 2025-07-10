import { createRouter, createWebHistory } from 'vue-router';
import UI from '../components/UI.vue';



const routes = [
  {
    path: '/',
    name: 'UI',
    component: UI
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;