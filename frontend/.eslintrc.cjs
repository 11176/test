// .eslintrc.js
module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true
  },
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@typescript-eslint/parser',
    ecmaVersion: 'latest',
    sourceType: 'module',
    extraFileExtensions: ['.vue']
  },
  extends: [
    'plugin:vue/vue3-recommended',
    '@vue/typescript/recommended' // 使用 Vue 官方提供的配置
  ],

  plugins: ['vue','@typescript-eslint'],
  // 添加这行关键配置 ↓↓↓
  globals: {
    defineProps: 'readonly',
    defineEmits: 'readonly',
    defineExpose: 'readonly',
    withDefaults: 'readonly'
  },
 rules: {
    'vue/no-parsing-error': [2, { 
      'x-invalid-end-tag': false,
      'invalid-first-character-of-tag-name': false
    }],
    'vue/html-self-closing': 'off' ,// 完全禁用规则
    'vue/comment-directive': 'off'
  },
  overrides: [
    {
      // 针对特定文件禁用规则
      files: ['vue.config.js'],
      rules: {
        '@typescript-eslint/no-var-requires': 'off',
        'import/no-commonjs': 'off'
      },
      env: {
        node: true // 声明这是 Node.js 环境
      }
    }
  ]
}