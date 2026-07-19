import ConfirmDialog from '../components/ui/ConfirmDialog.vue'

const ConfirmPlugin = {
  install(Vue) {
    const ConfirmConstructor = Vue.extend(ConfirmDialog)
    const confirmInstance = new ConfirmConstructor()
    confirmInstance.$mount()
    document.body.appendChild(confirmInstance.$el)

    Vue.prototype.$confirm = (options) => {
      return confirmInstance.open(options)
    }
  },
}

export default ConfirmPlugin
