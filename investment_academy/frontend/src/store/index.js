import Vue from 'vue'
import Vuex from 'vuex'
import { getProgress, updateProgress } from '../api/progress'
import { getPreferences, updatePreferences } from '../api/user'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    progress: [],           // 全部章节进度
    preferences: null,      // 用户偏好
    loading: false,
  },
  mutations: {
    SET_PROGRESS(state, data) { state.progress = data || []; },
    SET_PREFERENCES(state, data) { state.preferences = data; },
    SET_LOADING(state, val) { state.loading = val; },
  },
  actions: {
    async fetchProgress({ commit }) {
      try {
        const res = await getProgress()
        commit('SET_PROGRESS', res.data)
      } catch (e) {
        console.error('获取进度失败:', e)
      }
    },
    async saveProgress({ dispatch }, { chapterId, data }) {
      try {
        await updateProgress(chapterId, data)
        dispatch('fetchProgress')
      } catch (e) {
        console.error('保存进度失败:', e)
      }
    },
    async fetchPreferences({ commit }) {
      try {
        const res = await getPreferences()
        commit('SET_PREFERENCES', res.data)
      } catch (e) {
        console.error('获取偏好失败:', e)
      }
    },
    async savePreferences({ commit }, data) {
      try {
        const res = await updatePreferences(data)
        commit('SET_PREFERENCES', res.data)
      } catch (e) {
        console.error('保存偏好失败:', e)
      }
    },
  },
  getters: {
    chapterProgress: (state) => (chapterId) => {
      return (state.progress || []).find(p => p.chapter_id === chapterId)
    },
  },
})
