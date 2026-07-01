import api from './index'

export function submitQuiz(data) {
  return api.post('/quiz/submit', data)
}
