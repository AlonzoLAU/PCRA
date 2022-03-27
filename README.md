# PCRA

**Program of Court Reservation of University of Chinese Academy of Sciences (PCRA)**  
**中国科学院大学运动场地预约程序**  

UCAS 体育场预约脚本， 仅供学习。

> 注：学校上线运动场地预约系统，同时场地过于丰富，仅出于练习编程技能原因开发此脚本，禁止滥用。
 
> 注：每年网站代码可能会变动，故脚本存在失效可能，请注意风险。推荐在预约前查看本仓库代码是否有更新，并通过登录等功能对代码进行测试。如果在预约过程中发现场地的time_id、sub_id或预约网站的API有更新，欢迎发起PR或issue，非常感谢。

## 安装

### 环境依赖

Python 3.x

### Mac

```bash
brew install python3
sudo easy_install pip
sudo pip install requests
```

### Linux

```bash
sudo apt install python3-pip
sudo pip install requests
```

### Windows

根据[官网](https://www.python.org/downloads/) 安装Python并安装requests

```bash
python -m pip install requests
```

## 初始化

在当前目录下创建 `auth` 文件并填入登录信息，格式如下：

```
username@mails.ucas.ac.cn
password
```

第一行填写`sep用户名`，第二行填写`sep密码`

在当前目录下创建 `choice` 文件并填入课程，格式如下：

```
0
2022-03-26 10 1
2022-03-26 10 2
```

第一行填写`0`或`1`（0代表预约篮球场地，1代表预约羽毛球场地）  
接下来每一行表示一个预约条目 <日期，24小时制整点时间，场地编号（篮球：1-2， 羽毛球：1-8）>



`config.py`文件中共有三个配置，单次请求等待时间，轮询最短时间和轮询最长时间，可根据需求修改

## 运行程序

运行`python reverse.py -h`显示程序选项说明

## 校外运行

非校园网环境登录需要验证码，须长期轮询是否有人退订时，可使用 ``python reverse.py -c`` 命令运行， 此时会在目录下生成`captcha.jpg`文件，根据该图片的内容输入验证码即可登录。

## 定时任务

若希望程序静默至预定时间开启POST轮询，可使用`python reverse.py -t 12 30`命令运行，此时会在设定的当日时分秒开启轮询。

> 注：该选项参数为时分两项组成，缺一不可。

## 邮件提醒

需要邮件提醒时，在当前目录下创建 `mailConfig` 文件并填入登录信息，格式如下：

```
from_username@ict.ac.cn
password
mail.cstnet.cn
to_username@ict.ac.cn
```

第一行填写发件邮箱地址，第二行填写发件邮箱密码，第三行填写SMTP服务器地址，第四行填写接收通知邮箱地址。

创建完成后，带 `-m` 参数运行即可在预约结束后邮箱通知。

注：

1. 网易系邮箱第三方不能使用密码登录，需单独设置授权码。
2. 学校邮箱服务器为 `mail.cstnet.cn`

## 更新概要

- `2022-03-23` 参考 [前人工作](https://github.com/LyleMi/ucas) 完成本脚本，鸣谢[Lyle](https://github.com/LyleMi)
