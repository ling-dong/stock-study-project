import api from './index'

export function getPreferences() {
  return api.get('/user/preferences')
}

export function updatePreferences(data) {
  return api.put('/user/preferences', data)
}

export function addPsychologyCheck(data) {
  return api.post('/user/psychology-check', data)
}

export function getPsychologyHistory() {
  return api.get('/user/psychology-history')
}

export function addJournalEntry(data) {
  return api.post('/user/journal', data)
}

export function getJournal() {
  return api.get('/user/journal')
}

export function updateJournalEntry(id, data) {
  return api.put(`/user/journal/${id}`, data)
}

export function deleteJournalEntry(id) {
  return api.delete(`/user/journal/${id}`)
}
