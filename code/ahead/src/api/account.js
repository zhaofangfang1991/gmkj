// 关于账号的管理
import request from '@/utils/request'

export function create(data) {
  return request({
    url: '/users',
    method: 'post',
    data
  })
}

// 账号列表
export function fetchList(query) {
  return request({
    url: '/users',
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

// 删除
export function deleteAccount(id) {
  return request({
    url: '/user/' + id,
    method: 'patch'
  })
}

// 更新
export function updateAccount(tempData) {
  return request({
    url: '/user/' + tempData.id,
    method: 'put',
    params: tempData
  })
}