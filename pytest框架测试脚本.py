import pytest
import requests
from datetime import datetime


class TencentVideoAPI:
    def __init__(self):
        self.base_url = "https://pbaccess.video.qq.com"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0(Windows NT 10.0;Win64;x64)",
            "Referer": "https://v.qq.com",
            "Accept": "application/json"
        })

    def get_movie_list(self, page=1, pagesize=30, sort=0, year=None, category=None):
        endpoint = "/trpc.tencentvideohotlistdata.hospitalist.DoSearchHotListHttp/getSearchHotListHttp"
        params = {
            "page": page,
            "pagesize": pagesize,
            "sort": sort,
            "table": 26
        }
        if year:
            params["year"] = year
        if category:
            params["type"] = category

        response = self.session.get(f"{self.base_url}{endpoint}", params=params)
        return response

    def search_movies(self, keyword, page=1, pagesize=20):
        endpoint = "/trpc.video search.mobile_search.MultiTerminalSearch/MbSearch"
        params = {
            "keyword": keyword,
            "page": page,
            "pagesize": pagesize
        }
        response = self.session.get(f"{self.base_url}{endpoint}", params=params)
        return response

    def get_movie(self, vid):
        endpoint = "/trpc.universal_backend_service.hot_word_info.HttpHotWordRecall/GetHotWords"
        params = {
            "vid": vid,
            "platform": 2,
            "defn": "hd"
        }

        response = self.session.get(f"{self.base_url}{endpoint}", params=params)
        return response

    @pytest.fixture
    def client(self):
        return TencentVideoAPI()

    class TestMovieList:
        def test_get_all_movies(self, client):
            response = client.get_movie_list()
            # 校验状态码
            assert response.status_code == 200, f"状态码错误: {response.status_code}"
            # 校验响应类型
            assert "application/json" in response.headers.get("Content-Type", ""), "非JSON响应"
            # 校验响应结构
            data = response.json()
            assert "code" in data, "响应中缺少code字段"
            assert data["code"] == 0, f"接口返回错误: {data.get('message', '未知错误')}"
            # 校验数据内容
            movie_list = data.get("data", {}).get("list", [])
            assert len(movie_list) > 0, "未获得到电影数据"
            # 校验单条电影数据结构
            if movie_list:
                first_movie = movie_list[0]
                assert "title" in first_movie, "电影数据缺少title字段"
                assert "playUrl" in first_movie, "电影缺少playUrl字段"

        def test_get_movie_by_year(self, client):
            year = "2025"
            response = client.get_movie_list(year=year)
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            movie_list = data.get("data", {}).get("list", [])
            if movie_list:
                for movie in movie_list:
                    if "subTitle" in movie:
                        assert year in movie["subTitle"], f"电影{movie['title']}不在 {year}年"

    # 测试搜索接口
    class TestSearchAPI:
        def test_search_by_keyword(self, api_client):
            """测试关键词搜索"""
            keyword = "封神"
            response = api_client.search_movies(keyword=keyword)

            assert response.status_code == 200
            assert "application/json" in response.headers.get("Content-Type", "")

            data = response.json()
            assert data["code"] == 0

            search_results = data.get("data", {}).get("video", [])
            assert len(search_results) > 0, f"搜索 {keyword} 未找到结果"

            # 验证搜索结果是否包含关键词
            for result in search_results:
                assert keyword in result.get("title", "") or keyword in result.get("subTitle", ""), \
                    f"搜索结果 {result['title']} 不包含关键词 {keyword}"

        def test_search_by_actor(self, api_client):
            """测试按演员搜索"""
            actor = "赵丽颖"
            response = api_client.search_movies(keyword=actor)

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0

            search_results = data.get("data", {}).get("video", [])
            assert len(search_results) > 0, f"未找到 {actor} 参演的电影"

            # 验证结果类型为电影
            for result in search_results:
                assert "电影" in result.get("type", ""), f"结果 {result['title']} 不是电影类型"

    # 测试电影详情接口
    class TestMovieDetail:
        def test_get_movie_detail(self, api_client):
            """测试获取电影详情"""
            # 使用已知有效的vid（需从腾讯视频页面获取）
            test_vid = "d004589876d"  # 示例vid，可能需要替换为实际有效ID
            response = api_client.get_movie_detail(vid=test_vid)

            assert response.status_code == 200
            assert "application/json" in response.headers.get("Content-Type", "")

            data = response.json()
            assert data["code"] == 0

            video_info = data.get("data", {}).get("videoInfo", {})
            assert video_info, "未获取到电影详情"

            # 验证详情字段
            assert "title" in video_info, "详情中缺少title字段"
            assert "playUrl" in video_info, "详情中缺少playUrl字段"
            assert "poster" in video_info, "详情中缺少poster字段"

    # 测试异常情况
    class TestErrorHandling:
        def test_invalid_api_endpoint(self, client):
            """测试无效API路径"""
            # 修改base_url为无效域名，触发ConnectionError
            client.base_url = "https://pbaccess.video.qq.com"
            with pytest.raises(requests.exceptions.ConnectionError):
                client.get_movie_list()

        def test_empty_keyword_search(self, api_client):
            """测试空关键词搜索"""
            response = api_client.search_movies(keyword="")

            assert response.status_code == 200
            data = response.json()

            # 验证空关键词返回空结果或错误提示
            if "data" in data and "video" in data["data"]:
                assert len(data["data"]["video"]) == 0, "空关键词搜索应返回空结果"
            else:
                assert data["code"] != 0, "空关键词搜索应返回错误"

    # 运行测试

    if __name__ == "__main__":
        # 移除__file__参数，让pytest自动发现测试
        pytest.main(["-v", "-s"])
        # 或者使用简化的参数
        # pytest.main(["-q"])
