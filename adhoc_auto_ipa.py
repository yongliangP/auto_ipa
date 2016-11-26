#!/usr/bin/env python
# -*- coding:utf-8 -*-

#./adhoc_auto_ipa.py -p youproject.xcodeproj -s youproject -o ~/Desktop/youproject.ipa

#./adhoc_auto_ipa.py -w youproject.xcworkspace -s youproject -o ~/Desktop/youproject.ipa

from optparse import OptionParser
import subprocess
import requests
import hashlib
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
#configuration for iOS build setting
CODE_SIGN_IDENTITY = "iPhone Distribution: xxxxx(xxxxxx)"
ADHOC_PROVISIONING_PROFILE = "xxxx-xxxxx-xxxx-xxxx-xxxxx"
APPSTORE_PROVISIONING_PROFILE = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
ADHOCPath = "AdHocExportOptions.plist"
CONFIGURATION = "Release"
SDK = "iphoneos"

# configuration for pgyer
PGYER_UPLOAD_URL = "http://www.pgyer.com/apiv1/app/upload"
DOWNLOAD_BASE_URL = "http://www.pgyer.com"
USER_KEY = "xxx"
API_KEY = "xxx"

# configuration for email
from_gmail_addr = "xx@xx.com"
from_163_addr = "xx@163.com"
password = "xxxxxxx"
smtp_gmail_server = "smtp.gmail.com"
smtp_163_server = "smtp.163.com"
to_addr = 'xx@xx.com'
pgyer_addr = "http://www.pgyer.com/xx"


def cleanBuildDir(buildDir):
	cleanCmd = "rm -r %s" %(buildDir)
	process = subprocess.Popen(cleanCmd, shell = True)
	process.wait()
	print "cleaned buildDir: %s" %(buildDir)


def parserUploadResult(jsonResult):
	resultCode = jsonResult['code']
	if resultCode == 0:
		downUrl = DOWNLOAD_BASE_URL +"/"+jsonResult['data']['appShortcutUrl']
		print "Upload Success"
		print "DownUrl is:" + downUrl
	else:
		print "Upload Fail!"
		print "Reason:"+jsonResult['message']

def uploadIpaToPgyer(ipaPath):
    print "ipaPath:"+ipaPath
    files = {'file': open(ipaPath, 'rb')}
    headers = {'enctype':'multipart/form-data'}
    payload = {'uKey':USER_KEY,'_api_key':API_KEY,'publishRange':'2','isPublishToPublic':'2'}
    print "uploading...."
    r = requests.post(PGYER_UPLOAD_URL, data = payload ,files=files,headers=headers)
    if r.status_code == requests.codes.ok:
         result = r.json()
         parserUploadResult(result)
    else:
        print 'HTTPError,Code:'+r.status_code

def buildProject(project, scheme, output):
  
    process = subprocess.Popen("pwd", stdout=subprocess.PIPE)
    (stdoutdata, stderrdata) = process.communicate()
    buildDir = stdoutdata.strip() + '/build'
    print "buildDir: " + buildDir
    buildCmd = 'xcodebuild archive -project %s -scheme %s -configuration %s -sdk %s CODE_SIGN_IDENTITY="%s" PROVISIONING_PROFILE="%s" -archivePath %s/%s.xcarchive' %(project,scheme,CONFIGURATION,SDK,ADHOC_CODE_SIGN_IDENTITY,ADHOC_PROVISIONING_PROFILE,buildDir,scheme)
    print "buildCmd: " + buildCmd
    process = subprocess.Popen(buildCmd, shell = True)
    process.wait()
    
    ipaCmd = 'xcodebuild -exportArchive -archivePath %s/%s.xcarchive -exportPath %s -exportOptionsPlist %s' %(buildDir,scheme,output,ADHOCPath)
    process = subprocess.Popen(ipaCmd, shell=True)
    (stdoutdata, stderrdata) = process.communicate()

    uploadIpaToPgyer(output)
    cleanBuildDir(buildDir)

def buildWorkspace(workspace, scheme, output):
    process = subprocess.Popen("pwd", stdout=subprocess.PIPE)
    (stdoutdata, stderrdata) = process.communicate()
    buildDir = stdoutdata.strip() + '/build'
    print "buildDir: " + buildDir
    buildCmd = 'xcodebuild archive -workspace %s -scheme %s -configuration %s -sdk %s CODE_SIGN_IDENTITY="%s" PROVISIONING_PROFILE="%s" -archivePath %s/%s.xcarchive' %(workspace,scheme,CONFIGURATION,SDK,ADHOC_CODE_SIGN_IDENTITY,ADHOC_PROVISIONING_PROFILE,buildDir,scheme)
    process = subprocess.Popen(buildCmd, shell = True)
    process.wait()
        
    ipaCmd = 'xcodebuild -exportArchive -archivePath %s/%s.xcarchive -exportPath %s -exportOptionsPlist %s' %(buildDir,scheme,output,ADHOCPath)
    process = subprocess.Popen(ipaCmd, shell=True)
    (stdoutdata, stderrdata) = process.communicate()
        
    uploadIpaToPgyer(output)
    cleanBuildDir(buildDir)

def xcbuild(options):
	project = options.project
	workspace = options.workspace
	scheme = options.scheme
	output = options.output

	if project is None and workspace is None:
		pass
	elif project is not None:
		buildProject(project, scheme, output)
	elif workspace is not None:
		buildWorkspace(workspace, scheme, output)


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

# 发邮件
def send_mail():

    msg = MIMEText('xx iOS测试项目已经打包完毕，请前往 http://www.pgyer.com/xx 下载测试！', 'plain', 'utf-8')
    msg['From'] = _format_addr('iOS自动打包系统 <%s>' % from_163_addr)
    msg['To'] = _format_addr('xx 测试人员 <%s>' % to_addr)
    msg['Subject'] = Header('xxx 客户端打包程序', 'utf-8').encode()
    server = smtplib.SMTP_SSL(smtp_163_server, 465)
    server.connect(smtp_163_server, 465)
    server.set_debuglevel(1)
    server.starttls()
    server.ehlo()
    server.login(from_163_addr, password)
    print "开始发送邮件。。。"
    server.sendmail(from_163_addr, [to_addr], msg.as_string())
    server.quit()
    print "发送邮件完成。。。"
    
def main():
    parser = OptionParser()
    parser.add_option("-w", "--workspace", help="Build the workspace name.xcworkspace.", metavar="name.xcworkspace")
    parser.add_option("-p", "--project", help="Build the project name.xcodeproj.", metavar="name.xcodeproj")
    parser.add_option("-s", "--scheme", help="Build the scheme specified by schemename. Required if building a workspace.", metavar="schemename")
    parser.add_option("-t", "--target", help="Build the target specified by targetname. Required if building a project.", metavar="targetname")
    parser.add_option("-o", "--output", help="specify output filename", metavar="output_filename")
    (options, args) = parser.parse_args()

    print "options: %s, args: %s" % (options, args)
# 编译文件打包上传到蒲公英
    xcbuild(options)
# 发送邮件给测试人员
    send_mail()



if __name__ == '__main__':
	main()
