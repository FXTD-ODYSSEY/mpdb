# mpdb

Maya Python 代码调试器   
TD 和 TA 调试 Maya Python 代码的福音

[en_US](./README.md) | [zh_CN](./README_zh_CN.md)


## 安装 

我使用了 Maya 的模块安装方法，借助 rj 大神的力量，可以去他的 [github仓库](https://github.com/robertjoosten/maya-module-installer)查阅。    
你只需要按照下面的步骤进行操作即可：

1. 在 Github 上下载发布的插件压缩包 （或者将 release 分支克隆到本地）
2. 将压缩包解压到任意路径上（建议路径保持全英文）(如果是克隆分支的不需要解压操作)
3. 将 install.mel 拖拽到 Maya 的视窗上 

![alt](img/0.gif)

![alt](img/01.gif)

当你安装成功之后，你每次打开 Maya 插件就会自动开启。   
如果你想要管理好模块，也可以借助 rj 大神的的[模块管理器](https://github.com/robertjoosten/maya-module-manager)来进行管理

## 介绍

![alt](img/02.gif)

所有图标都有提示，告诉你如何使用 （右键扳手设定图标可以切换语言）

![alt](img/02_01.gif)

鼠标中键点击脚本编辑器按钮可以重新将调试工具架打开并且放到右侧的区域。

![alt](img/02_02.gif)

点击设定图标可以打开 Maya调试面板

![alt](img/02_03.png)

当你触发断点的时候，调试面板就会显示相关的信息。   
左边是代码信息显示右边是的函数和域信息显示。

## 如何设置断点

这个插件是基于 Python 的 pdb 模块开发的，你可以认为它就是 pdb 的 Maya 特供版本，通过 Qt 组件进行更方便的交互。

```python
import mpdb
mpdb.set_trace()
```

只要调试工具架打开了，你就可以 import mpdb 了。   
它的使用方法和 pdb 模块如出一辙的。

## 调试例子 1

```Python
import mpdb

def add(a,b):
    print (a,b)
    return a+b

def mul(a,b):
    print (a,b)
    return a*b

def main():
    mpdb.set_trace()
    a = 1
    b = 2

    c = add(a,b)

    mpdb.set_trace()
    d = mul(c,b)

    print (a,b,c,d)
    return a,b,c,d

if __name__ == "__main__":
    mpdb.set_trace()
    main()
    print "done"
```

这段代码就是我用来测试 mpdb 插件用的   
你可以将代码复制到 Maya 的脚本编辑器上 或者 是通过导入模块的方式执行。

![alt](img/03.gif)

如果你直接将代码粘贴到脚本编辑器运行，插件无法遭到运行的代码，不过你还是可以看到变量和域的信息。

![alt](img/04.gif)

如果是通过 import 的方式导入的代码，插件可以追踪到文件的路径读取文件的内容显示在左侧的面板上。

## 调试例子 2

![alt](img/05.gif)

上面的截图是我用来测试 mayapy VScode 插件的代码。    
当你使用外部的代码调试器的时候，不可避免会导致 Maya 无响应，失去交互的途径。

```Python
import mpdb
import pymel.core as pm

crv = pm.circle(ch=0)[0]

for cv in crv.cv:
    pos = cv.getPosition(space="world")
    loc = pm.spaceLocator(p=pos)
    mpdb.set_trace()
    print (loc,pos)
```
这个代码就是在上面的测试代码上基于 mpdb 模块量身定做调整的代码

![alt](img/06.gif)

mpdb 模块可以在调试过程中，保持Maya的响应。 挖藕、凹森~ 运用自如~

![alt](img/07.gif)

并且你可以在调试模式下修改变量的值！~   
（只适合修改 python 基础类型的变量 如果是 OpenMaya 之类的特殊类型变量修改可能导致报错甚至 Maya 崩溃哦）

## 终止按钮功能

![alt](img/stop.png)

终止按钮有两个不同的终止调试功能

![alt](img/08.gif)

1. 左键点击会立刻在当前运行的代码跳出终止

![alt](img/09.gif)

2. 中键点击会忽略掉后续所有的断点一直执行到结束。

## 设定按钮功能

![alt](img/setting.png)

设定按钮有三个功能

![alt](img/02_02.gif)

1. 左键点击打开 Maya调试面板

![alt](img/10.gif)

2. 中键点击打开 pdb 模式输入窗口，可以输入 pdb 命令进行调试

![alt](img/11.gif)

3. 右键点击弹出语言切换菜单，切换不同语言（这里我使用了 Qt i18n 的功能可以动态修改所有显示的文字）

## 脚本编辑器的修改

1. 重写了 Execute 和 ExecuteAll 按钮的功能

mpdb 模块重写了 scriptEditorPanel 的面板类型来修复一些 Bug。   
Maya 2017 执行脚本编辑器的代码来触发断点会导致 Maya 崩溃。   
通过我的一番努力，我找到了问题的原因。   
我是使用 maya.utils.processIdleEvents 来让 Maya 保持响应的。    
然而 Maya2017 执行代码的时候会捕获执行事件为 idle 事件导致代码重复执行，这也直接导致退出debug模式之后 Maya 立即崩溃_(:з」∠)_    
所以我重写了两个执行按钮的功能，用 Python 的方式实现代码的执行而不会导致崩溃。   
使用的时候基本上是感受不出来的，因为我已经尽量将原生的代码执行效果还原了。

---

![alt](img/12.gif)

2. 添加 Ctrl + E 快捷键来执行代码

有时候我觉得 Maya 每次执行代码都要点击执行按钮是挺烦的。   
我用 3ds Max 的时候可以通过 Ctrl + E 快捷键来执行代码，我觉得还是挺方便的。   
然而 Maya 的热键编辑器貌似还实现不了这样的操作。   
所以我通过 Qt 的 eventFilter 来实现。   
只要让脚本编辑器在选中状态下按 Ctrl + E 就可以执行当前代码   

## TodoList

- [x] ~~使用 helpline 类型的 toolbar workspace 组件~~
- [x] ~~重写脚本编辑器执行按钮功能，避免 Maya2107 执行崩溃问题~~ - 修改 scriptEditorPanel 的添加窗口 mel 函数 实现窗口自定义
- [x] ~~执行按钮功能 脚本编辑器 textedit 滚动到最后~~
- [x] ~~debug 跳出 mpdb 模块的 frame~~
- [x] ~~toolbar 嵌入异常~~ - 貌似是 Maya2017 的窗口记录导致的 判断 workspaceControl 的存在 先删除再创建即可
- [x] ~~脚本编辑器 添加 ctlr + E 执行代码功能~~ 
- [x]  ~~完善 panel link path 显示~~
- [x]  ~~脚本编辑器按钮 鼠标中键 打开调试器~~
- [x]  ~~工具图标 鼠标中键 打开pdb输入模块进行自定义调试输入~~
- [x]  ~~数据接入到 Panel 上~~
- [x]  ~~点击 listwidget 的 item 切换 locals 数据~~
- [x]  ~~icon 添加 tooltip statusTip~~
- [x]  ~~多国语言版本~~
- [x]  ~~右键菜单切换语言~~
- [x]  ~~窗口名称多语言~~
- [x]  ~~通过 Qt 获取系统语言~~
- [x]  ~~变量调试 修改功能~~
- [x]  ~~pdb 模式刷新面板~~ - 重写 default 函数添加更新 locals
- [x]  ~~跳过 mpdb 内部文件的追踪~~  - MPDB 进入 interaction 进行追踪过滤
- [x]  ~~正则过滤导致修改变量 修改错误的问题~~ - 获取左侧的 header 编号解决定位问题
- [x]  ~~修复 exec 执行代码导致 Qt 变量不在全局的问题~~ - 将 globals() 传入变量解决
- [x] ~~中断执行不报错 - 略过错误无法停止代码运行~~ - ~~使用 executeInMainThreadWithResult 之后报错在这一行，可以通过 异常处理 抹除报错~~ - 导致插件 Debug 模式执行代码卡死
- [x]  ~~解决关闭插件卡死问题 2020-1-30~~ - 使用 sys.exit() 退出程序不执行代码
- [x]  ~~中断执行添加鼠标中键实现跳过断点完成代码执行 2020-1-30~~ - mpdb模块添加 quitting 变量 代码编辑器运行的代码最后设定为 False ，中途设定为 True 跳过所有 set_trace 断点
- [x]  ~~完善 github readme 文档~~
- [x]  ~~github readme 文档 中文版~~
- [ ]  弄一个 release 分支 在 github 上发布

## 无法解决的问题

- [ ] 使用 QThread 多线程加载窗口 减少加载卡顿 - 多线程无法减少卡顿，对比体验没有什么区别_(:з」∠)_
- [ ] Debug模式 红框包裹 Maya 主窗口 - 会挡住主窗口使用_(:з」∠)_
- [ ] reload scriptEditor 报错 - `ImportError: reload(): module __main__ not in sys.modules`
- [ ] 获取当前代码编辑器执行代码的内容 - 编辑器的函数是可以动态修改的，无法定位
