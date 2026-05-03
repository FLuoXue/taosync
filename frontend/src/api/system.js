import request from '@/utils/request'

// 系统配置
export function systemGet() {
	return request({
		url: '/system',
		headers: {
			isMask: false
		},
		method: 'get'
	})
}

// 更新系统配置
export function systemPut(data) {
	return request({
		url: '/system',
		headers: {
			isMask: false
		},
		method: 'put',
		data
	})
}