<template>
	<div class="engine">
		<div class="loading-box content-none-data" v-loading="true" v-if="getLoading">加载中</div>
		<div v-else class="card-box">
			<div class="card-item" v-for="item in alistList">
				<div class="card-item-top">
					<el-image src="/alist.svg" fit="contain" style="width: 60px;height: 60px;"></el-image>
					<div style="margin-left: 12px;">
						<div class="card-item-user">{{item.userName}}
							<div class="card-item-remark" v-if="item.remark != null">[{{item.remark}}]</div>
						</div>
						<div class="card-item-url">{{item.url}}</div>
					</div>
				</div>
				<div class="card-item-bottom">
					<el-button size="small" type="primary" @click="editShowDialog(item)">编辑</el-button>
					<el-button size="small" type="danger" @click="delAlist(item.id)">删除</el-button>
				</div>
			</div>
			<div class="card-item card-add" @click="addShow" v-if="!getLoading">
				<template v-if="alistList.length == 0">
					暂无引擎，请<span style="color: #409eff;">新增</span>
				</template>
				<span v-else>新增</span>
			</div>
			<el-dialog :close-on-click-modal="false" :visible.sync="editShow" :title="editFlag ? '编辑' : '新增'" width="600px"
				:before-close="closeShow" :append-to-body="true">
				<div class="elform-box">
					<el-form :model="editData" :rules="editFlag ? editRule : addRule" ref="addRule" v-if="editShow"
						label-width="66px">
						<el-form-item prop="url" label="地址">
							<el-input v-model="editData.url" placeholder="请输入地址，如http://127.0.0.1:5244"></el-input>
						</el-form-item>
						<el-form-item prop="remark" label="备注">
							<el-input v-model="editData.remark" placeholder="备注方便你标识引擎，非必填"></el-input>
						</el-form-item>
						<el-form-item prop="token" label="令牌">
							<el-input v-model="editData.token" show-password
								:placeholder="`请输入令牌，${editFlag ? '留空表示不修改' : '请到AList管理-设置-其他中复制，保存后不要重置令牌'}`"
								@keyup.enter.native="submit"></el-input>
						</el-form-item>
					</el-form>
				</div>
				<span slot="footer" class="dialog-footer">
					<el-button @click="closeShow">取 消</el-button>
					<el-button type="primary" @click="submit" :loading="editLoading">确 定</el-button>
				</span>
			</el-dialog>
		</div>
	</div>
</template>

<script>
	import {
		alistGet,
		alistPost,
		alistPut,
		alistDelete
	} from "@/api/job";
	export default {
		name: 'Engine',
		components: {},
		data() {
			return {
				alistList: [],
				getLoading: false,
				deleteLoading: false,
				editLoading: false,
				editData: null,
				editFlag: false,
				editShow: false,
				editRule: {
					url: [{
						required: true,
						message: '请输入地址',
						trigger: 'blur'
					}, {
						pattern: /^https?:\/\/.+/,
						message: '请输入有效的HTTP/HTTPS地址',
						trigger: 'blur'
					}]
				},
				addRule: {
					url: [{
						required: true,
						message: '请输入地址',
						trigger: 'blur'
					}, {
						pattern: /^https?:\/\/.+/,
						message: '请输入有效的HTTP/HTTPS地址',
						trigger: 'blur'
					}],
					token: [{
						required: true,
						message: '请输入令牌，请到AList管理-设置-其他中复制，保存后不要重置令牌否则令牌失效',
						trigger: 'blur'
					}]
				}
			};
		},
		created() {
			this.getAlistList();
		},
		beforeDestroy() {},
		methods: {
			getAlistList() {
				this.getLoading = true;
				alistGet().then(res => {
					this.getLoading = false;
					this.alistList = res.data;
				}).catch(err => {
					this.getLoading = false;
				})
			},
			addShow() {
				this.editFlag = false;
				this.editData = {
					remark: '',
					url: '',
					token: ''
				}
				this.editShow = true;
			},
			editShowDialog(row) {
				this.editData = {
					...row,
					token: ''
				};
				this.editFlag = true;
				this.editShow = true;
			},
			closeShow() {
				this.editShow = false;
			},
			submit() {
				this.$refs.addRule.validate((valid) => {
					if (valid) {
						this.editData.url = this.ensureHttpPrefix(this.editData.url);
						this.editLoading = true;
						if (this.editFlag) {
							alistPut(this.editData).then(res => {
								this.editLoading = false;
								this.$message({
									message: res.msg,
									type: 'success'
								});
								this.closeShow();
								this.getAlistList();
							}).catch(err => {
								this.editLoading = false;
							})
						} else {
							alistPost(this.editData).then(res => {
								this.editLoading = false;
								this.$message({
									message: res.msg,
									type: 'success'
								});
								this.closeShow();
								this.getAlistList();
							}).catch(err => {
								this.editLoading = false;
							})
						}
					}
				})
			},
			delAlist(alistId) {
				this.$confirm("操作不可逆，将永久删除该引擎，请确认没有作业使用该引擎，否则会导致错误，仍要删除吗？", '提示', {
					confirmButtonText: '确定',
					cancelButtonText: '取消',
					type: 'warning'
				}).then(() => {
					this.deleteLoading = true;
					alistDelete(alistId).then(res => {
						this.deleteLoading = false;
						this.$message({
							message: res.msg,
							type: 'success'
						});
						this.getAlistList();
					}).catch(err => {
						this.deleteLoading = false;
					})
				});
			},
			ensureHttpPrefix(url) {
				if (!url) return url;
				url = url.trim();
				if (!/^https?:\/\//i.test(url)) {
					if (url.startsWith('//')) {
						return 'http:' + url;
					}
					return 'http://' + url;
				}
				return url;
			}
		}
	}
</script>

<style lang="scss" scoped>
	.engine {
		box-sizing: border-box;
		width: 100%;
		height: 100%;

		.loading-box {
			box-sizing: border-box;
			width: 100%;
			height: 100%;
		}

		.card-box {
			box-sizing: border-box;
			padding: 16px;
			display: grid;
			grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
			gap: 16px;
			width: 100%;
			height: 100%;
			overflow-y: auto;

			.card-item {
				background-color: var(--bg-tertiary);
				border-radius: 8px;
				border: 2px solid transparent;
				height: 140px;
				padding: 16px;
				transition: all 0.3s ease;
				display: flex;
				flex-direction: column;
				justify-content: space-between;

				.card-item-top {
					display: flex;
					align-items: center;
					flex: 1;

					.card-item-user {
						font-size: 18px;
						font-weight: 600;
						display: flex;
						align-items: center;
						color: var(--text-primary);
						margin-bottom: 8px;

						.card-item-remark {
							margin-left: 8px;
							color: #e6a23c;
							font-size: 14px;
							font-weight: 400;
							max-width: 150px;
							white-space: nowrap;
							overflow: hidden;
							text-overflow: ellipsis;
							padding: 2px 8px;
							background: rgba(230, 162, 60, 0.1);
							border-radius: 4px;
						}
					}

					.card-item-url {
						margin-top: 4px;
						font-size: 13px;
						color: var(--text-muted);
						word-break: break-all;
					}
				}

				.card-item-bottom {
					display: flex;
					align-items: center;
					justify-content: flex-end;
					gap: 8px;
					padding-top: 12px;
					border-top: 1px solid var(--border-color);
				}
			}

			.card-add {
				font-size: 24px;
				cursor: pointer;
				display: flex;
				justify-content: center;
				align-items: center;
				color: var(--text-muted);
				font-weight: 500;
				transition: all 0.3s ease;

				span {
					transition: all 0.3s ease;
				}
			}

			.card-item:hover {
				border-color: #409eff;
				background-color: var(--bg-input);
				transform: translateY(-2px);
				box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
			}

			.card-add:hover {
				color: #409eff;
				background-color: var(--bg-input);
				border-color: #409eff;
				
				span {
					transform: scale(1.1);
				}
			}
		}
	}

	// 响应式设计
	@media (max-width: 768px) {
		.engine {
			.card-box {
				grid-template-columns: 1fr;
				padding: 12px;
				gap: 12px;

				.card-item {
					height: auto;
					min-height: 120px;

					.card-item-top {
						flex-direction: column;
						align-items: flex-start;

						.card-item-user {
							font-size: 16px;
							flex-wrap: wrap;

							.card-item-remark {
								margin-left: 0;
								margin-top: 4px;
								max-width: 100%;
							}
						}
					}

					.card-item-bottom {
						justify-content: center;
						flex-wrap: wrap;
					}
				}
			}
		}
	}
</style>