# mpdb

Maya python Debugger Tool

## Insatall 

I using a module installer method to install mpdb plugin, which could check [here](https://github.com/robertjoosten/maya-module-installer)
All you need to do is pretty simple, follow the step below.
1. download the release version of the plugin. 
2. unzip the file to any location in your computer.
3. drag the install.mel to your running Maya viewport.


![alt](img/01.gif)

When you run the mel script once, the plugin will load every time you open Maya.
You can use the [module manager](https://github.com/robertjoosten/maya-module-manager) to manage the plugin mod information.

## Description

![alt](img/02.gif)

All the Icon have toolTip and statusTip tell you how to use it.

Middle Click Script Editor Icon can popup up the debug toolbar on the right side.
Click the setting icon can show up the Debugger Panel window.



## How to set breakpoint

the plugin is complete rely on the pdb moudle , you could think it as the pdb moudle wrap for maya and interact with Qt Widget.

```python
import mpdb
mpdb.set_trace()
```

Once the debug toolbar popup, you can import my mpdb moudle already.
And how it work is exactly the same as python pdb moudle.

When you use the set_trace method, the next running line will set breakpoint.

## Debug example 1

```Python
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

this is the code how I test the plugin.
you can paste the code and run in the Script Editor Directly or you can load it as the moudle and import it.

![alt](img/03.gif)

If you run in the Script Editor directly, Plugin cannot find the code snippet inside maya,but you still could trace the variable and scope changed.

![alt](img/04.gif)

If you import the code,then I can trace the file content and show the code snippet on the left.

## Debug example 2

![alt](img/05.gif)

this is the example I test for the mayapy vsocde extension
when you debug code outside Maya that the debugger would freeze maya and you no longer interact with maya.

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
this is little modified version for mpdb.
And mpdb moudle could fix all the unfriendly problems.

![alt](img/06.gif)

You can modified everything on the run time , awesome!~

![alt](img/07.gif)

And you can modified the variable data on the run time



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
- [x]  ~~跳过 mpdb 内部文件的追踪~~
- [ ]  正则过滤 修改变量 修改错误的问题
- [ ]  完善 github readme 文档
- [ ]  弄一个 release 分支 在 github 上发布

## 无法解决的问题

- [x] ~~中断执行不报错 - 略过错误无法停止代码运行~~ | 使用 executeInMainThreadWithResult 之后报错在这一行，可以通过 异常处理 抹除报错
- [ ] 使用 QThread 多线程加载窗口 | 减少加载卡顿 - 多线程无法提升较少卡顿，对比体验没有什么区别_(:з」∠)_
- [ ] Debug模式 红框包裹 Maya 主窗口 - 会挡住主窗口使用_(:з」∠)_
- [ ] reload scriptEditor 报错 - ImportError: reload(): module __main__ not in sys.modules
- [ ] 获取当前代码编辑器执行代码的内容 | 编辑器的函数是动态修改的，无法定位的
