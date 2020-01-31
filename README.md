# mpdb

Maya python Debugger

## Insatall 

I using a module installer method to install mpdb plugin, which could check [here](https://github.com/robertjoosten/maya-module-installer)   
All you need to do is pretty simple, follow the step below.
1. download the release version of the plugin. (you also can clone the release branch)
2. unzip the folder to any location in your computer.(skip this step if you clone the branch)
3. drag the install.mel to your running Maya viewport.

![alt](img/01.gif)

When you run the mel script once, the plugin will load every time you open Maya.    
You can use the [module manager](https://github.com/robertjoosten/maya-module-manager) to manage the plugin mod information.   

## Description

![alt](img/02.gif)

All the Icon have toolTip and statusTip tell you how to use it.

![alt](img/02_01.gif)

Middle Click Script Editor Icon can popup up the debug toolbar on the right side.

![alt](img/02_02.gif)

Click the setting icon can show up the Debugger Panel window.

![alt](img/02_03.png)

When you hit the breakpoint.     
Debugger Panel will display debugger information for the current running python file.      
CodeEditor on the right and the Scope Information on the left.     

## How to set breakpoint

the plugin fully base on the pdb moudle , you could think it as the pdb moudle wrap for maya and interact with Qt Widget.

```python
import mpdb
mpdb.set_trace()
```

Once the debug toolbar popup, you can import the mpdb moudle already.     
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

this is the code how I test the mpdb plugin.    
you can paste the code and run in the Script Editor Directly or you can load it as the moudle and import it.

![alt](img/03.gif)

If you run in the Script Editor directly, Plugin cannot find the code snippet inside maya,but you still could trace the variable and scope changed.

![alt](img/04.gif)

If you import the code,then it can trace the file content and show the code snippet on the left.

## Debug example 2

![alt](img/05.gif)

this is the example I test for the mayapy vsocde extension
when you debug code outside Maya that the debugger would freeze maya and maya no longer response to you .

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
this is a little modified version for mpdb moudle.

![alt](img/06.gif)

mpdb Module Debugger keep maya alive on the run time , awesome!~

![alt](img/07.gif)

And you also can modified the variable data on the run time

## Stop Button Feature

![alt](img/stop.png)

Stop Button has two stop debug feature

![alt](img/08.gif)

1. Left Mouse Click stop at the running line

![alt](img/09.gif)

2. Middle Mouse Click ignore all the set_trace breakpoints and keep running

## Setting Button Feature

![alt](img/setting.png)

Setting Button has three feature

![alt](img/02_02.gif)

1. Left Mouse Click can open the Debugger Panel window.

![alt](img/10.gif)

2. Middle Mouse Click pop up the pdb prompt dialog for pdb input. you can use the pdb command for debugging.

![alt](img/11.gif)

3. Right Mouse Click pop up Language Menu to switch different language mode. (I use the Qt i18n feature that allow the program change the Language on the run time)

## Script Editor Feature

1. Overwrite Execute and ExecuteAll Button

mpdb module overwrite the scriptEditorPanel type to fix some problems    
Maya2017 execute the scriptEditor code and hit the breakpoint will crash the Maya immediately   
With my effort, I find out that I use the maya.utils.processIdleEvents function to keep maya alive.   
However, Maya 2017 catch the execute event as the idle event and that will crash the maya after debug mode exit \_(:з」∠)_   
So I overwrite the execute button clicked event to fix this problems.   
the overwrite execute function running seamless like the maya original execute method,you probably do not feel it any way.

---

![alt](img/12.gif)

2. Add Ctrl + E shortcut for Execute Button

Sometimes I feel pretty annoying to click the execute button every single time.   
When I write something on the 3ds Max, I can press ctrl + E shrotcut to run the code.   
I think this pretty handy,however maya hotkey editor seem not possible to do that.   
so I use the Qt eventFilter to do this trick,when you focus on the Script Editor Window,then you can press Ctrl + E to run your code. 

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
- [ ]  完善 github readme 文档
- [ ]  弄一个 release 分支 在 github 上发布

## 无法解决的问题

- [ ] 使用 QThread 多线程加载窗口 减少加载卡顿 - 多线程无法减少卡顿，对比体验没有什么区别_(:з」∠)_
- [ ] Debug模式 红框包裹 Maya 主窗口 - 会挡住主窗口使用_(:з」∠)_
- [ ] reload scriptEditor 报错 - ImportError: reload(): module __main__ not in sys.modules
- [ ] 获取当前代码编辑器执行代码的内容 - 编辑器的函数是可以动态修改的，无法定位
