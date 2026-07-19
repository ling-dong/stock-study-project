import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ToastPlugin from './plugins/toast'
import ConfirmPlugin from './plugins/confirm'

import './styles/theme.css'
import './styles/components.css'

Vue.config.productionTip = false
Vue.use(ToastPlugin)
Vue.use(ConfirmPlugin)

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
