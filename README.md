fullstack-project/
├── frontend/               # Vue 3 项目
│   ├── src/
│   ├── public/
│   └── package.json
├── backend/                # Python 后端
│   ├── app.py              # Flask 主文件
│   ├── requirements.txt    # 依赖文件
│   ├── .venv/              # Python 虚拟环境
│   ├── data_processor.py   # 数据处理脚本
│   └── database.db         # 数据库文件
├── database/               # 数据库相关
│   ├── schema.sql          # 数据库表结构
│   └── er_diagram.pdm      # 数据库设计文件
└── scripts/                # 数据处理脚本
    └── data_processor.py   # 数据处理脚本


后端：激活虚拟环境 .venv\Scripts\activate    推出虚拟环境 deactivate
      启动flask程序  python app.py

前端：启动服务  npm run serve
