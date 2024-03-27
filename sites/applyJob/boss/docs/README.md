## 基本

- 克隆项目：`git clone https://github.com/NC-Cj/BigPlayer.git `
- 安装必要包：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r r .\requirements.txt`
- 使用`playwright install`安装开发浏览器
- 设置谷歌浏览器属性
  1. 找到谷歌浏览器图标右键点击属性
  2. 在`快捷方式栏/目标`中，在后面添加`--remote-debugging-port=9999`，全部内容应该是 `"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9999`，最后点击应用保存

## Pages下站点爬虫启动

1. 双击浏览器，打开boss站点登录
2. 在当前浏览器新建窗口，关闭已打开的boss网页（此时浏览器已经有了boss用户登录缓存）
3. 找到站点目录，运行`main.py`文件
4. 个性化定制您的招聘助手