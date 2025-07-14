# 这是一个示例 Python 脚本。
import requests

# 发送一个get请求并得到响应
r = requests.get('https://www.baidu.com')
# 查看响应对象的类型
print(type(r))
# 查看响应状态码
print(r.status_code)
# 查看响应内容的类型
print(type(r.text))
# 查看响应的内容
print(r.text)
# 查看cookies
print(r.cookies)



