module.exports = {
    env: {
        browser: false,
        es6: true,
        node: true
    },
    extends: [
        'eslint:recommended'
    ],
    parserOptions: {
        ecmaVersion: 2020,
        sourceType: 'module'
    },
    rules: {
        'no-unused-vars': ['warn', { 'argsIgnorePattern': '^_' }],
        'no-console': 'off',
        'semi': ['warn', 'always'],
        'quotes': ['warn', 'single', { 'allowTemplateLiterals': true, 'avoidEscape': true }],
        'indent': ['warn', 4, { 'SwitchCase': 1 }],
        'no-trailing-spaces': 'warn',
        'comma-dangle': 'off',
        'no-multiple-empty-lines': ['warn', { 'max': 2 }],
        'eol-last': 'warn'
    },
    globals: {
        'vscode': 'readonly'
    }
};
