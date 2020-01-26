# mpdb

Maya python Debugger Tool

## todoList

- [x] ~~使用 helpline 类型的 toolbar workspace 组件~~
- [x] ~~重写脚本编辑器执行按钮功能，避免 Maya2107 执行崩溃问题~~
- [x] ~~执行按钮功能 脚本编辑器 textedit 滚动到最后~~
- [x] ~~debug 跳出 mpdb 模块的 frame~~
- [x] ~~toolbar 嵌入异常~~
- [x] ~~脚本编辑器 添加 ctlr + E 执行代码功能~~
- [x]  ~~完善 panel link path 显示~~
- [x]  ~~脚本编辑器按钮 鼠标中键 打开调试器~~
- [x]  ~~工具图标 鼠标中键 打开pdb输入模块进行自定义调试输入~~
- [x]  ~~中断执行添加鼠标中键实现跳过断点完成代码执行~~
- [x]  ~~数据接入到 Panel 上~~
- [x]  ~~点击 listwidget 的 item 切换 locals 数据~~
- [x]  ~~icon 添加 tooltip statusTip~~
- [x]  ~~修复 exec 执行代码导致 Qt 变量不在全局的问题~~ | 使用 maya.utils.executeInMainThreadWithResult 解决
- [x]  ~~多国语言版本~~
- [x]  ~~右键菜单切换语言~~
- [x]  ~~窗口名称多语言~~
- [x]  ~~通过 Qt 获取系统语言~~
- [x]  ~~变量调试 修改功能~~
- [x]  ~~pdb 模式刷新面板~~ | 重写 default 函数添加更新 locals
- [ ]  代码显示 gotoline 尝试
- [ ]  弄一个 release 分支 在 github 上发布

## 无法解决的问题

- [x] ~~中断执行不报错 - 略过错误无法停止代码运行~~ | 使用 executeInMainThreadWithResult 之后报错在这一行，可以通过 异常处理 抹除报错
- [ ] 使用 QThread 多线程加载窗口 | 减少加载卡顿 - 多线程无法提升加载速度，对比体验没有什么区别_(:з」∠)_
- [ ] Debug模式 红框包裹 Maya 主窗口 - 会挡住主窗口使用_(:з」∠)_
- [ ] reload scriptEditor 报错 - ImportError: reload(): module __main__ not in sys.modules
