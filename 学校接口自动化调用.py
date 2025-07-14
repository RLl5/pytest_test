import requests
import time
from datetime import datetime


def _validate_response(response, expected_status, response_time_threshold, actual_time, check_json=False):
    """通用响应验证方法"""
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
            assert False, "响应不是有效的JSON格式"


class SchoolAPITester:
    def __init__(self, base_url, auth_token=None):
        """初始化测试器，设置基础URL和认证信息"""
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'SchoolAPI Tester/1.0'
        })

        # 如果提供了认证token，则添加到请求头
        if auth_token:
            self.session.headers.update({'Authorization': f'Bearer {auth_token}'})

    def get_course_list(self, semester=None, course_type=None):
        """获取课程列表接口测试"""
        endpoint = "/api/courses"
        params = {}

        # 添加可选查询参数
        if semester:
            params["semester"] = semester
        if course_type:
            params["type"] = course_type

        start_time = time.time()
        response = self.session.get(f"{self.base_url}{endpoint}", params=params)
        elapsed_time = (time.time() - start_time) * 1000  # 转换为毫秒

        # 验证响应
        _validate_response(
            response,
            expected_status=200,
            response_time_threshold=500,
            actual_time=elapsed_time,
            check_json=True
        )

        return response.json()

    def search_grades(self, student_id, course_id=None, semester=None):
        """搜索成绩接口测试"""
        endpoint = "/api/grades/search"
        data = {"studentId": student_id}

        # 添加可选查询参数
        if course_id:
            data["courseId"] = course_id
        if semester:
            data["semester"] = semester

        start_time = time.time()
        response = self.session.post(
            f"{self.base_url}{endpoint}",
            json=data
        )
        elapsed_time = (time.time() - start_time) * 1000  # 转换为毫秒

        # 验证响应
        _validate_response(
            response,
            expected_status=200,
            response_time_threshold=800,  # 成绩查询可能更耗时
            actual_time=elapsed_time,
            check_json=True
        )

        return response.json()

    def run_tests(self):
        """运行完整测试套件"""
        print(f"开始测试学校API - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)

        try:
            # 测试获取课程列表
            print("测试获取全部课程列表...")
            courses = self.get_course_list()
            print(f"成功获取 {len(courses)} 门课程")

            print("\n测试获取指定学期课程...")
            spring_courses = self.get_course_list(semester="2023-2024春季")
            print(f"成功获取 {len(spring_courses)} 门春季课程")

            # 测试搜索成绩
            print("\n测试搜索学生成绩...")
            student_id = "112303100104"  # 示例学生ID
            grades = self.search_grades(student_id)
            print(f"成功获取学生 {student_id} 的 {len(grades)} 门课程成绩")

            print("\n测试带课程筛选的成绩搜索...")
            math_grades = self.search_grades(student_id, course_id="MATH101")
            print(f"成功获取学生 {student_id} 的 {len(math_grades)} 门数学课程成绩")

            print("\n所有测试通过!")

        except AssertionError as e:
            print(f"\n测试失败: {str(e)}")
        except Exception as e:
            print(f"\n发生意外错误: {str(e)}")
        finally:
            print("=" * 50)
            print(f"测试完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "黄思麒":
    # 设置API基础URL
    BASE_URL = "https://i.hyit.edu.cn"  # 替换为实际API地址

    # 初始化测试器（如果需要认证，提供token）
    tester = SchoolAPITester(BASE_URL, auth_token="your_access_token")

    # 运行测试
    tester.run_tests()