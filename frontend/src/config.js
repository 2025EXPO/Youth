// 환경에 따라 자동 설정되게 해도 가능하지만, 일단 수동으로 기본값 지정
current_ip = "56.155.45.183";
const BASE_URL = `http://${current_ip}:5000`; // ✅ 이 한 줄만 바꾸면 전역 반영됨

export default BASE_URL;
