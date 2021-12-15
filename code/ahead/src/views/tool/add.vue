<template>
  <div class="form">
    <el-form ref="ruleForm" :model="ruleForm" :rules="rules" label-width="100px" class="demo-ruleForm">
      <el-form-item label="姓名" prop="username">
        <el-input v-model="ruleForm.username" />
      </el-form-item>
      <el-form-item label="手机号" prop="telnumber">
        <el-input v-model="ruleForm.telnumber" @blur="onRodeChange($event)" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="ruleForm.password" />
      </el-form-item>
      <el-form-item label="性别" prop="gender">
        <el-radio-group v-model="ruleForm.gender">
          <el-radio label="男" />
          <el-radio label="女" />
        </el-radio-group>
      </el-form-item>
      <el-form-item label="角色类型" prop="role_type">
        <el-checkbox-group v-model="ruleForm.role_type">
          <el-checkbox label="8" name="type" value="8"> 管理员</el-checkbox>
          <el-checkbox label="4" name="type" value="4"> 维修人员</el-checkbox>
          <el-checkbox label="2" name="type" value="2"> 巡检人员</el-checkbox>
          <el-checkbox label="1" name="type" value="1"> 设备负责人</el-checkbox>
        </el-checkbox-group>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm('ruleForm')">立即创建</el-button>
        <el-button @click="resetForm('ruleForm')">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>
<script>
// import { createSpiderTask } from "@/api/spider";
export default {
  data() {
    return {
      ruleForm: {
        username: '',
        telnumber: '',
        password: '',
        gender: '男',
        role_type: [],
      },
      rules: {
        username: [
          { required: true, message: '请输入员工姓名', trigger: 'blur' },
          { min: 2, max: 5, message: '长度在 2 到 5 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 12, message: '长度在 6 到 12 个字符', trigger: 'blur' }
        ],
        telnumber: [
          {
            required: true,
            pattern: /^1[34578]\d{9}$/, // 可以写正则表达式呦呦呦
            message: '请输入正确的手机号码',
            trigger: 'blur'
          }
        ],
        gender: [
          { required: true, message: '请选择性别', trigger: 'change' }
        ],
        role_type: [
          { type: 'array', required: true, message: '请至少选择一个角色类型', trigger: 'change' }
        ]
      },
    }
  },
  methods: {
    submitForm(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          // alert('submit!')
          // console.log(this.ruleForm.role_type, typeof this.ruleForm.role_type);
          // return false;
          this.loading = true
          this.$store.dispatch('account/create', this.ruleForm)
            .then(() => {
              // console.log("debugging..");
              // return false;
              this.$router.push({ path: this.redirect || '/account-manage/list', query: this.otherQuery })
              this.loading = false
            })
            .catch(() => {
              this.$message({ type: 'danger', message: '添加失败89' })  // 怎么让API的失败的理由传过来？
              this.loading = false
            })
        } else {
          console.log('error submit!!')
          return false
        }
      })
    },
    resetForm(formName) {
      this.$refs[formName].resetFields()
    },
    onRodeChange(event) {
      const telnumber = event.target.value
      const isTelnumber = /^1[34578]\d{9}$/.test(telnumber)
      if (isTelnumber) {
        this.ruleForm.password = telnumber.substring(telnumber.length - 6, telnumber.length)
      }
    }
  }
}
</script>

<style scoped>
.form {
  width: 60%;
  margin: 50px;
}
</style>

