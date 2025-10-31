import json
import asyncio
from flask import Flask, jsonify
import websockets
import os
from urllib.parse import urlunparse, urlencode # THƯ VIỆN MỚI

app = Flask(__name__)

# URL WebSocket CỦA BẠN (Đã sửa lỗi InvalidURI bằng urllib.parse)
# LỖI: Sử dụng urlunparse/urlencode là cách đảm bảo URI hợp lệ 100%
BASE_SCHEME = "wss"
BASE_NETLOC = "pmcn.site"
BASE_PATH = "/game_sunwin/ws"
# Tham số truy vấn đã được tách riêng
QUERY_PARAMS = {
    "id": "Cskhtool11",
    "key": "NhiCuTo"
}

# Sử dụng urlunparse để xây dựng URL hợp lệ 100%
SUNWIN_WS_URL = urlunparse(
    (BASE_SCHEME, BASE_NETLOC, BASE_PATH, None, urlencode(QUERY_PARAMS), None)
)

@app.route('/get_tx_data', methods=['GET'])
def get_tx_data():
    data = asyncio.run(get_websocket_data()) 
    
    if data and data.get('success'):
        return jsonify(data)
    else:
        return jsonify({
            "error": "Không thể kết nối hoặc nhận dữ liệu từ WebSocket. Vui lòng kiểm tra Log Render.", 
            "raw_error": data.get('raw_error', 'Lỗi không xác định')
        }), 503

async def get_websocket_data():
    try:
        # Thiết lập timeout 10 giây
        async with websockets.connect(SUNWIN_WS_URL, timeout=10) as websocket: 
            # ... (Phần logic kết nối và trích xuất JSON giữ nguyên)
            response = await websocket.recv()
            data = json.loads(response)
            
            # Khóa JSON chính xác
            session_id = data.get('phien') 
            dice_results = [data.get('xuc_xac_1'), data.get('xuc_xac_2'), data.get('xuc_xac_3')]
            total = data.get('tong')
            ket_qua = data.get('ket_qua')

            return {
                "success": True,
                "current_session": session_id,
                "dice_results": dice_results,
                "total": total,
                "ket_qua": ket_qua,
                "raw_data": data
            }

    except Exception as e:
        error_message = f"LỖI WEBSOCKET/ASYNC: {e}"
        print(error_message)
        return {"success": False, "raw_error": str(e)}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
