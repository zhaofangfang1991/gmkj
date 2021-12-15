<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="listQuery.username" placeholder="姓名" style="width: 200px;" class="filter-item" @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.telnumber" placeholder="手机号" style="width: 200px;" class="filter-item" @keyup.enter.native="handleFilter" />
<!--       
      <el-select v-model="listQuery.importance" placeholder="Imp" clearable style="width: 90px" class="filter-item">
        <el-option v-for="item in importanceOptions" :key="item" :label="item" :value="item" />
      </el-select>
      <el-select v-model="listQuery.type" placeholder="Type" clearable class="filter-item" style="width: 130px">
        <el-option v-for="item in calendarTypeOptions" :key="item.key" :label="item.display_name+'('+item.key+')'" :value="item.key" />
      </el-select>
      <el-select v-model="listQuery.sort" style="width: 140px" class="filter-item" @change="handleFilter">
        <el-option v-for="item in sortOptions" :key="item.key" :label="item.label" :value="item.key" />
      </el-select> -->
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <!-- <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-edit" @click="handleCreate">
        创建
      </el-button> -->
      <el-button v-waves :loading="downloadLoading" class="filter-item" type="primary" icon="el-icon-download" @click="handleDownload">
        导出表格
      </el-button>
      <!-- <el-checkbox v-model="showReviewer" class="filter-item" style="margin-left:15px;" @change="tableKey=tableKey+1">
        审核员
      </el-checkbox> -->
    </div>

    <el-table
      :key="tableKey"
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 95%;"
      @sort-change="sortChange"
    >
      <el-table-column label="序号" prop="id" sortable="custom" align="center" width="80" :class-name="getSortClass('id')">
        <template slot-scope="{row}">
          <span>{{ row.id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="姓名" min-width="80px">
        <template slot-scope="{row}">
          <span class="link-type" @click="handleUpdate(row)">{{ row.username }}</span>
          &nbsp;&nbsp;<el-tag>{{ row.type | typeFilter }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="手机号" width="200px" align="center">
        <template slot-scope="{row}">
          <span>{{ row.telnumber }}</span>
        </template>
      </el-table-column>
      <!-- <el-table-column v-if="showReviewer" label="审核员" width="110px" align="center">
        <template slot-scope="{row}">
          <span style="color:red;">{{ row.reviewer }}</span>
        </template>
      </el-table-column> -->
      <el-table-column label="性别" align="center" width="95px">
        <template slot-scope="{row}">
          <span>{{ row.gender}}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" class-name="status-col" width="100px">
        <template slot-scope="{row}">
          <el-tag :type="row.status | statusColorFilter">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="最新操作时间" width="180px" align="center">
        <template slot-scope="{row}">
          <span>{{ row.uptime | parseTime('{y}-{m}-{d} {h}:{i}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="300px" class-name="small-padding fixed-width">
        <template slot-scope="{row,$index}">
          <el-button type="primary" size="mini" @click="handleUpdate(row)">
            编辑
          </el-button>
          <!-- <el-button v-if="row.status!='published'" size="mini" type="success" @click="handleModifyStatus(row,'published')">
            Publish
          </el-button>
          <el-button v-if="row.status!='draft'" size="mini" @click="handleModifyStatus(row,'draft')">
            Draft
          </el-button> -->
          <el-button v-if="row.status!='deleted'" size="mini" type="danger" @click="handleDelete(row,$index)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />

    <!-- 模态框 -->
    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="70px" style="width: 400px; margin-left:50px;">
        <el-form-item label="姓名" prop="username">
          <el-input v-model="temp.username" />
        </el-form-item>
        <el-form-item label="手机号" prop="telnumber">
          <el-input v-model="temp.telnumber" />
        </el-form-item>
        <el-form-item label="角色" prop="role_type">
          <el-select v-model="temp.role_type" multiple placeholder="请选择">
            <el-option
              v-for="item in roleTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="temp.status" class="filter-item" placeholder="请选择">
            <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="temp.gender" class="filter-item" placeholder="请选择">
            <el-option v-for="item in genderOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="密码" prop="password" placeholder="如果需要修改，请填入">
          <el-input v-model="temp.password" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          取消
        </el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">
          确认
        </el-button>
      </div>
    </el-dialog>

    <el-dialog :visible.sync="dialogPvVisible" title="Reading statistics">
      <el-table :data="pvData" border fit highlight-current-row style="width: 100%">
        <el-table-column prop="key" label="Channel" />
        <el-table-column prop="pv" label="Pv" />
      </el-table>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="dialogPvVisible = false">Confirm2</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { fetchList, create, deleteAccount, updateAccount } from '@/api/account'

import { fetchPv, createArticle, updateArticle } from '@/api/article'
import waves from '@/directive/waves' // waves directive
import { parseTime } from '@/utils'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination

// 身份配置
const calendarTypeOptions = [
  { key: '8', display_name: '管理员' },
  { key: '4', display_name: '维修人员' },
  { key: '2', display_name: '巡检人员' },
  { key: '1', display_name: '设备负责人' },
  { key: '12', display_name: '管理员  维修人员' },
  { key: '10', display_name: '管理员  巡检人员' },
  { key: '9', display_name: '管理员  设备负责人' },
  { key: '6', display_name: '维修人员  巡检人员' },
  { key: '5', display_name: '维修人员  设备负责人' },
  { key: '3', display_name: '巡检人员  设备负责人' },
  { key: '14', display_name: '管理员  维修人员  巡检人员' },
  { key: '13', display_name: '管理员  维修人员  设备负责人' },
  { key: '11', display_name: '管理员  巡检人员  设备负责人' },
  { key: '7', display_name: '维修人员  巡检人员  设备负责人' },
  { key: '15', display_name: '管理员  维修人员  巡检人员  设备负责人' }
]

// arr to obj, such as { CN : "China", US : "USA" }
const calendarTypeKeyValue = calendarTypeOptions.reduce((acc, cur) => {
  acc[cur.key] = cur.display_name
  return acc
}, {})

export default {
  name: 'ComplexTable',
  components: { Pagination },
  directives: { waves },
  filters: {
    statusColorFilter(status) {
      const statusMap = {
        '正常': 'success',
        '已删除': 'danger'
      }
      return statusMap[status]
    },
    typeFilter(type) {
      return calendarTypeKeyValue[type]
    },
  },
  data() {
    return {
      tableKey: 0,
      list: null,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20,
        // importance: undefined,
        // title: undefined,
        // type: undefined,
        // sort: '+id',
        username: undefined,
        telnumber: undefined
      },
      importanceOptions: [1, 2, 3],
      calendarTypeOptions,
      sortOptions: [{ label: 'ID Ascending', key: '+id' }, { label: 'ID Descending', key: '-id' }],
      statusOptions: ['正常', '已删除'],
      genderOptions: ['男', '女'],
      // showReviewer: false,
      temp: {
        id: undefined,
        status: '正常',
        remark: '',
        timestamp: new Date(),
        title: '',
        type: 1,
        gender: '男',
        telnumber: '',
        username: '',
        password: '',
        role_type: []
      },
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: '编辑',
        create: '创建'
      },
      dialogPvVisible: false,
      pvData: [],
      rules: {
        // type: [{ required: true, message: 'type is required', trigger: 'change' }],
        timestamp: [{ type: 'date', required: true, message: 'timestamp is required', trigger: 'change' }],
        title: [{ required: true, message: 'title is required', trigger: 'blur' }],
        username: [
          { required: true, message: '请输入员工姓名', trigger: 'blur' },
          { min: 2, max: 5, message: '长度在 2 到 5 个字符', trigger: 'blur' }
        ],
        telnumber: [{required: true,pattern: /^1[34578]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }],
        role_type: [
          { type: 'array', message: '请至少选择一个角色类型', trigger: 'change' }
        ],
        status: [
          { type: 'array', required: true, message: '请至少选择一个状态', trigger: 'change' }
        ],
        password: [
          { min: 6, max: 12, message: '长度在 6 到 12 个字符', trigger: 'blur' }
        ],

      },
      downloadLoading: false,

      roleTypeOptions: [{
        value: 8,
        label: '管理员'
      }, {
        value: 4,
        label: '维修人员'
      }, {
        value: 2,
        label: '巡检人员'
      }, {
        value: 1,
        label: '设备负责人'
      }],
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      fetchList(this.listQuery).then(response => {
        // console.log(response);
        this.list = response.items
        this.total = response.count

        this.listLoading = false
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handleModifyStatus(row, status) {
      this.$message({
        message: '操作Success',
        type: 'success'
      })
      row.status = status
    },
    sortChange(data) {
      const { prop, order } = data
      if (prop === 'id') {
        this.sortByID(order)
      }
    },
    sortByID(order) {
      if (order === 'ascending') {
        this.listQuery.sort = '+id'
      } else {
        this.listQuery.sort = '-id'
      }
      this.handleFilter()
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        importance: 1,
        remark: '',
        timestamp: new Date(),
        title: '',
        status: '正常',
        type: '',
        role_type:[],
        gender:''
      }
    },
    // handleCreate() {
    //   this.resetTemp()
    //   this.dialogStatus = 'create'
    //   this.dialogFormVisible = true
    //   this.$nextTick(() => {
    //     this.$refs['dataForm'].clearValidate()
    //   })
    // },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.temp.id = parseInt(Math.random() * 100) + 1024 // mock a id
          this.temp.author = 'vue-element-admin'
          createArticle(this.temp).then(() => {
            this.list.unshift(this.temp)
            this.dialogFormVisible = false
            this.$notify({
              title: 'Success',
              message: 'Created Successfully',
              type: 'success',
              duration: 2000
            })
          })
        }
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row) // copy obj
      this.temp.timestamp = new Date(this.temp.timestamp)
      
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.temp.role_type = row.role_type.split(',').map(Number)
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.temp)
          tempData.timestamp = +new Date(tempData.timestamp) // change Thu Nov 30 2017 16:41:05 GMT+0800 (CST) to 1512031311464
          // 处理role_type
          let typeValue = 0
          for (let i=0; i<tempData.role_type.length; i++){
            typeValue +=  tempData.role_type[i]
          } 
          tempData.typeValue = typeValue
          updateAccount(tempData).then((response) => {
            if (response.response_code == 2000) {
              const index = this.list.findIndex(v => v.id === this.temp.id)
              this.list.splice(index, 1, this.temp)
              this.dialogFormVisible = false
              this.temp.password = ''
              this.$notify({
                title: '成功！',
                message: '编辑成功',
                type: 'success',
                duration: 2000
              })              
            }
          })
        }
      })
    },
    handleDelete2(row, index) {
      this.$notify({
        title: 'Success',
        message: 'Delete Successfully',
        type: 'success',
        duration: 2000
      })
      this.list.splice(index, 1)
    },
    handleDelete(row, index) { // 执行后端 删除方法
      this.$confirm('你确定要删除该信息, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async() => {
        await deleteAccount(row.id)
        this.getList()
        this.$message({ type: 'success', message: '删除成功!' })
      }).catch(() => {
        this.$message({ type: 'success', message: '已取消删除' })
      })
    },
    handleFetchPv(pv) {
      fetchPv(pv).then(response => {
        this.pvData = response.data.pvData
        this.dialogPvVisible = true
      })
    },
    handleDownload() {
      this.downloadLoading = true
      import('@/vendor/Export2Excel').then(excel => {
        const tHeader = ['姓名', '手机号', '角色类型', '性别', '用户状态']
        const filterVal = ['username', 'telnumber', 'type', 'gender', 'status']
        const data = this.formatJson(filterVal)
        excel.export_json_to_excel({
          header: tHeader,
          data,
          filename: 'table-list'
        })
        this.downloadLoading = false
      })
    },
    formatJson(filterVal) {
      return this.list.map(v => filterVal.map(j => {
        if (j === 'timestamp') {
          return parseTime(v[j])
        }
        else if (j === 'type') {

          // const downloadTypeOptions2 = [
          //   [8 =  '管理员' ],
            // [4: '维修人员' ],
            // [2: '巡检人员' ],
            // [1: '设备负责人' ],
            // [12: '管理员  维修人员' ],
            // [10: '管理员  巡检人员' ],
            // [9: '管理员  设备负责人' ],
            // [6: '维修人员  巡检人员' ],
            // [5: '维修人员  设备负责人' ],
            // [3: '巡检人员  设备负责人' ],
            // [14: '管理员  维修人员  巡检人员' ],
            // [13: '管理员  维修人员  设备负责人' ],
            // [11: '管理员  巡检人员  设备负责人' ],
            // [7: '维修人员  巡检人员  设备负责人' ],
            // [15: '管理员  维修人员  巡检人员  设备负责人' ]
          // ],

          // alert(v[j]) downloadTypeOptions

          var downloadTypeOptions = {
            8:"管理员",
            4: '维修人员' ,
            2: '巡检人员' ,
            1: '设备负责人' ,
            12: '管理员  维修人员' ,
            10: '管理员  巡检人员' ,
            9: '管理员  设备负责人' ,
            6: '维修人员  巡检人员' ,
            5: '维修人员  设备负责人' ,
            3: '巡检人员  设备负责人' ,
            14: '管理员  维修人员  巡检人员' ,
            13: '管理员  维修人员  设备负责人' ,
            11: '管理员  巡检人员  设备负责人' ,
            7: '维修人员  巡检人员  设备负责人' ,
            15: '管理员  维修人员  巡检人员  设备负责人' 
          };
          return downloadTypeOptions[v[j]];
        }
        else {
          return v[j]
        }
      }))
    },
    getSortClass: function(key) {
      const sort = this.listQuery.sort
      return sort === `+${key}` ? 'ascending' : 'descending'
    },

  }
}
</script>
