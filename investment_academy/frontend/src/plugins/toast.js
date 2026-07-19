import IAToast from '../components/ui/Toast.vue'

const ToastPlugin = {
  install(Vue) {
    const ToastConstructor = Vue.extend(IAToast)
    const toastInstance = new ToastConstructor()
    toastInstance.$mount()
    document.body.appendChild(toastInstance.$el)

    Vue.prototype.$toast = (message, type = 'info', duration = 3000) => {
      toastInstance.add(message, type, duration)
    }
  },
}

export default ToastPlugin
