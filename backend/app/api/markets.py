from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import pandas as pd

from ..data.stock_handler import StockDataHandler

router = APIRouter(prefix="/markets", tags=["市场与数据"])


@router.get("/supported")
def get_supported_markets():
    return ["A股", "加密货币(预留)"]


@router.get("/stocks")
def list_stocks():
    handler = StockDataHandler()
    symbols = handler.list_symbols()
    return [{"symbol": s, "name": s} for s in symbols]


@router.post("/import_csv")
async def import_csv(symbol: str, file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    content = await file.read()
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        df = pd.read_csv(tmp_path)
        handler = StockDataHandler()
        csv_path = handler.save_csv(symbol, df)
        return {"message": f"Data imported for {symbol}", "path": csv_path}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        os.unlink(tmp_path)
