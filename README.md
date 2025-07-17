## 项目结构

```
fullstack-project/
├── frontend/               # Vue3
│   ├── public/
│   ├── src/
│   |   |—— assets/
│   |   |—— components/
│   │   ├── services/       # 新增：API服务层
│   |   |   |—— TradeService.js  
│   |   |   |—— api.js  
│   │   ├── router/
│   |   |   |——index.js
│   │   ├── views/
│   │   └── App.vue
│   └── vue.config.js       # 新增：代理配置
├── backend/
│   ├── api/                # 路由层
│   |   |——trade_api.py
│   ├── core/               # 业务逻辑
│   |   |—— TradeTable.py   # 数据处理脚本
│   |   |—— config.py       # 数据库连接环境配置
│   |   |—— models.py        
│   ├── data/
│   |   |—— database.sql
│   |   |—— 订单信息列表-样例数据.csv
│   ├── app.py              # Flask初始化
│   ├── requirements.txt
│   ├── venv/       
└── scripts/                # 独立脚本
```

我有一个这个结构的全栈项目，目前已经完成了前后端以及数据库的构建（vue3+python+mysql），目的是完成一个对订单信息表的分析，通过前端点击按钮调用数据处理脚本分析数据库数据，反馈回前端。

## 前端

启动服务  `npm run serve`

## 后端

激活虚拟环境 `.venv\Scripts\activate`

退出虚拟环境 `deactivate`

下载所有依赖库 `pip install -r requirements.txt`

启动flask程序  `python app.py`
