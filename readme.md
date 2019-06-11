# CMM语言解释器

[![](https://img.shields.io/github/repo-size/yeung66/cmm.svg)] [![](https://img.shields.io/github/stars/yeung66/cmm.svg?style=social)

本项目为武汉大学计算机学院软件工程专业大三课程《解释器构造与实践》的课程项目。

项目使用原生Python开发，功能包括词法分析，语法分析，语义分析，中间代码生成，中间代码解释执行。

本库包括

## 使用方法

```
python interpreter.py filename.cmm
```

直接调用最后的解释执行代码即可，该模块会自动调用前面的词法分析等模块作为后续操作的输入。亦可直接通过命令行调用Python文件单独执行前面的模块。

## 相关文档

## 码表

- 保留字
  `if`,`else`,`while`,`int`,`float`,`string`,`in`,`out`
- 运算符
  `+`,`-`,`*`,`\`,`=`,`|`,`&`,`^`,`<`,`<=`,`==`,`<>`,`&&`,`||`,`!`
- 数字
  `[0-9]+(.[0-9]+)?`
- 标识符
  `letter(letter|digit|_)*(letter|digit)`
- 字符串
  `"任意字符"`
- 分界符
  ​    `{`,`}`, `;`, `[`,`]`, `(`,`)`, `,`

## 文法

#### 入口

- PROGRAM -> STMTS
- STMTS-> STMT STMTS| BLOCK STMTS| $\varepsilon$

#### 语句与块

- STMT -> VARDECL | ASSIGNSTMT | IFSTMT | WHILESTMT | INSTMT |OUTSTMT
- BLOCK -> __{__STMTS**}**

#### 变量声明

- VARDECL ->NUMTYPE NUMVARLIST __;__ |

  ​			ARRAYTYPE VARLIST__;__|

  ​			__string__ STRVARLIST__;__

- NUMTYPE-> __int__ | __float__  

- ARRAYTYPE -> __int[NUM]__ | __float[NUM]__| __string[NUM]__

- VARLIST -> __ID__ OTHERID__;__

- OTHERID -> __, ID__ OTHERID | $\varepsilon$

- NUMVARLIST -> __ID__ OTHERNUMID__;__ | __ID__ __=__ EXPR OTHERNUMID__;__ 

- OTHERNUMID-> __, ID__ OTHERNUMID | __, ID__ __=__ EXPR OTHERNUMID |$\varepsilon$

- STRVARLIST-> __ID__ OTHERSTRID__;__  | __ID__ __=__ __STR__ OTHERSTRID__;__ 

- OTHERSTRID-> __, ID__ OTHERSTRID| __, ID__ __=__ __STR__ OTHERSTRID |$\varepsilon$

#### 赋值

- ASSIGNMENT -> VAR __=__ EXPR__;__  |VAR __= STR__;

#### 选择语句

- IFSTMT -> __if (__CONDITON__)__ BLOCK OTHERIFSTMT |

  ​		  __if (__CONDITON__)__ STMT OTHERIFSTMT	

- OTHERIFSTMT->__else__ STMT | __else__ BLOCK |$\varepsilon$

#### 循环语句

- WHILESTMT-> __while (__ CONDITION__)__ BLOCK | 

  ​			  __while (__ CONDITION__)__ STMT

#### 输入输出

- INSTMT->__in( ID );__
- OUTSTMT->__out(__(__STR__|EXPR)__)__

#### 条件

- CONDITION->COND OTHERCONDITION |__!(__CONDITION__)__
- OTHERCONDITION->LOGOP COND OTHERCONDITION | $\varepsilon$
- COND->EXPR COMPARE EXPR |__!(__COND__)__
- LOGOP->__&&__|__||__
- COMPARE-> __<__|__<=__ | __==__ | __<>__

#### 表达式

- EXPR->TERM OTHERTERM | __-__EXPR
- OTHERTERM->__+__ TERM OTHERTERM| __-__ TERM OTHERTERM | $\varepsilon$
- TERM -> FACTOR OTHERFACTOR
- OTHERFACTOR->__*__ FACTOR OTHERFACTOR |__/__ FACTOR OTHERFACTOR | $\varepsilon$
- FACTOR-> VAR | __NUM__|  __(__EXPR__)__
- VAR -> __ID__ | __ID[__EXPR__]__

### 中间代码

- `(JMP, condition, None, target) ` 条件跳转，不成立时跳转

- `(IN, None, None, None)` 进入代码块

- `(OUT, None, None, None)` 退出代码块

- `(READ, None, None, VAR)` 读取输入至变量

- `(WRITE, None, 0/1, STR/VAR/NUM)` 输出变量或表达式或字符串常量

- `(ASSIGN, VAR, 0/1, STR/VAR/NUM)` 变量赋值

- `(OP, left, right|None, result)` 运算结果，第三元为空时为单目运算

- `(int|float|string, ID, None|lenght, value|None)` 

  声明 第三元为数字时为声明数组，第四元不为空时表示初始化

