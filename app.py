import requests
from flask import Flask, jsonify, request
import os

app = Flask(__name__)

# ----------------------------------------------------
# URL API ỔN ĐỊNH ĐƯỢC XÁC NHẬN (KHÔNG CẦN TOKEN)
URL_API_GOC_KHONG_TOKEN = "https://taixiu1.gsum01.com/api/luckydice1/GetSoiCau" 

# CÁC GIẢ ĐỊNH VỀ KHÓA JSON (Cần chỉnh sửa nếu có lỗi 500 sau khi triển khai)
TEN_KHOA_DATA_LEVEL_1 = "" # Giả định: Dữ liệu là một list ở cấp độ ngoài cùng.
TEN_KHOA_PHIEN = "ID"      # Giả định: Khóa chứa số phiên
TEN_KHOA_XUC_XAC = "Result"  # Giả định: Khóa chứa list kết quả [x1, x2, x3]
# ----------------------------------------------------

@app.route('/api/ketqua', methods=['GET'])
def get_results_real():
    
    # 1. Gọi API Gốc ổn định
    full_url = URL_API_GOC_KHONG_TOKEN 
    
    try:
        response = requests.get(full_url, timeout=10)
        response.raise_for_status() 
        data_goc = response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Không thể kết nối hoặc API gốc đã lỗi/bị chặn.", "details": str(e)}), 503
    
    # 2. Xử lý dữ liệu dựa trên giả định (Lấy phiên gần nhất - thường là phần tử đầu tiên)
    try:
        # Xử lý khóa bao ngoài
        if isinstance(data_goc, list) and data_goc:
            latest_session_data = data_goc[0]
        elif TEN_KHOA_DATA_LEVEL_1 and isinstance(data_goc.get(TEN_KHOA_DATA_LEVEL_1), list):
            latest_session_data = data_goc[TEN_KHOA_DATA_LEVEL_1][0]
        else:
            return jsonify({"error": "Cấu trúc JSON không phù hợp. Có thể khóa bao ngoài không đúng.", "raw_data": data_goc}), 500

        phien = latest_session_data.get(TEN_KHOA_PHIEN, "Không tìm thấy")
        ket_qua_xuc_xac = latest_session_data.get(TEN_KHOA_XUC_XAC)

        if not isinstance(ket_qua_xuc_xac, list) or len(ket_qua_xuc_xac) < 3:
            return jsonify({"error": "Kết quả xúc xắc không phải là list 3 phần tử.", "raw_data": latest_session_data}), 500

        x1, x2, x3 = ket_qua_xuc_xac[0], ket_qua_xuc_xac[1], ket_qua_xuc_xac[2]
        tong_diem = x1 + x2 + x3
        
        tai_xiu = "Tài" if tong_diem >= 11 else "Xỉu"

        # 3. Trả về cấu trúc API của bạn
        data_tra_ve = {
            "phien": phien,
            "tong_diem": tong_diem,
            "ket_qua_tai_xiu": tai_xiu,
            "xuc_xac1": x1,
            "xuc_xac2": x2,
            "xuc_xac3": x3,
            "trang_thai": "KET_QUA_THAT (API ON DINH)"
        }
        
        return jsonify(data_tra_ve)
        
    except (TypeError, IndexError, KeyError) as e:
        return jsonify({"error": "Lỗi xử lý JSON (Khóa không đúng).", "details": str(e), "data_goc": data_goc}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
