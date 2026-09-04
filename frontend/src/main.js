import { createApp } from 'vue'
import Antd from 'ant-design-vue'
import App from './App.vue'
import router from './router/index.js'
import './assets/style.css'

const app = createApp(App)
app.use(Antd)
app.use(router)
app.mount('#app')