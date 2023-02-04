# MR插件 日语学习工具
## 使用方法
1. 将代码以压缩包的形式下载下来
2. 将压缩包解压
3. 将文件夹重命名为jav_bot
4. 将文件夹拷贝到MR插件目录
5. 重启MR容器
6. 进入插件页面进行配置
## 配置相关
代理: 基本上是需要的
下载器: 支持MR支持的下载器,可通过设置MR中定义的下载器名称，来指定下载器
保存路径: 下载器手动模式下必填
分类：下载器自动模式下必填，请提前在下载中设置好分类
整理刮削：如果需要开启整理刮削,需安装mdc插件，插件地址：https://github.com/mdc-ng/mdc_mbot_plugin, 并将插件文件夹名称重命名mdc_mbot_plugin，放入插件目录
刮削成功目录: 整理模式仅支持硬链,此目录为硬链目录，也为整理的目标目录，也为你媒体服务器设置的目录(请注意docker容器与主机的映射)
刮削失败目录：此处存放刮削失败影片的日志目录
Cookie，UA: 能设置尽量设置，避免CF，无法获取信息
推送用户：
头图URL: 需图床,本人使用了alist
##关于删除演员，番号
对演员，番号进行删除的时候，会发现删除成功之后，选项仍然存在。目前只有重启容器，选项才会更新，还没找到解决办法
##关于订阅
共有1、2、3三个参数,支持一下三种情况：
1、2、3都传则订阅番号+演员
1传2、3不传则订阅番号
1不穿2、3传则订阅演员
## 关于自动更新与指令中的手动更新
上述更新，仅下载最新的代码文件到本地进行覆盖。重启容器之后，更新才会生效
## 关于刮削
本插件仅为调用方，不发表任何意见，有问题请咨询MDC开发者
