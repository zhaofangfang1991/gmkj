// 关于账号的管理
import request from '@/utils/request'

export function create(data) {
  return request({
    url: '/user',
    method: 'post',
    data
  })
}

export function fetchList(query) {
  return request({
    url: '/user',
    method: 'get',
    params: query
  })
}

export function logout() {
  return request({
    url: '/user/logout',
    method: 'post'
  })
}
