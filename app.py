import json
import asyncio
from flask import Flask, jsonify
import websockets
import os

app = Flask(__name__)

# URL WebSocket CỦA BẠN (Đã xác định)
# LƯU Ý: Đây là URL tĩnh, nếu Sunwin thay đổi tên miền, bạn cần cập nhật.
SUNWIN_WS_URL = "wss://pmcn.site/game_sunwin/ws?id=Cskhtool11&key=NhiCuTo"

@app.route('/get_tx_data', methods=['GET'])
def get_tx_data():
    """
    Điểm truy cập API HTTP: Chạy hàm async để kết nối WebSocket.
    """
    data = asyncio.run(get_websocket_data()) 
    
    if data and data.get('success'):
        return jsonify(data)
    else:
        return jsonify({"error": "Không thể kết nối hoặc nhận dữ liệu từ WebSocket.", "raw_error": data.get('raw_error')}), 503

async def get_websocket_data():
    """
    Kết nối tới WebSocket, nhận dữ liệu và xử lý bằng khóa JSON chính xác.
    """
    try:
        # Thiết lập timeout 10 giây
        async with websockets.connect(SUNWIN_WS_URL, timeout=10) as websocket: 
            
            # Đợi nhận dữ liệu phản hồi đầu tiên
            response = await websocket.recv()
            
            # Chuyển chuỗi JSON nhận được thành đối tượng Python
            data = json.loads(response)
            
            # -------------------------------------------------------------
            # DÙNG KHÓA JSON CHÍNH XÁC: 'phien', 'xuc_xac_1', 'xuc_xac_2', 'xuc_xac_3'
            # -------------------------------------------------------------
            
            session_id = data.get('phien') 
            dice_results = [
                data.get('xuc_xac_1'),
                data.get('xuc_xac_2'),
                data.get('xuc_xac_3')
            ]
            total = data.get('tong')
            ket_qua = data.get('ket_qua')

            return {
                "success": True,
                "current_session": session_id,
                "dice_results": dice_results,
                "total": total,
                "ket_qua": ket_qua,
                "raw_data": data # Trả về dữ liệu thô để kiểm tra
            }

    except Exception as e:
        # Ghi log lỗi ra console Render
        error_message = f"LỖI WEBSOCKET/ASYNC: {e}"
        print(error_message)
        return {"success": False, "raw_error": str(e)}

if __name__ == '__main__':
    # Render sẽ cung cấp biến môi trường PORT
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
