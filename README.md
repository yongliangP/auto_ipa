# auto_ipa
iOS 自动打包工具 支持project、workspace

运用 xcodebuild 方式

修改文件中的 xx 替换成你自己的信息

将脚本下载下来，放入工程根目录

配置好打包需要的环境后 ，打开命令行工具 `cd 工程文件夹` 进入根目录 
然后输入  
```
#project 方式
./auto_ipa.py -p youproject.xcodeproj -s youproject -o ~/Desktop/youproject.ipa
#workspace 方式
./auto_ipa.py -w youproject.xcworkspace -s youproject -o ~/Desktop/youproject.ipa
```
或者直接修改源文件供自己直接使用

具体说明[iOS 关于自动打包那些事](http://www.jianshu.com/p/9629b4049766)
