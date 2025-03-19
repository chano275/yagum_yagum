from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 라우터 임포트
from router.user.user_router import router as user_router
from router.account.account_router import router as account_router
from router.team.team_router import router as team_router
from router.player.player_router import router as player_router
from router.mission.mission_router import router as mission_router
from router.saving_rule.saving_rule_router import router as saving_rule_router
from router.report.report_router import router as report_router
from router.game.game_router import router as game_router

# 데이터베이스 초기화
from database import engine
import models
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="야금야금 서비스 API",
    description="야구 기반 적금 서비스를 위한 백엔드 API",
    version="1.0.0"
)

# CORS 설정
origins = [
    "http://localhost",
    "http://localhost:3000",  # 프론트엔드 주소
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(user_router, prefix="/api/user", tags=["사용자"])
app.include_router(account_router, prefix="/api/account", tags=["계정"])
app.include_router(team_router, prefix="/api/team", tags=["팀"])
app.include_router(player_router, prefix="/api/player", tags=["선수"])
app.include_router(mission_router, prefix="/api/mission", tags=["우대금리"])
app.include_router(saving_rule_router, prefix="/api/saving_rule", tags=["적금 규칙"])
app.include_router(report_router, prefix="/api/report", tags=["보고서"])
app.include_router(game_router, prefix="/api/game", tags=["경기"])

@app.get("/")
async def root():
    return {"message": "야금야금 서비스 API에 오신 것을 환영합니다"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)