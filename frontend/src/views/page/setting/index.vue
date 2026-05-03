<template>
	<div class="user">
		<div class="settings-container">
			<!-- 用户信息卡片 -->
			<div class="setting-card">
				<div class="card-title">用户信息</div>
				<div class="card-content" v-if="vuex_userInfo">
					<div class="info-item">
						<div class="info-label">用户名</div>
						<div class="info-value">{{vuex_userInfo.userName}}</div>
					</div>
					<div class="info-item">
						<div class="info-label">创建时间</div>
						<div class="info-value">{{vuex_userInfo.createTime | timeStampFilter}}</div>
					</div>
				</div>
			</div>

			<!-- 系统配置卡片 -->
			<div class="setting-card">
				<div class="card-title">系统配置</div>
				<div class="card-content">
					<div class="config-item">
						<div class="config-label">本地中转缓存上限</div>
						<div class="config-control">
							<el-input 
								v-model.number="sysConfig.copyCacheMaxMb" 
								placeholder="请输入缓存上限" 
								type="number"
								:min="1"
								style="width: 200px;">
								<template slot="append">MB</template>
							</el-input>
							<el-button 
								type="primary" 
								size="small"
								style="margin-left: 12px;" 
								:loading="cacheSaving"
								@click="saveCopyCacheMax">
								保存
							</el-button>
						</div>
					</div>
					<div class="config-tip">
						<i class="el-icon-info"></i>
						设置本地中转复制时的缓存大小限制，建议根据磁盘空间合理设置
					</div>
				</div>
			</div>

			<!-- 修改密码卡片 -->
			<div class="setting-card">
				<div class="card-title">修改密码</div>
				<div class="card-content">
					<el-form :model="resetForm" :rules="rules" ref="resetForm" label-width="90px">
						<el-form-item prop="oldPasswd" label="旧密码">
							<el-input 
								class="input" 
								placeholder="请输入旧密码" 
								show-password
								v-model="resetForm.oldPasswd">
							</el-input>
						</el-form-item>
						<el-form-item prop="passwd" label="新密码">
							<el-input 
								placeholder="请输入新密码" 
								show-password 
								v-model="resetForm.passwd">
							</el-input>
						</el-form-item>
						<el-form-item prop="passwd2" label="确认密码">
							<el-input 
								placeholder="确认新密码" 
								show-password 
								v-model="resetForm.passwd2"
								@keyup.enter.native="resetPasswd">
							</el-input>
						</el-form-item>
						<el-form-item>
							<el-button 
								type="primary" 
								:loading="loading" 
								@click="resetPasswd">
								修改密码
							</el-button>
							<el-button @click="resetPasswordForm">重置</el-button>
						</el-form-item>
					</el-form>
				</div>
			</div>
		</div>

		<div class="setting-bottom">
			<div class="setting-bottom-item">TaoSync 版本：__version_placeholder__</div>
			<div class="setting-bottom-item"><a href="https://github.com/dr34m-cn/taosync" target="_blank">项目地址（GitHub）</a></div>
			<div class="setting-bottom-item"><a href="https://github.com/dr34m-cn/taosync/issues" target="_blank">问题反馈（GitHub Issues）</a></div>
		</div>
	</div>
</template>

<script>
	import {
		editPwd
	} from "@/api/user";
	import {
		systemGet,
		systemPut
	} from "@/api/system";
	export default {
		name: 'User',
		data() {
			var validatePass2 = (rule, value, callback) => {
				if (value == '' || value == null) {
					callback(new Error('请再次输入新密码'));
				} else if (value !== this.resetForm.passwd) {
					callback(new Error('两次输入密码不一致!'));
				} else {
					callback();
				}
			};
			return {
				sysConfig: {
					copyCacheMaxMb: 1024
				},
				resetForm: {
					oldPasswd: null,
					passwd: null,
					passwd2: null
				},
				loading: false,
				cacheSaving: false,
				rules: {
					oldPasswd: [{
						required: true,
						message: '请输入旧密码',
						trigger: 'blur'
					}],
					passwd: [{
						required: true,
						message: '请输入新密码',
						trigger: 'blur'
					}],
					passwd2: [{
						validator: validatePass2,
						trigger: 'blur'
					}]
				}
			};
		},
		created() {
			this.getSystemConfig();
		},
		methods: {
			getSystemConfig() {
				systemGet().then(res => {
					this.sysConfig = res.data;
				})
			},
			saveCopyCacheMax() {
				if (!Number.isInteger(this.sysConfig.copyCacheMaxMb) || this.sysConfig.copyCacheMaxMb <= 0) {
					this.$message.error('缓存上限必须是正整数(MB)');
					return;
				}
				this.cacheSaving = true;
				systemPut({
					copyCacheMaxMb: this.sysConfig.copyCacheMaxMb
				}).then(res => {
					this.cacheSaving = false;
					this.$message({
						message: res.msg,
						type: 'success'
					});
				}).catch(() => {
					this.cacheSaving = false;
				})
			},
			resetPasswordForm() {
				this.$refs.resetForm.resetFields();
			},
			resetPasswd() {
				this.$refs.resetForm.validate((valid) => {
					if (valid) {
						this.loading = true;
						editPwd(this.resetForm).then(res => {
							this.$message({
								message: res.msg,
								type: 'success'
							});
							this.$refs.resetForm.resetFields();
							this.loading = false;
						}).catch(err => {
							this.loading = false;
						})
					} else {
						return false;
					}
				});
			}
		}
	}
</script>

<style lang="scss" scoped>
	.user {
		padding: 24px;
		font-size: 14px;
		width: 100%;
		height: 100%;
		box-sizing: border-box;
		overflow-y: auto;
		position: relative;
		padding-bottom: 80px;

		.settings-container {
			max-width: 900px;
			margin: 0 auto;
		}

		.setting-card {
			background-color: var(--bg-tertiary);
			border-radius: 8px;
			padding: 24px;
			margin-bottom: 24px;
			box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
			transition: all 0.3s ease;

			&:hover {
				box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
			}

			.card-title {
				font-size: 18px;
				font-weight: 600;
				color: var(--text-primary);
				margin-bottom: 20px;
				padding-bottom: 12px;
				border-bottom: 2px solid var(--border-color);
			}

			.card-content {
				.info-item {
					display: flex;
					align-items: center;
					margin-bottom: 16px;
					padding: 8px 0;

					&:last-child {
						margin-bottom: 0;
					}

					.info-label {
						min-width: 100px;
						color: var(--text-muted);
						font-weight: 500;
					}

					.info-value {
						color: var(--text-primary);
						flex: 1;
					}
				}

				.config-item {
					margin-bottom: 16px;

					.config-label {
						color: var(--text-muted);
						margin-bottom: 12px;
						font-weight: 500;
					}

					.config-control {
						display: flex;
						align-items: center;
						flex-wrap: wrap;
						gap: 8px;
					}
				}

				.config-tip {
					margin-top: 12px;
					padding: 12px;
					background-color: var(--bg-input);
					border-radius: 4px;
					color: var(--text-muted);
					font-size: 13px;
					line-height: 1.6;
					display: flex;
					align-items: flex-start;

					i {
						margin-right: 8px;
						margin-top: 2px;
						color: #409eff;
					}
				}

				.el-form {
					max-width: 500px;

					.el-input {
						width: 100%;
					}
				}
			}
		}

		.setting-bottom {
			position: fixed;
			bottom: 0;
			left: 0;
			right: 0;
			padding: 16px;
			background-color: var(--bg-secondary);
			border-top: 1px solid var(--border-color);
			display: flex;
			align-items: center;
			justify-content: center;
			flex-wrap: wrap;
			gap: 16px;
			z-index: 10;

			.setting-bottom-item {
				font-size: 13px;
				color: var(--text-muted);
				
				a {
					color: #409eff;
					text-decoration: none;
					transition: color 0.3s ease;
				}
				
				a:hover {
					color: #66b1ff;
					text-decoration: underline;
				}
			}
		}
	}

	// 响应式设计
	@media (max-width: 768px) {
		.user {
			padding: 16px;
			padding-bottom: 100px;

			.setting-card {
				padding: 16px;

				.card-title {
					font-size: 16px;
				}

				.card-content {
					.info-item {
						flex-direction: column;
						align-items: flex-start;

						.info-label {
							margin-bottom: 4px;
						}
					}

					.config-item {
						.config-control {
							flex-direction: column;
							align-items: stretch;

							.el-input {
								width: 100% !important;
							}

							.el-button {
								margin-left: 0 !important;
								width: 100%;
							}
						}
					}

					.el-form {
						max-width: 100%;
					}
				}
			}

			.setting-bottom {
				flex-direction: column;
				gap: 8px;
				padding: 12px;
			}
		}
	}
</style>