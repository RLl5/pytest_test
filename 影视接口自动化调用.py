import requests
import time
from datetime import datetime

"""def _validate_response(response, expected_status, response_time_threshold, actual_time, check_json=False):
    # 验证状态码
    assert response.status_code == expected_status, \
        f"请求失败，预期状态码: {expected_status}，实际状态码: {response.status_code}"

    # 验证响应时间
    assert actual_time < response_time_threshold, \
        f"响应时间过长，预期: < {response_time_threshold}ms，实际: {actual_time:.2f}ms"

    # 验证JSON格式
    if check_json:
        try:
            response.json()
        except ValueError:
            assert False, "响应不是有效的JSON格式
            """


#def _validate_response(self, response, expected_status, response_time_threshold, actual_time, check_json=False):
 #   print(f"\n请求URL: {response.request.url}")
  #  print(f"响应状态码: {response.status_code}")
   # print(f"响应内容类型: {response.headers.get('Content-Type')}")
    #print(f"响应内容长度: {len(response.text)}")

    #response.encoding = 'utf-8'
    # 打印前500个字符（避免大型响应占用过多输出）
    #print(f" 响应内容前500个字符: \n{response.text[:500]}")

    #assert response.status_code == expected_status, \
     #   f"请求失败，预期状态码: {expected_status}，实际状态码: {response.status_code}"

    #assert actual_time < response_time_threshold, \
     #   f"响应时间过长，预期: < {response_time_threshold}ms，实际: {actual_time:.2f}ms"

  #  if check_json:
   #     try:
    #        response.json()
     #   except ValueError as e:
      #      # 保存响应内容到文件，便于后续分析
          #  with open("response_content.txt", "w", encoding="utf-8") as f:
         #       f.write(response.text)
        #    assert False, f"响应不是有效的JSON格式: {str(e)}"


class MovieAplTester:
    @staticmethod
    def _validate_response(response, expected_status, response_time_threshold, actual_time, check_json=False):
        print(f"\n请求URL: {response.request.url}")
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容类型: {response.headers.get('Content-Type')}")
        print(f"响应内容长度: {len(response.text)}")

        response.encoding = 'utf-8'
        # 打印前500个字符（避免大型响应占用过多输出）
        print(f" 响应内容前500个字符: \n{response.text[:500]}")

        assert response.status_code == expected_status, \
            f"请求失败，预期状态码: {expected_status}，实际状态码: {response.status_code}"

        assert actual_time < response_time_threshold, \
            f"响应时间过长，预期: < {response_time_threshold}ms，实际: {actual_time:.2f}ms"

        if check_json:
            try:
                response.json()
            except ValueError as e:
                # 保存响应内容到文件，便于后续分析
                with open("response_content.txt", "w", encoding="utf-8") as f:
                    f.write(response.text)
                assert False, f"响应不是有效的JSON格式: {str(e)}"

    def __init__(self, base_url="https://pbaccess.video.qq.com", auth_token=None):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'MovieAPI Tester/1.0' ,
            'Referer': 'https://v.qq.com/'
        })
        # 如果提供了认证token，则添加到请求头
        if auth_token:
            self.session.headers.update({'Authorization': f'Bearer {auth_token}'})

    def movielist(self, year=None, movie_type=None):
        endpoint = "/collect/whitelist"
        params = {
            "page": 1,
            "pagesize": 30,
            "sort": 0,  # 0=推荐，1=最新，2=最热
            "tabId": 14  # 14=电影
        }
        if year:
            params["year"] = year
        if movie_type:
            params["movie_type"] = movie_type

        start_time = time.time()
        response = self.session.get(f"{self.base_url}{endpoint}", params=params)
        elapsed_time = (time.time() - start_time) * 1000
        if response.status_code == 404:
            # 若返回404，可能是没有符合条件的电影，返回空列表
            print("警告: 未找到符合条件的电影，返回空列表")
            return []
        # 验证响应
        self._validate_response(
            response,
            expected_status=200,
            response_time_threshold=700,
            actual_time=elapsed_time,
            check_json=True
        )

        return response.json()

    def search_movie(self, name, actor=None, year=None,page=1):
        endpoint = "/trpc.video search.mobile_search.MultiTerminalSearch/MbSearch"
        params = {
            "keyword": name,
            "page": page,
            "pagesize": 20
        }
        data = {"name": name}
        if actor:
            data["autor"] = actor
        if year:
            data["year"] = year
        start_time = time.time()
        response = self.session.post(
            f"{self.base_url}{endpoint}",
            json=data
        )

        elapsed_time = (time.time() - start_time) * 1000  # 转换为毫秒

        self._validate_response(
            response,
            expected_status=200,
            response_time_threshold=800,
            actual_time=elapsed_time,
            check_json=True
        )

        return response.json()

    def run_tests(self):
        """运行完整测试套件"""
        print(f"开始测试影视API - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)

        try:
            # 测试获取电影列表
            print("测试获取全部电影列表...")
            movies = self.movielist()
            print(f"成功获取 {len(movies)} 部电影")

            # 特殊处理：如果返回空列表，可能是测试环境无数据
            if not movies:
                print("警告: 获取到0部电影，可能测试环境无数据")
            else:
                print(f"成功获取 {len(movies)} 部电影")
            print("\n测试获取指定年电影...")
            spring_movie = self.movielist(year="2025")
            print(f"成功获取 {len(spring_movie)} 部电影")

            # 测试搜索电影
            print("\n测试搜索演员的电影...")
            actor = "赵丽颖"  # 示例演员
            name = self.search_movie(actor)
            print(f"成功获取 {actor} 的 {name} 电影")

            print("\n测试搜索特定电影...")
            movie_name = "第二十一条"
            movie_details = self.search_movie(name=movie_name)  # 修正调用方式
            print(f"成功获取电影: {movie_name} 的详情")

            print("\n所有测试通过!")

        except AssertionError as e:
            print(f"\n测试失败: {str(e)}")
        except Exception as e:
            print(f"\n发生意外错误: {str(e)}")
        finally:
            print("=" * 50)
            print(f"测试完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    # 设置API基础URL（使用实际API域名）
    BASE_URL = "https://pbaccess.video.qq.com"  # 腾讯视频实际API域名

    # 初始化测试器（修正类名）
    tester = MovieAplTester(BASE_URL)  # 类名应为 MovieApiTester，无需auth_token

    # 运行测试
    tester.run_tests()
