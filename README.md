# PySimpleTest -- Make test as simple as possible

## 1  Why PySimpleTest
If you are suffering from writting just a simple for loop in **Robot Framework**, or if you are suffering from figuring out how fixture be called in **PyTest**, you come to the right place.

**PySimpleTest** use native python grammar and logic and make test very easy. It has following advantages:

* Use native python interpreter (not like pytest or robot framework).
* Only provide functions. No class, fixture, decorator or other weird things.
* Provide "super-realism" assertion system such as `should_become_true`, `should_keep_true`.
* Provide article liked log system. You can use `section`, `subsection`, ... to organize your test report.
* Provide many test assistant functions like `wait` with GUI progress bar, `say` to speake string out.
* Provide manual operation request functions like `please` and `please_check`
* Colored cmd output to indicate <font color="red">Fail</font>, <font color="green">Pass</font>, <font color="red">Error</font>, etc.
* Log file with link information. If you use editor like Sublime, can realize double-click test report line to jump to corresponding code.

So for writting small test, PySimpleTest is a good choice. In addition, you can find PyPI index at: [https://pypi.org/project/PySimpleTest/](https://pypi.org/project/PySimpleTest/)

## 2  Getting Start
Write a file `main.py`:
```python
import PySimpleTest as pst

a = 2
pst.should_be_equal(a, 2)
pst.should_be_less(a, 1)
```
Then run it. You can get following cmd output:  
<div align="center">
<img src="https://s1.ax1x.com/2020/08/15/dkoHfS.png" width="350">
</div>

And you can see 3 output file: `main.log`, `main.info` and `main.linfo`:

* `main.info` has the same content as console output.
* `main.linfo` has the same content as `main.info` but with `<file>:<line-number>` link information. It's for double-click jump purpose. See details in section [External Configuration](#sec_External_Configuration)
* `main.log`: `info` function will not save into `.log` file. See details in [info](#func_info) function description

So what functions can I use just like `should_be_equal` and `should_be_less`? See in section [Function List](#sec_Function_List)

## 3  <label id="sec_Function_List">Function List</label>
This section will introduce all functions provided by `PySimpleTest`

### 3.1  Assertion System
For all assertion functions, will return `True` when Pass, return `False` when Fail. These function are listed below:

* `should_be_true(expression)`:  
If `expression` is True, it will print "<font color="green">Pass: (&lt;expression&gt;) is True</font>" and log in three output files.
Else "<font color="red">Fail: (&lt;expression&gt;) is False</font>" will be printed and logged.
* `should_be_false(expression)`: Pass when `expression` is False.
* `should_be_equal(value1, value2)`: Pass when `value1 == value2`.
* `should_not_be_equal(value1, value2)`: Pass when `value1 != value2`.
* `should_be_less(value1, value2)`: Pass when `value1 < value2`.
* `should_not_be_less(value1, value2)`: Pass when `value1 >= value2`.
* `should_be_greater(value1, value2)`: Pass when `value1 > value2`.
* `should_not_be_greater(value1, value2)`: Pass when `value1 <= value2`.
* `should_be_approx(value1, value2, tolerance = 5, func = abs)`: Pass when `func(value1-value2) <= tolerance`.
* `should_not_be_approx(value1, value2, tolerance = 5, func = abs)`: Pass when `func(value1-value2) > tolerance`.
* `should_keep_true(expression, duration)`: Pass when `expression` keeps True for `duration` seconds.
Try following example:
```python
import PySimpleTest as pst
import time

start_time = time.time()
pst.should_keep_true(time.time()-start_time < 3, 2)

start_time = time.time()
pst.should_keep_true(time.time()-start_time < 3, 5)
```
* `should_keep_false(expression, duration)`: Pass when `expression` keeps False for `duration` seconds.
* `should_become_true(expression, timeout)`: Pass when `expression` becomes True in `timeout` seconds.
* `should_become_false(expression, timeout)`: Pass when `expression` becomes False in `timeout` seconds.
* `should_raise(expression, exception=None)`: Pass when `expression` raise a exception.
    * If parameter `exception` is `None`, all exceptions raised will be passed;
    * If parameter `exception` is an exception type such as `ZeroDivisionError`, all exceptions that are the instance of such type raised will be passed;
    * If parameter `exception` is an exception instance such as `BaseException()`, only exception that just the same with such exception instance raised will be passed;
Try following example:
```python
import PySimpleTest as pst

pst.should_raise(lambda:1/0)
pst.should_raise(lambda:1/0, ZeroDivisionError)
pst.should_raise(lambda:1/0, NameError)
pst.should_raise(lambda:1/0, ZeroDivisionError("division by zero"))
```
* `should_not_raise(expression)`: Pass when `expression` dosen't raise any exception;
* `should_keep_raising(expression, duration, interval=0.1, exception=None)`: Pass when `expression` keeps raising `exception`;
* `should_keep_not_raising(expression, duration, interval=0.1)`: Pass when `expression` keeps raise nothing;
* `should_become_raising(expression, timeout=480, interval=0.1, exception=None)`: Pass when `expression` raise `exception` in `timeout` seconds;
* `should_become_not_raising(expression, timeout=480, interval=0.1)`: Pass when `expression` become not raising anything in `timeout` seconds;

> In above function list, all parameter named with `expression` can be a normal expression or a lambda expression. But you can only use lambda expression in Python console mode.

> Every function start with `should_` has it's blocked version start with `must_`. For example, `must_be_true(expression)`. `must_*` functions do the same thing as `should_*` functions only except when assertion is failed, `must_*` function will raise an `AssertionError` with fail message.

### 3.2  Logging System

* `log(*args, **kwargs)`:  
Use `log` just like `print`. It will print in console as well as write into log file. For example:
```python
a = {"key": 5}
log("a =", a)
```
Default log file has the same base name with your python script but with expand name ".log" lays in the same folder with your python script. If you want to change path, use `--logfile` argument. See details in [Terminal Arguments](#sec_Terminal_Arguments).  
In addition to `print`, `log` support color print, you can use `color` and `style` argument to control the print format. For example:
```
log("I am here!", color = "red", style = "highlight")
```
`color` can choose in list: `["black", "red", "green", "yellow", "blue", "purple", "cyan", "white"]`  
`style` can choose in list: `["default", "highlight", "underline", "shining", "anti"]`

* <label id="func_info">`info(*args, **kwargs)`</label>:  
Use `info` just like `log`. `info` will not write into `.log` file but into `.info` file. In fact, `log` will also write into `.info` file. Providing `info` function is aim to keep `.log` file clean. You can use `info` to print and note some assistant information. It will not disturb main test log file.

* `section(name, level = 1)`:  
To make following log with one level indent. For example:
```python
section("Test eval function")

section("eval single value", level = 2)
should_be_equal(eval("1"), 1)
should_be_equal(eval("1.2"), 1.2)
should_be_equal(eval("-3.6"), -3.6)
should_be_equal(eval("True"), True)

section("eval math expression", level = 2)
should_be_equal(eval("3 + 5*2"), 13)
should_be_equal(eval("(6-2)*5"), 20)
```
Above code will have following output:
<div align="center">
<img src="https://s1.ax1x.com/2020/08/15/dkoxwq.png" width="550">
</div>

* `subsection(name)`: Same as `section(name, level = 2)`
* `subsubsection(name)`: Same as `section(name, level = 3)`
* `subsubsubsection(name)`: Same as `section(name, level = 4)`
* `subsubsubsubsection(name)`: Same as `section(name, level = 5)`
* `end_section()`: Will go back one level indent for following log. For example:
```python
log("line 1")
log("line 2")

section("section")
log("line 3")
log("line 4")
subsection("subsection")
log("line 5")
log("line 6")
end_section()
log("line 7")
log("line 8")
end_section()
log("line 9")
```
Above code will have following output. You can see that after `end_section()`, `line 7` and following log go back one level's indent, `line 9` and following log also go back one level's indent.
<div align="center">
<img src="https://s1.ax1x.com/2020/08/15/dko7Y8.png" width="350">
</div>

Also, you can use leveled section using class `Section`. For above example, you can rewrite in this way:

```python
log("line 1")
log("line 2")

with Section("section"):
    log("line 3")
    log("line 4")
    with Section("subsection")
        log("line 5")
        log("line 6")
    log("line 7")
    log("line 8")
log("line 9")
```

It can also generate the same result as above figure. This is the recommanded way to use leveled section. Because result out log will have the same indent layout with the source code.
### 3.3  Header/Tailer information control
In a test report, following figure shows the header and tailer information position:
<div align="center">
<img src="https://s1.ax1x.com/2020/08/15/dkoLlQ.png" width="550">
</div>

You can use following functions to control the output of Header/Tailer information:

* `title(name)`: to specify title in header information. If it is not used, title message in header information will use script base name.
* `author(name)`: to specify test author in header information. If it is not used, author will use your system user name.
* `version(name)`: Specify production version in header information.
* `url(link)`: Specify url in header information.
* `header_info[key] = value`: You can log more other "`<key>: <value>`" liked items in header information. For example:
```
header_info["Reviewer"] = "Eason"
```
* `tailer_info[key] = value`: In the same way, you can use `tailer_info` to log more "`<key>: <value>`" liked tailer information.

### 3.4  Test Assistant System

* `Pass(message)`: Same as `log("Pass:", message, color="green", style="highlight")`
* `Fail(message)`: Same as `log("Fail:", message, color="red", style="highlight")`
* `Skip(message)`: Same as `log("Skip:", message, color="green", style="highlight")`
* `wait(duration)`: Wait `duration` seconds. If `gui_on()` is called before and `duration` is greater than 10, The progress bar will pop out to indicate progress and time remain. Just like following figure:
<div align="center">
<img src="https://s1.ax1x.com/2020/08/15/dkovmn.png" width="500">
</div>

* `wait_until(expression, timeout=480, interval=0.1, must=False)`: Wait until `<expression>` becomes True. If time waited more than `timeout`, it will stop waiting. `interval` indicate the time interval between two times `eval` of `<expression>`. If `must` is True, it will raise an `AssertionError` when timeout is reached.  
* `wait_until_not(expression, timeout=480, interval=0.1, must=False)`: Similar with `wait_until`. Just to wait `<expression>` become False.  
* `wait_until_raise(expression, exception=None, timeout=480, interval=0.1, must=False)`: Wait until `<expression>` raise `exception`.
* `wait_until_not_raise(expression, timeout=480, interval=0.1, must=False)`: Wait until `<expression>` not raise any exceptions.
* `please(do_something)`: If `gui_on()` is called before, it will pop up a message box to indicate you to do some manual operation. For example:
```python
please("reboot machine 1")
```
Then it will pop up following message box and wait you finish manual operation then click `OK` button.
<div align="center">
<img src="https://s1.ax1x.com/2020/08/15/dkoOyj.png" width="200">
</div>
If `gui_on()` is not called before, a console prompt will indicate you to enter after you finished manual operation.

* `please_check(something)`: If `gui_on()` is called before, it will pop up a message box to indicate you to do some manual check. This window will have two buttons: `Yes` and `No`:
    * If you click `Yes`, it will log "<font color="green">Pass: (&lt;somthing&gt;) is True</font>".
    * If you click `No`, it will log "<font color="red">Fail: (&lt;something&gt;) is False</font>".
<div align="center">
<img src="https://s1.ax1x.com/2020/08/15/dkoXOs.png" width="200">
</div>
If `gui_on()` is not called before, a console prompt will indicate you to input yes or no.

* `say(message)`: If `void_on()` is called before, you can use `say` to speak out message.

### 3.5  Configuration System

* `color_on()`: To turn on coloring console output. If your console out is just like following figure:
<div align="center">
<img src="https://s1.ax1x.com/2020/08/15/dkoqSg.png" width="400">
</div>

that means your console not support ASCII escape characters. Please use `color_off()` to turn off color. The default coloring print status is enabled.
* `color_off()`: To turn off coloring console output.
* `voice_on()`: To turn on voice. If voice is enable:
    * a voice will say "Fail" when assertion failed;
    * a voice will say out Exception Type when an internal exception is raised;
    * a voice will say "Please &lt;do something&gt;" when `please` is called;
    * a voice will say "Please check &lt;something&gt;" when `please_check` is called. 
* `voice_off()`: To turn off voice. If voice is disable, nothing will speak out only except you use `say` function. The voice default status is disabled.
* `gui_on()`: To turn on gui. If gui is enable:
    * a message box will pop up when `please` or `please_check` is called;
    * a progressbar will pop up when `wait` or `should/must_keep_true/false` is called;

## 4  <label id="sec_Terminal_Arguments">Terminal Arguments</label>
If you import `PySimpleTest`, you can use some terminal arguments to configure some thing. The terminal arguments formats is as following:
```
$ python <script>.py [--logfile <path>] [--infofile <path>] [--linfofile <path>] [--color {on|off}] [--voice {on|off}] [--gui {on|off}] [--title <name>] [--author <name>] [--version <name>] [--url <link>]
```
For example, when execute your script, use following command to log author name in log file:
```
$ python <script>.py --author Bruce
```
All supported arguments description are list here:

* `--logfile <path>`: to specify log file store path.
* `--infofile <path>`: to specify info file store path.
* `--linfofile <path>`: to specify linfo file store path.
* `--color {(on)|off}`: to decide console coloring output is on or off. Just like use `color_on()` or `color_off()` inside script. Default option is color on.
* `--voice {on|(off)}`: to decide voice enable or disable. Just like use `voice_on()` or `voice_off()` inside script. Default option is voice off.
* `--gui {on|(off)}`: to decide gui enable or disable. Just like use `gui_on()` or `gui_off()` inside script. Default option is gui off.
* `--title <name>`: to specify test title logged in log file. Just like use `title(name)` inside script.
* `--author <name>`: to specify author name logged in log file. Just like use `author(name)` inside script.
* `--version <ver>`: to specify product version logged in log file. Just like use `version(ver)` inside script.
* `--url <link>`: to specify url link logged in log file. Just like use `url(link)` inside script.

## 5  Exit Code
In your console, Python program with PySimpleTest module will exit with 5 kind of exit code:

* exit code `0`: All assertions passed.
* exit code `1`: Some assertions failed.
* exit code `2`: User killed with `Ctrl + C`.
* exit code `3`: Inner exception raised.
* exit code `5`: No assertion.

After running a test script, 

* On Windows, you can use `echo %errorlevel%` to check the exit code in command window;
* On Linux, you can use `echo $?` to check the exit code in terminal.

## 6  <label id="sec_External_Configuration">External Configuration</label>
A file with `.linfo` expand name is also generated. This file is same as `.info` file but with additional link information. So `linfo` is the abbreviation of "link info". The link information is just like `<file_name>:<line_number>`. It's used for double click then jump to script calling place. But this need external editor's support. This section will introduce how to implement double click jump in editor `Sublime Text`.

1. Firstly please install `Log Highlight` plugin in Sublime Text
2. Click Preferences->Package Settings->Log Highlight->Settings. Just like following figure
<div align="center">
<img src="https://s1.ax1x.com/2020/08/15/dkoTFf.png" width="500">
</div>

3. Copy following code in `Log Highlight.sublime-settings -- User` file then save:
<details>
	<summary>See Code</summary>

```json
{
    "context_menu": true,
    "auto_highlight" : true,
    "auto_highlight_output_panel": ["exec"],

    "log_list" :
    {
        "PySimpleTest_log_info" :
        {
            "type"         : "compile",
            "extension"    : [ "*.log", "*.info" ],
            "output.panel" : [ "" ],
            "use_link"     : true,
            "search_base":
            {
                "enable"        : true,
                "ignore_dir"    : [""],
                "max_scan_path" : 1000,
            },
            "bookmark" :
            {
                "enable"     : true,
                "goto_error" : false,
            },
            "severity" :
            {
                "fail" :
                {
                    "enable"  : true,
                    "pattern" : [[ "^\\s*Fail: ", "[\\r\\n]" ]],
                    "color" : {"base"  : ["#F92672", ""]}
                },
                "failed" :
                {
                    "enable"  : true,
                    "pattern" : [[ "^Failed: [1-9]", "[\\r\\n]" ]],
                    "color" : {"base"  : ["#F92672", ""]}
                },
                "failed0" :
                {
                    "enable"  : true,
                    "pattern" : [[ "^Failed: 0", "[\\r\\n]" ]],
                    "color" : {"base"  : ["#A6E22C", ""]}
                },
                "pass" :
                {
                    "enable"  : true,
                    "pattern" :
                    [
                        [ "^\\s*Pass: ", "[\\r\\n]" ],
                        [ "^\\s*Skip: ", "[\\r\\n]" ]
                    ],
                    "color" : {"base"  : ["#A6E22C", ""]}
                },
                "passed" :
                {
                    "enable"  : true,
                    "pattern" :[[ "^Passed: [1-9]", "[\\r\\n]" ]],
                    "color" : {"base"  : ["#A6E22C", ""]}
                },
                "passed0" :
                {
                    "enable"  : true,
                    "pattern" :[[ "^Passed: 0", "[\\r\\n]" ]],
                    "color" : {"base"  : ["#F92672", ""]}
                },
                "info" :
                {
                    "enable"  : true,
                    "pattern" :
                    [
                        [ "^\\S.*(?<!Pass|Fail|Summary|Total|Passed|Failed|Result): \\S", "[\\r\\n]" ],
                        [ "^\\s*([0-9])+(.([0-9])+)*  \\S", "[\\r\\n]" ],
                        [ "^\\s*Section ([0-9])+(.([0-9])+)*", "[\\r\\n]" ],
                        [ "^\\s*\\[ ", " \\]" ],
                    ],
                    "color" : {"base"  : ["#67D8EF", ""]}
                },
                "sum" :
                {
                    "enable"  : true,
                    "pattern" :[[ "^Total: [0-9]?", "[\\r\\n]" ]],
                    "color" : {"base"  : ["#67D8EF", ""]}
                },
                "result_pass":
                {
                    "enable"  : true,
                    "pattern" :[[ "^Result: Pass", "[\\r\\n]" ]],
                    "color" : {"base"  : ["#A6E22C", ""]}
                },
                "result_fail":
                {
                    "enable"  : true,
                    "pattern" :[[ "^Result: (Fail|Error)", "[\\r\\n]" ]],
                    "color" : {"base"  : ["#F92672", ""]}
                }
            },
            "theme":
            {
                "foreground"      : "#F8F8F2",
                "background"      : "#282923",
                "caret"           : "#F8F8F2",
                "selection"       : "#48473D",
                "selectionBorder" : "#181E26",
                "lineHighlight"   : "#3A392F"
            }
        },

        "PySimpleTest_linfo" :
        {
            "type"         : "compile",
            "extension"    : [ "*.linfo" ],
            "output.panel" : [ "" ],
            "use_link"     : true,
            "search_base":
            {
                "enable"        : true,
                "ignore_dir"    : [""],
                "max_scan_path" : 1000,
            },
            "bookmark" :
            {
                "enable"     : true,
                "goto_error" : false,
            },
            "severity" :
            {
                "link":
                {
                    "enable"  : true,
                    "pattern" :[[ "^{{{LINK}}}", " " ]],
                    "color" : {"base"  : ["#AC80FF", ""]}
                },
                "fail" :
                {
                    "enable"  : true,
                    "pattern" :[[ "\\|   *Fail: ", "[\\r\\n]" ]],
                    "color" : {"base"  : ["#F92672", ""]}
                },
                "failed" :
                {
                    "enable"  : true,
                    "pattern" :[[ "\\|  Failed: [1-9]", "[\\r\\n]" ]],
                    "color" : {"base"  : ["#F92672", ""]}
                },
                "failed0" :
                {
                    "enable"  : true,
                    "pattern" :[[ "\\|  Failed: 0", "[\\r\\n]" ]],
                    "color" : {"base"  : ["#A6E22C", ""]}
                },
                "pass" :
                {
                    "enable"  : true,
                    "pattern" :
                    [
                        [ "\\|   *Pass: ", "[\\r\\n]" ],
                        [ "\\|   *Skip: ", "[\\r\\n]" ]
                    ],
                    "color" : {"base"  : ["#A6E22C", ""]}
                },
                "passed" :
                {
                    "enable"  : true,
                    "pattern" :[[ "\\|  Passed: [1-9]", "[\\r\\n]" ]],
                    "color" : {"base"  : ["#A6E22C", ""]}
                },
                "passed0" :
                {
                    "enable"  : true,
                    "pattern" :[[ "\\|  Passed: 0", "[\\r\\n]" ]],
                    "color" : {"base"  : ["#F92672", ""]}
                },
                "info" :
                {
                    "enable"  : true,
                    "pattern" :
                    [
                        [ "\\|  \\S.*(?<!Pass|Fail|Summary|Total|Passed|Failed|Result): \\S", "[\\r\\n]" ],
                        [ "\\|   *Section ([0-9])+(.([0-9])+)*", "[\\r\\n]" ],
                        [ "\\|   *([0-9])+(.([0-9])+)*  \\S", "[\\r\\n]" ],
                        [ "\\|   *\\[ ", " \\]" ],
                    ],
                    "color" : {"base"  : ["#67D8EF", ""]}
                },
                "sum" :
                {
                    "enable"  : true,
                    "pattern" : [[ "\\|  Total: [0-9]?", "[\\r\\n]" ]],
                    "color" : {"base"  : ["#67D8EF", ""]}
                },
                "result_pass":
                {
                    "enable"  : true,
                    "pattern" : [[ "\\|  Result: Pass$", "[\\r\\n]" ]],
                    "color" : {"base"  : ["#A6E22C", ""]}
                },
                "result_fail":
                {
                    "enable"  : true,
                    "pattern" : [[ "\\|  Result: (Fail|Error)$", "[\\r\\n]" ]],
                    "color" : {"base"  : ["#F92672", ""]}
                }
            },
            "theme":
            {
                "foreground"      : "#F8F8F2",
                "background"      : "#282923",
                "caret"           : "#F8F8F2",
                "selection"       : "#48473D",
                "selectionBorder" : "#181E26",
                "lineHighlight"   : "#3A392F"
            }
        }
    }
}
```
</details>

4. `Ctrl+Shift+P` in Sublime, input `Log Highlight` in panel.
5. Click `Log Highlight: Generate Syntax & Theme`
6. Restart Sublime Text.
7. Open a `*.linfo` file with Sublime Text.
8. Double click a line, then it will jump to calling place. Just like following gif:
<div align="center">
<img src="https://ftp.bmp.ovh/imgs/2020/08/a5c36d6089ff4dcc.gif" width="700">
</div>
