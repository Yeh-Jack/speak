import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import './style.css';

const app = createApp(App);

app.use(createPinia());
app.use(router);

app.directive('spray', {
  mounted(el) {
    el.classList.add('hover-fade');
  }
});

app.mount('#app');
