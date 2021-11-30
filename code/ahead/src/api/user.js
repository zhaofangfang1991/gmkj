import request from '@/utils/request'

export function login(data) {
  return request({
    // headers: {
    //   Accept: "application/json;charset=utf-8"
    // },
    url: '/oauth/token',
    method: 'post',
    data
  })
}

export function getInfo(token) {
  return request({
    url: '/user/info',
    method: 'get',
    params: { token }
  })
}

export function logout() {
  return request({
    url: '/oauth/token',
    method: 'get'
  })
}
