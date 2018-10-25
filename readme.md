# 词法分析器
## 相关码表
- 保留字
     `if`,`else`,`while`,`int`,`float`,`string`,`in`,`out`
- 运算符
     `+`,`-`,`*`,`\`,`=`,`|`,`&`,`^`,`<`,`<=`,`==`,`<>`,`&&`,`||`,`!`
- 数字
     `[0-9]+`
- 标识符
     `letter(letter|digit|_)*(letter|digit)`
- 字符串
     `"任意字符"`
- 分界符
  ​    `{`,`}`, `;`, `[`,`]`, `(`,`)`, `,`, `.`
## 开发环境
- python3.6
- windows10
## 运行方式
程序已经打包成exe文件（lexer.exe),可以直接双击运行，但建议使用cmd命令提示符用`./lexer.exe`命令运行，因为直接双击运行，控制台会在程序结束后就消失，可能会看不清楚。进入程序后根据提示输入测试文件目录即可。
## 测试文件
- 正确且全面的测试文件 `test/lexer/sample.cmm`
- 各种错误类型测试文件
    - 无法识别字符 `test/lexer/unknown_word.cmm`
    - 非法标识符 `test/lexer/wrong_id.cmm`
    - 注释未结束 `test/lexer/notend_comment.cmm`
    - 字符串未结束 `test/lexer/notend_string.cmm`